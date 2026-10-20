from pathlib import Path
from datetime import date
import math
import argparse
import heapq
import itertools
import json

import pcbnew as pcb


OUTPUT = Path(__file__).resolve().parents[1] / 'ergogen-kikad/generated'
BOARD = OUTPUT / 'pcbs/macropad.kicad_pcb'
BASE_PLATE = OUTPUT / 'pcbs/baseplate.kicad_pcb'
WIDTH_MM = 0.30
GRID_MM = 0.25
CLEARANCE_MM = 0.25
PAGE_OFFSET_MM = (0, 0)
DRAWING_TITLE = 'QBF Wireless Split Perkins Keyboard'
RING_INNER_RADIUS_MM = 23.0


def point(xy):
    return pcb.VECTOR2I(pcb.FromMM(xy[0]), pcb.FromMM(xy[1]))


def mm_point(vector):
    return (round(pcb.ToMM(vector.x), 4), round(pcb.ToMM(vector.y), 4))


def point_to_segment_distance(position, start, end):
    delta = (end[0] - start[0], end[1] - start[1])
    length_squared = delta[0] ** 2 + delta[1] ** 2
    fraction = max(0, min(1, ((position[0] - start[0]) * delta[0]
                               + (position[1] - start[1]) * delta[1])
                           / length_squared))
    closest = (start[0] + fraction * delta[0], start[1] + fraction * delta[1])
    return math.dist(position, closest)


def segment_distance(start1, end1, start2, end2):
    d1 = (end1[0] - start1[0], end1[1] - start1[1])
    d2 = (end2[0] - start2[0], end2[1] - start2[1])
    offset = (start1[0] - start2[0], start1[1] - start2[1])
    determinant = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(determinant) > 1e-12:
        t = (d2[0] * offset[1] - d2[1] * offset[0]) / determinant
        u = (d1[0] * offset[1] - d1[1] * offset[0]) / determinant
        if 0 <= t <= 1 and 0 <= u <= 1:
            return 0
    return min(point_to_segment_distance(start1, start2, end2),
               point_to_segment_distance(end1, start2, end2),
               point_to_segment_distance(start2, start1, end1),
               point_to_segment_distance(end2, start1, end1))


def pad_distance(pad, start, end):
    center = mm_point(pad.GetPosition())
    if pad.GetAttribute() == pcb.PAD_ATTRIB_NPTH:
        size = pad.GetDrillSize()
    else:
        size = pad.GetSize()
    if pad.GetShape() == pcb.PAD_SHAPE_CIRCLE:
        return point_to_segment_distance(center, start, end) - pcb.ToMM(size.x) / 2
    angle = math.radians(pad.GetOrientationDegrees())
    cosine, sine = math.cos(angle), math.sin(angle)
    half_x, half_y = pcb.ToMM(size.x) / 2, pcb.ToMM(size.y) / 2
    def local(position):
        x, y = position[0] - center[0], position[1] - center[1]
        return (x * cosine - y * sine, x * sine + y * cosine)
    first, last = local(start), local(end)
    if any(abs(x) <= half_x and abs(y) <= half_y for x, y in (first, last)):
        return 0
    corners = [(-half_x, -half_y), (half_x, -half_y),
               (half_x, half_y), (-half_x, half_y)]
    return min(segment_distance(first, last, corner, corners[(index + 1) % 4])
               for index, corner in enumerate(corners))


