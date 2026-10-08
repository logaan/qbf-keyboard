"""Build the QBF base plate, route the main PCB, and fill GND on both sides.

Run with KiCad's Python interpreter (or any Python with pcbnew installed).
The pad-position checks make a layout change fail explicitly rather than leaving
stale traces connected to the wrong pads.
"""

from pathlib import Path
from datetime import date
import math

import pcbnew as pcb


BOARD = Path('generated/pcbs/macropad.kicad_pcb')
BASE_PLATE = Path('generated/pcbs/baseplate.kicad_pcb')
WIDTH_MM = 0.30
CORNER_MITER_MM = 0.75
PAGE_OFFSET_MM = (181.425, 165.5)  # Center the 73.65 x 60.5 mm board on A3.
DRAWING_TITLE = 'QBF Wireless Split Perkins Keyboard'
RING_CENTER_MM = (22.0, -17.0)
RING_INNER_RADIUS_MM = 23.0
RING_OUTER_RADIUS_MM = 28.0
GROUND_CHANNEL_SAMPLES = {}


def point(xy):
    return pcb.VECTOR2I(pcb.FromMM(xy[0]), pcb.FromMM(xy[1]))


def mm_point(vector):
    return (round(pcb.ToMM(vector.x), 2), round(pcb.ToMM(vector.y), 2))


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


def check_board(board):
    """Check connectivity and a conservative 0.25 mm copper clearance."""
    tracks = list(board.GetTracks())
    pads = [pad for footprint in board.GetFootprints() for pad in footprint.Pads()]
    zones = list(board.Zones())
    if board.GetConnectivity().GetUnconnectedCount(False):
        raise RuntimeError('Board still has unconnected nets')
    if len(zones) != 2 or {zone.GetLayer() for zone in zones} != {pcb.F_Cu, pcb.B_Cu}:
        raise RuntimeError('Expected filled GND zones on both copper layers')
    if not all(zone.IsFilled() for zone in zones):
        raise RuntimeError('One or more GND zones are not filled')
    front_zone = next(zone for zone in zones if zone.GetLayer() == pcb.F_Cu)
    front_fill = front_zone.GetFilledPolysList(pcb.F_Cu)
    for channel, xy in GROUND_CHANNEL_SAMPLES.items():
        position = point((xy[0] + PAGE_OFFSET_MM[0], xy[1] + PAGE_OFFSET_MM[1]))
        if not front_fill.Contains(position):
            raise RuntimeError(f'No front GND copper between {channel} traces')

    for track in tracks:
        start, end = mm_point(track.GetStart()), mm_point(track.GetEnd())
        half_width = pcb.ToMM(track.GetWidth()) / 2
        for pad in pads:
            if pad.GetAttribute() == pcb.PAD_ATTRIB_NPTH:
                radius = pcb.ToMM(pad.GetDrillSize().x) / 2
            elif pad.GetNetname() != track.GetNetname():
                radius = pcb.ToMM(pad.GetSize().x) / 2
            else:
                continue
            clearance = point_to_segment_distance(mm_point(pad.GetPosition()), start, end) - radius - half_width
            if clearance < 0.25 - 1e-5:
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
            if clearance < 0.25 - 1e-5:
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
        if dx and dy and dx != dy:
            raise RuntimeError(f'Non-45-degree track in {net.GetNetname()}: {start}->{end}')
        track = pcb.PCB_TRACK(board)
        track.SetStart(point(start))
        track.SetEnd(point(end))
        track.SetWidth(pcb.FromMM(WIDTH_MM))
        track.SetLayer(layer)
        track.SetNetCode(net.GetNetCode())
        board.Add(track)
        previous_direction = direction


def fan_in(start, lane_y, target):
    """Join a horizontal lane and the header approach with 45-degree bends."""
    target_x, target_y = target
    diagonal = abs(lane_y - start[1])
    knee_x = round(start[0] + diagonal, 2)
    if knee_x >= target_x - CORNER_MITER_MM or abs(target_y - lane_y) <= CORNER_MITER_MM:
        raise RuntimeError(f'Not enough space for 45-degree bends: {start}->{target}')
    turn_y = round(lane_y + math.copysign(CORNER_MITER_MM, target_y - lane_y), 2)
    return [(knee_x, lane_y), (round(target_x - CORNER_MITER_MM, 2), lane_y),
            (target_x, turn_y)]


def add_ground_zone(board, ground, layer):
    zone = pcb.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNetCode(ground.GetNetCode())
    zone.SetLocalClearance(pcb.FromMM(0.25))
    zone.SetThermalReliefGap(pcb.FromMM(0.30))
    zone.SetThermalReliefSpokeWidth(pcb.FromMM(0.35))
    zone.SetIslandRemovalMode(pcb.ISLAND_REMOVAL_MODE_ALWAYS)
    polygon = zone.Outline()
    polygon.NewOutline()
    # Inset 0.8 mm from the cap-sized rounded board outline.
    for xy in [(-6.75, -46.45), (63.9, -46.45), (64.6, -45.75),
               (64.6, 11.75), (63.9, 12.45), (-6.75, 12.45),
               (-7.45, 11.75), (-7.45, -45.75)]:
        polygon.Append(*point(xy))
    board.Add(zone)


def make_base_plate():
    """Copy the board shape and drill positions without any electrical circuit."""
    plate = pcb.LoadBoard(str(BOARD))
    if list(plate.GetTracks()) or list(plate.Zones()):
        raise RuntimeError('Base plate source must be the un-routed Ergogen board')

    for footprint in list(plate.GetFootprints()):
        is_controller = footprint.GetReference().startswith('MCU')
        pads = list(footprint.Pads())
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

    # The filled disc aligns with the inside edge of a 46/56 mm adhesive ring.
    # The annulus where its adhesive sits remains bare board finish.
    marker = pcb.PCB_SHAPE(plate)
    marker.SetShape(pcb.SHAPE_T_CIRCLE)
    marker.SetStart(point(RING_CENTER_MM))
    marker.SetEnd(point((RING_CENTER_MM[0] + RING_INNER_RADIUS_MM,
                         RING_CENTER_MM[1])))
    marker.SetLayer(pcb.B_SilkS)
    marker.SetWidth(pcb.FromMM(0.12))
    marker.SetFilled(True)
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
    if len(pads) != 58 or any(pad.GetAttribute() != pcb.PAD_ATTRIB_NPTH or
                              pad.GetNetCode() != 0 for pad in pads):
        raise RuntimeError('Base plate must have 58 unconnected mechanical holes')
    # The adhesive ring may overlap mechanical and component-clearance holes.
    markers = [drawing for drawing in plate.GetDrawings()
               if drawing.GetLayer() == pcb.B_SilkS]
    if len(markers) != 1 or not markers[0].IsSolidFill() or \
            markers[0].GetShape() != pcb.SHAPE_T_CIRCLE:
        raise RuntimeError('Expected one filled B.SilkS alignment disc')


def main():
    board = pcb.LoadBoard(str(BOARD))
    if len(list(board.GetTracks())) or len(list(board.Zones())):
        raise RuntimeError('Expected an un-routed Ergogen board; run npm run layout first')

    make_base_plate()

    nets = {net.GetNetname(): net for net in board.GetNetInfo().NetsByNetcode().values()}
    pads = {}
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            name = pad.GetNetname()
            if name:
                pads.setdefault(name, []).append(mm_point(pad.GetPosition()))

    expected = {
        'D6': [(-5.9, -34.0), (47.38, -24.62)],
        'D5': [(13.15, -34.0), (49.92, -24.62)],
        'D4': [(32.2, -34.0), (52.46, -24.62)],
        'D3': [(51.25, -34.0), (55.0, -24.62)],
        'D7': [(-3.8, -5.0), (47.38, -9.38)],
        'D8': [(15.25, -5.0), (49.92, -9.38)],
        'D9': [(34.3, -5.0), (52.46, -9.38)],
        'D10': [(53.35, -5.0), (55.0, -9.38)],
    }
    for name, endpoints in expected.items():
        if sorted(pads.get(name, [])) != sorted(endpoints):
            raise RuntimeError(f'{name} pad positions changed: {pads.get(name)}')
    if len(pads.get('GND', [])) != 9:
        raise RuntimeError('Expected eight grounded switches and one XIAO GND pad')

    # Both rows leave the switch pads beside their mounting holes, then
    # approach the header pads from clear lanes between the switch rows.
    # 1.8 mm lane pitch leaves room for 0.25 mm clearance on each side
    # of a 0.30 mm trace and a useful strip of GND copper between traces.
    top_approach = {'D6': -23.0, 'D5': -21.2, 'D4': -19.4, 'D3': -17.6}
    bottom_approach = {'D7': -11.0, 'D8': -12.8, 'D9': -14.6, 'D10': -16.4}
    for name, endpoints in expected.items():
        start, end = endpoints
        if name == 'D4':
            coordinates = [start, (start[0], -27.7), (start[0] + 1, -26.7),
                           (end[0] - 1, -26.7), (end[0], -25.7), end]
        elif name == 'D9':
            coordinates = [start, (start[0], -6.2), (start[0] + 1, -7.2),
                           (end[0] - 1, -7.2), (end[0], -8.2), end]
        elif name == 'D3':
            coordinates = [start, (start[0], -29.12), (end[0], -25.37), end]
        elif name == 'D10':
            coordinates = [start, (start[0], -7.73), end]
        elif start[1] == -34:
            exit_pad = (start[0], -27.0)
            coordinates = [start, exit_pad] + fan_in(exit_pad, top_approach[name], end) + [end]
        else:
            exit_pad = (start[0], -8.0)
            coordinates = [start, exit_pad] + fan_in(exit_pad, bottom_approach[name], end) + [end]
        layer = pcb.F_Cu if name in ('D6', 'D4', 'D7', 'D9') else pcb.B_Cu
        route(board, nets[name], layer, coordinates)

    for layer in (pcb.F_Cu, pcb.B_Cu):
        add_ground_zone(board, nets['GND'], layer)
    board.GetTitleBlock().SetTitle(DRAWING_TITLE)
    board.GetTitleBlock().SetDate(date.today().isoformat())
    board.Move(point(PAGE_OFFSET_MM))
    board.BuildConnectivity()
    pcb.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    pcb.SaveBoard(str(BOARD), board)
    check_board(pcb.LoadBoard(str(BOARD)))
    print(f'Generated circuit-free base plate with 58 holes: {BASE_PLATE}')
    print(f'Routed {len(list(board.GetTracks()))} segments and filled two GND zones: {BOARD}')


if __name__ == '__main__':
    main()