def check_board(board):
    tracks = list(board.GetTracks())
    pads = [pad for footprint in board.GetFootprints() for pad in footprint.Pads()]
    zones = list(board.Zones())
    if board.GetConnectivity().GetUnconnectedCount(False):
        raise RuntimeError('Board still has unconnected nets')
    if len(zones) != 2 or {zone.GetLayer() for zone in zones} != {pcb.F_Cu, pcb.B_Cu}:
        raise RuntimeError('Expected filled GND zones on both copper layers')
    if not all(zone.IsFilled() for zone in zones):
        raise RuntimeError('One or more GND zones are not filled')
    for track in tracks:
        start, end = mm_point(track.GetStart()), mm_point(track.GetEnd())
        half_width = pcb.ToMM(track.GetWidth()) / 2
        for pad in pads:
            if pad.GetAttribute() == pcb.PAD_ATTRIB_SMD and not pad.IsOnLayer(track.GetLayer()):
                continue
            if pad.GetAttribute() != pcb.PAD_ATTRIB_NPTH and pad.GetNetname() == track.GetNetname():
                continue
            clearance = pad_distance(pad, start, end) - half_width
            if clearance < CLEARANCE_MM - 1e-5:
                raise RuntimeError(f'{track.GetNetname()} trace {start}->{end} too close to '
                                   f'{pad.GetParentFootprint().GetReference()} pad {pad.GetNumber()} '
                                   f'at {mm_point(pad.GetPosition())}: {clearance:.3f} mm')

    for index, first in enumerate(tracks):
        for second in tracks[index + 1:]:
            if first.GetLayer() != second.GetLayer() or first.GetNetCode() == second.GetNetCode():
                continue
            separation = segment_distance(mm_point(first.GetStart()), mm_point(first.GetEnd()),
                                          mm_point(second.GetStart()), mm_point(second.GetEnd()))
            clearance = separation - pcb.ToMM(first.GetWidth() + second.GetWidth()) / 2
            if clearance < CLEARANCE_MM - 1e-5:
                raise RuntimeError(f'{first.GetNetname()} and {second.GetNetname()} traces too close: {clearance:.3f} mm')


def route(board, net, layer, coordinates):
    previous_direction = None
    for start, end in zip(coordinates, coordinates[1:]):
        if start == end:
            continue
        direction = (round(end[0] - start[0], 6), round(end[1] - start[1], 6))
        if previous_direction and abs(sum(a * b for a, b in zip(previous_direction, direction))) < 1e-9:
            raise RuntimeError(f'90-degree turn in {net.GetNetname()} at {start}')
        dx = round(abs(end[0] - start[0]), 6)
        dy = round(abs(end[1] - start[1]), 6)
        if dx and dy and abs(dx - dy) > 0.000002:
            raise RuntimeError(f'Non-45-degree track in {net.GetNetname()}: {start}->{end}')
        track = pcb.PCB_TRACK(board)
        track.SetStart(point(start))
        track.SetEnd(point(end))
        track.SetWidth(pcb.FromMM(WIDTH_MM))
        track.SetLayer(layer)
        track.SetNetCode(net.GetNetCode())
        board.Add(track)
        previous_direction = direction


def add_ground_zone(board, ground, layer):
    zone = pcb.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNetCode(ground.GetNetCode())
    zone.SetMinThickness(pcb.FromMM(0.1 if WIDTH_MM < 0.3 else 0.25))
    zone.SetLocalClearance(pcb.FromMM(CLEARANCE_MM))
    zone.SetThermalReliefGap(pcb.FromMM(max(0.15, CLEARANCE_MM)))
    zone.SetThermalReliefSpokeWidth(pcb.FromMM(0.2 if WIDTH_MM < 0.3 else 0.35))
    zone.SetIslandRemovalMode(pcb.ISLAND_REMOVAL_MODE_ALWAYS)
    polygon = zone.Outline()
    polygon.NewOutline()
    bounds = board_bounds(board)
    left, top, right, bottom = bounds
    inset = 0.8
    for xy in [(left + inset, top + inset), (right - inset, top + inset),
               (right - inset, bottom - inset), (left + inset, bottom - inset)]:
        polygon.Append(*point(xy))
    board.Add(zone)


def make_base_plate():
    plate = pcb.LoadBoard(str(BOARD))
    if list(plate.GetTracks()) or list(plate.Zones()):
        raise RuntimeError('Base plate source must be the un-routed Ergogen board')

    for footprint in list(plate.GetFootprints()):
        is_controller = footprint.GetReference().startswith('MCU')
        pads = list(footprint.Pads())
        if footprint.GetReference().startswith(('LCD', 'W')):
            positions = [pad.GetPosition() for pad in pads]
            center = pcb.VECTOR2I(sum(position.x for position in positions) // len(positions),
                                 sum(position.y for position in positions) // len(positions))
            length = max(position.y for position in positions) - min(position.y for position in positions) + pcb.FromMM(1.8)
            reference = footprint.GetReference()
            plate.Remove(footprint)
            footprint = pcb.FOOTPRINT(plate)
            footprint.SetReference(reference)
            footprint.SetValue('Header clearance')
            plate.Add(footprint)
            slot = pcb.PAD(footprint)
            slot.SetAttribute(pcb.PAD_ATTRIB_NPTH)
            slot.SetShape(pcb.PAD_SHAPE_OVAL)
            slot.SetDrillShape(pcb.PAD_DRILL_SHAPE_OBLONG)
            slot.SetSize(pcb.VECTOR2I(pcb.FromMM(1.8), length))
            slot.SetDrillSize(slot.GetSize())
            slot.SetPosition(center)
            slot.SetLayerSet(pcb.LSET.AllCuMask())
            footprint.Add(slot)
            pads = [slot]
        footprint.Reference().SetVisible(False)
        footprint.Value().SetVisible(False)
        for pad in pads:
            if pad.GetAttribute() != pcb.PAD_ATTRIB_NPTH:
                diameter = 2.0 if is_controller else 2.8
                drill = pcb.VECTOR2I(pcb.FromMM(diameter), pcb.FromMM(diameter))
                pad.SetDrillSize(drill)
                pad.SetSize(drill)
            pad.SetAttribute(pcb.PAD_ATTRIB_NPTH)
            pad.SetNumber('')
            pad.SetNetCode(0)
        for graphic in list(footprint.GraphicalItems()):
            if graphic.GetLayer() in (pcb.F_SilkS, pcb.B_SilkS):
                graphic.SetLayer(pcb.F_Fab)
    plate.RemoveUnusedNets(None)

    left, top, right, bottom = board_bounds(plate)
    cx, cy = (left + right) / 2, (top + bottom) / 2
    r = RING_INNER_RADIUS_MM
    for start, end in [((cx - r - 1, cy), (cx - r + 1, cy)),
                       ((cx + r - 1, cy), (cx + r + 1, cy)),
                       ((cx, cy - r - 1), (cx, cy - r + 1)),
                       ((cx, cy + r - 1), (cx, cy + r + 1))]:
        marker = pcb.PCB_SHAPE(plate)
        marker.SetShape(pcb.SHAPE_T_SEGMENT)
        marker.SetStart(point(start))
        marker.SetEnd(point(end))
        marker.SetLayer(pcb.B_SilkS)
        marker.SetWidth(pcb.FromMM(0.16))
        plate.Add(marker)

    plate.GetTitleBlock().SetTitle('QBF Circuit-Free Base Plate')
    plate.GetTitleBlock().SetDate(date.today().isoformat())
    plate.Move(point(PAGE_OFFSET_MM))
    pcb.SaveBoard(str(BASE_PLATE), plate)
    check_base_plate(pcb.LoadBoard(str(BASE_PLATE)))


def check_base_plate(plate):
    if list(plate.GetTracks()) or list(plate.Zones()):
        raise RuntimeError('Base plate has tracks or copper zones')
    pads = [pad for footprint in plate.GetFootprints() for pad in footprint.Pads()]
    if len(pads) != 81 or any(pad.GetAttribute() != pcb.PAD_ATTRIB_NPTH or
                              pad.GetNetCode() != 0 for pad in pads):
        raise RuntimeError('Base plate must have 81 unconnected mechanical holes or slots')
    markers = [drawing for drawing in plate.GetDrawings()
               if drawing.GetLayer() == pcb.B_SilkS]
    if len(markers) != 4 or any(marker.GetShape() != pcb.SHAPE_T_SEGMENT
                                for marker in markers):
        raise RuntimeError('Expected four B.SilkS ring alignment ticks')


def board_bounds(board):
    coordinates = [mm_point(position) for drawing in board.GetDrawings()
                   if drawing.GetLayer() == pcb.Edge_Cuts
                   for position in (drawing.GetStart(), drawing.GetEnd())]
    return (min(x for x, y in coordinates), min(y for x, y in coordinates),
            max(x for x, y in coordinates), max(y for x, y in coordinates))


def cap_bounds(footprint):
    positions = [mm_point(position) for drawing in footprint.GraphicalItems()
                 if drawing.GetLayer() == pcb.Dwgs_User
                 for position in (drawing.GetStart(), drawing.GetEnd())]
    return (min(x for x, y in positions), min(y for x, y in positions),
            max(x for x, y in positions), max(y for x, y in positions))


def check_layout(board, output):
    switches = [footprint for footprint in board.GetFootprints()
                if footprint.GetReference().startswith('S')]
    controllers = [footprint for footprint in board.GetFootprints()
                   if footprint.GetReference().startswith('MCU')]
    mounts = [mm_point(footprint.GetPosition()) for footprint in board.GetFootprints()
              if footprint.GetReference().startswith('H')]
    if len(switches) != 10 or len(controllers) != 1 or len(mounts) != 6:
        raise RuntimeError('Expected ten switches, one controller and six mounts')
    main = [footprint for footprint in switches
            if cap_bounds(footprint)[3] - cap_bounds(footprint)[1] > 20]
    extra = [footprint for footprint in switches if footprint not in main]
    if len(main) != 8 or len(extra) != 2:
        raise RuntimeError('Expected eight portrait and two landscape 1.5U caps')
    xs = sorted({mm_point(footprint.GetPosition())[0] for footprint in main})
    ys = sorted({mm_point(footprint.GetPosition())[1] for footprint in main})
    if len(xs) != 4 or len(ys) != 2 or abs(ys[1] - ys[0] - 27.5) > 0.001:
        raise RuntimeError('The main rows must have a 1 mm cap gap')
    if any(abs(right - left - 19.05) > 0.001 for left, right in zip(xs, xs[1:])):
        raise RuntimeError('Expected 19.05 mm horizontal key spacing')
    expected_mounts = {(round((xs[index] + xs[index + 1]) / 2, 4), y)
                       for index in (0, 2) for y in ys}
    right_mount_x = round(board_bounds(board)[2] - 2.25, 4)
    expected_mounts.update((right_mount_x, y) for y in ys)
    if set(mounts) != expected_mounts:
        raise RuntimeError('Mounts must sit between columns 1/2 and 3/4 and beside the rightmost keys')
    cx, cy = mm_point(controllers[0].GetPosition())
    if abs(cy - sum(ys) / 2) > 0.001 or abs(cx - 83.9) > 0.001:
        raise RuntimeError('Controller must be centered in the next column to the right')
    extra_positions = sorted(mm_point(footprint.GetPosition()) for footprint in extra)
    if any(abs(x - xs[-1] - 24.05) > 0.001 for x, y in extra_positions):
        raise RuntimeError('Landscape keys must retain the 2.55 mm gap to column four')
    if any(abs(abs(y - cy) - 18.75) > 0.001 for x, y in extra_positions):
        raise RuntimeError('Extra keys must align with the outer row edges')
    if not extra_positions[0][1] < cy < extra_positions[1][1]:
        raise RuntimeError('Expected one extra key above and one below the controller')
    left, top, right, bottom = board_bounds(board)
    caps = []
    for footprint in switches:
        bounds = cap_bounds(footprint)
        width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        expected_width, expected_height = (26.5, 16.5) if footprint in extra else (16.5, 26.5)
        if footprint.GetValue() != 'Choc v1 1.5U' or abs(width - expected_width) > 0.001 or abs(height - expected_height) > 0.001:
            raise RuntimeError(f'Incorrect cap dimensions: {footprint.GetReference()}')
        if bounds[0] < left or bounds[1] < top or bounds[2] > right or bounds[3] > bottom:
            raise RuntimeError(f'Cap outside board: {footprint.GetReference()}')
        caps.append(bounds)
    top_edges = [cap_bounds(footprint)[1] for footprint in switches
                 if mm_point(footprint.GetPosition())[1] < cy]
    bottom_edges = [cap_bounds(footprint)[3] for footprint in switches
                    if mm_point(footprint.GetPosition())[1] > cy]
    if max(top_edges) - min(top_edges) > 0.001 or max(bottom_edges) - min(bottom_edges) > 0.001:
        raise RuntimeError('All five outer cap edges must align in each row')
    rectangles = caps + [(cx - 18, cy - 9.15, cx + 18, cy + 9.15)]
    for first, second in itertools.combinations(rectangles, 2):
        if min(first[2], second[2]) > max(first[0], second[0]) and min(first[3], second[3]) > max(first[1], second[1]):
            raise RuntimeError('Overlapping keycaps or controller')
    displays = [footprint for footprint in board.GetFootprints()
                if footprint.GetReference().startswith('LCD')]
    if len(displays) != 1:
        raise RuntimeError('Expected one stacked display')
    dx, dy = mm_point(displays[0].GetPosition())
    display_bounds = (dx - 18, dy - 7, dx + 18, dy + 7)
    for cap in caps:
        if min(cap[2], display_bounds[2]) > max(cap[0], display_bounds[0]) and min(cap[3], display_bounds[3]) > max(cap[1], display_bounds[1]):
            raise RuntimeError('Display adapter overlaps a keycap')
    if display_bounds[2] > right - 0.499 or display_bounds[0] < xs[-1] + 8.749:
        raise RuntimeError('Display adapter must clear the fourth column and board edge')
    if any(pad.GetAttribute() != pcb.PAD_ATTRIB_NPTH and
           pad.GetAttribute() != pcb.PAD_ATTRIB_PTH
           for footprint in board.GetFootprints() for pad in footprint.Pads()):
        raise RuntimeError('Assembly must use through-hole components only')
    geometry = {
        'width': round(right - left, 3),
        'height': round(bottom - top, 3),
        'display': {'x': round(dx - left, 3), 'y': round(bottom - dy, 3),
                    'width': 36, 'height': 14, 'module_underside_z': 8.0,
                    'module_thickness': 2.9},
        'hole_x': sorted({round(x - left, 3) for x, y in mounts}),
        'hole_y': sorted({round(bottom - y, 3) for x, y in mounts}),
    }
    (output / 'board_geometry.json').write_text(json.dumps(geometry, indent=2) + '\n')
    print(f"Validated aligned outer cap edges and 1 mm main row gap; board {geometry['width']} x {geometry['height']} mm")


def grid_point(position):
    return tuple(round(value / GRID_MM) for value in position)


def grid_mm(position):
    return tuple(round(value * GRID_MM, 6) for value in position)


def mark_obstacle(blocked, start, end, radius):
    left, top = grid_point((min(start[0], end[0]) - radius - GRID_MM,
                            min(start[1], end[1]) - radius - GRID_MM))
    right, bottom = grid_point((max(start[0], end[0]) + radius + GRID_MM,
                                max(start[1], end[1]) + radius + GRID_MM))
    for x in range(left, right + 1):
        for y in range(top, bottom + 1):
            position = grid_mm((x, y))
            distance = math.dist(position, start) if start == end else point_to_segment_distance(position, start, end)
            if distance < radius:
                blocked.add((x, y))


def find_path(board, net, layer, start, end):
    blocked = set()
    margin = WIDTH_MM / 2 + 0.25 + GRID_MM / math.sqrt(2) + 0.01
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.GetAttribute() != pcb.PAD_ATTRIB_NPTH and pad.GetNetCode() == net.GetNetCode():
                continue
            size = pad.GetDrillSize() if pad.GetAttribute() == pcb.PAD_ATTRIB_NPTH else pad.GetSize()
            position = mm_point(pad.GetPosition())
            mark_obstacle(blocked, position, position, max(pcb.ToMM(size.x), pcb.ToMM(size.y)) / 2 + margin)
    for track in board.GetTracks():
        if track.GetLayer() == layer and track.GetNetCode() != net.GetNetCode():
            mark_obstacle(blocked, mm_point(track.GetStart()), mm_point(track.GetEnd()),
                          pcb.ToMM(track.GetWidth()) / 2 + margin)
    left, top, right, bottom = board_bounds(board)
    xmin, ymin = grid_point((left + 0.75, top + 0.75))
    xmax, ymax = grid_point((right - 0.75, bottom - 0.75))
    origin, target = grid_point(start), grid_point(end)
    if origin in blocked or target in blocked:
        raise RuntimeError(f'Blocked endpoint for {net.GetNetname()}')

    def estimate(position):
        dx, dy = abs(position[0] - target[0]), abs(position[1] - target[1])
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

    serial = itertools.count()
    queue = [(estimate(origin), next(serial), origin)]
    cost, parents = {origin: 0}, {}
    directions = ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    visited = set()
    while queue:
        _, _, current = heapq.heappop(queue)
        if current in visited:
            continue
        if current == target:
            path = [current]
            while current != origin:
                current = parents[current]
                path.append(current)
            return [grid_mm(position) for position in reversed(path)]
        visited.add(current)
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if not xmin <= neighbor[0] <= xmax or not ymin <= neighbor[1] <= ymax:
                continue
            if neighbor in blocked or neighbor in visited:
                continue
            if dx and dy and ((current[0] + dx, current[1]) in blocked or
                              (current[0], current[1] + dy) in blocked):
                continue
            new_cost = cost[current] + math.hypot(dx, dy)
            if current in parents:
                previous = parents[current]
                if (current[0] - previous[0], current[1] - previous[1]) != (dx, dy):
                    new_cost += 0.05
            if new_cost < cost.get(neighbor, math.inf):
                cost[neighbor] = new_cost
                parents[neighbor] = current
                heapq.heappush(queue, (new_cost + estimate(neighbor), next(serial), neighbor))
    raise RuntimeError(f'No route for {net.GetNetname()} on layer {layer}')


def terminal(start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    diagonal = min(abs(dx), abs(dy))
    knee = (round(start[0] + math.copysign(diagonal, dx), 6),
            round(start[1] + math.copysign(diagonal, dy), 6))
    return [start, knee, end]


def smooth_path(coordinates):
    compact = []
    for position in coordinates:
        if compact and math.dist(compact[-1], position) < 1e-6:
            continue
        compact.append(position)
        while len(compact) >= 3:
            a, b, c = compact[-3:]
            first, second = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
            if abs(first[0] * second[1] - first[1] * second[0]) > 1e-6 or sum(x * y for x, y in zip(first, second)) <= 0:
                break
            compact.pop(-2)
    result = [compact[0]]
    for a, b, c in zip(compact, compact[1:], compact[2:]):
        first, second = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
        if abs(sum(x * y for x, y in zip(first, second))) < 1e-6:
            trim = min(GRID_MM / 2, math.hypot(*first) / 3, math.hypot(*second) / 3)
            result.append(tuple(round(b[i] - first[i] / math.hypot(*first) * trim, 6) for i in (0, 1)))
            result.append(tuple(round(b[i] + second[i] / math.hypot(*second) * trim, 6) for i in (0, 1)))
        else:
            result.append(b)
    return result + [compact[-1]]


def route_signals(board):
    endpoints = {}
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.GetNetname() and pad.GetNetname() != 'GND':
                endpoints.setdefault(pad.GetNetname(), []).append(mm_point(pad.GetPosition()))
    if len(endpoints) != 14 or any(len(pads) != 2 for pads in endpoints.values()):
        raise RuntimeError('Expected ten direct key nets, three display signals and display power')
    ordered = sorted(endpoints, key=lambda name: (name.startswith('LCD_') or name == '3V3', math.dist(*endpoints[name])))
    for name in ordered:
        start, end = endpoints[name]
        net = board.FindNet(name)
        layer = pcb.F_Cu if name in ('P4', 'P6', 'P8', 'P9', 'P16', 'LCD_CLK', 'LCD_CS') else pcb.B_Cu
        try:
            path = find_path(board, net, layer, start, end)
        except RuntimeError:
            layer = pcb.B_Cu if layer == pcb.F_Cu else pcb.F_Cu
            path = find_path(board, net, layer, start, end)
        coordinates = terminal(start, path[0]) + path[1:-1] + terminal(path[-1], end)
        route(board, net, layer, smooth_path(coordinates))


def main():
    global BOARD, BASE_PLATE, PAGE_OFFSET_MM
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    BOARD = args.output / 'pcbs/macropad.kicad_pcb'
    BASE_PLATE = args.output / 'pcbs/baseplate.kicad_pcb'
    board = pcb.LoadBoard(str(BOARD))
    if list(board.GetTracks()) or list(board.Zones()):
        raise RuntimeError('Expected an un-routed Ergogen board; regenerate the layout first')
    left, top, right, bottom = board_bounds(board)
    PAGE_OFFSET_MM = (210 - (left + right) / 2, 148.5 - (top + bottom) / 2)
    check_layout(board, args.output)
    make_base_plate()
    route_signals(board)
    ground = board.FindNet('GND')
    for layer in (pcb.F_Cu, pcb.B_Cu):
        add_ground_zone(board, ground, layer)
    board.GetTitleBlock().SetTitle(DRAWING_TITLE)
    board.GetTitleBlock().SetDate(date.today().isoformat())
    board.Move(point(PAGE_OFFSET_MM))
    board.BuildConnectivity()
    pcb.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    pcb.SaveBoard(str(BOARD), board)
    check_board(pcb.LoadBoard(str(BOARD)))
    print(f'Generated circuit-free base plate with 81 holes or slots: {BASE_PLATE}')
    print(f'Routed {len(list(board.GetTracks()))} segments and filled two GND zones: {BOARD}')


if __name__ == '__main__':
    main()
