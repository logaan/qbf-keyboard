"""Route the fixed QBF layout produced by Ergogen, then fill GND on both sides.

Run with KiCad's Python interpreter (or any Python with pcbnew installed).
The pad-position checks make a layout change fail explicitly rather than leaving
stale traces connected to the wrong pads.
"""

from pathlib import Path
import math

import pcbnew as pcb


BOARD = Path('generated/pcbs/macropad.kicad_pcb')
WIDTH_MM = 0.30


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
                raise RuntimeError(f'{track.GetNetname()} trace too close to pad or hole: {clearance:.3f} mm')

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
    for start, end in zip(coordinates, coordinates[1:]):
        if start == end:
            continue
        track = pcb.PCB_TRACK(board)
        track.SetStart(point(start))
        track.SetEnd(point(end))
        track.SetWidth(pcb.FromMM(WIDTH_MM))
        track.SetLayer(layer)
        track.SetNetCode(net.GetNetCode())
        board.Add(track)


def add_ground_zone(board, ground, layer):
    zone = pcb.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNetCode(ground.GetNetCode())
    zone.SetLocalClearance(pcb.FromMM(0.25))
    zone.SetThermalReliefGap(pcb.FromMM(0.30))
    zone.SetThermalReliefSpokeWidth(pcb.FromMM(0.35))
    polygon = zone.Outline()
    polygon.NewOutline()
    # Inset from the rounded 75 x 82 mm board outline.
    for xy in [(-5.5, -65.2), (62.5, -65.2), (65.2, -62.5),
               (65.2, 12.5), (62.5, 15.2), (-5.5, 15.2),
               (-8.2, 12.5), (-8.2, -62.5)]:
        polygon.Append(*point(xy))
    board.Add(zone)


def main():
    board = pcb.LoadBoard(str(BOARD))
    if len(list(board.GetTracks())) or len(list(board.Zones())):
        raise RuntimeError('Expected an un-routed Ergogen board; run npm run layout first')

    nets = {net.GetNetname(): net for net in board.GetNetInfo().NetsByNetcode().values()}
    pads = {}
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            name = pad.GetNetname()
            if name:
                pads.setdefault(name, []).append(mm_point(pad.GetPosition()))

    expected = {
        'K0': [(-5.9, -50.0), (62.62, -32.62)],
        'K1': [(12.1, -50.0), (60.08, -32.62)],
        'K2': [(30.1, -50.0), (57.54, -32.62)],
        'K3': [(48.1, -50.0), (55.0, -32.62)],
        'K4': [(-5.9, 0.0), (52.46, -32.62)],
        'K5': [(12.1, 0.0), (49.92, -32.62)],
        'K6': [(30.1, 0.0), (47.38, -32.62)],
        'K7': [(48.1, 0.0), (47.38, -17.38)],
    }
    for name, endpoints in expected.items():
        if sorted(pads.get(name, [])) != sorted(endpoints):
            raise RuntimeError(f'{name} pad positions changed: {pads.get(name)}')
    if len(pads.get('GND', [])) != 9:
        raise RuntimeError('Expected eight grounded switches and one XIAO GND pad')

    # Top row fans out above the switches, then enters D0-D3 from above.
    top = {
        'K0': [(-5.9, -50), (-7.4, -51.5), (-7.4, -62), (62.62, -62), (62.62, -32.62)],
        'K1': [(12.1, -50), (10.6, -51.5), (10.6, -60.5), (60.08, -60.5), (60.08, -32.62)],
        'K2': [(30.1, -50), (28.6, -51.5), (28.6, -59), (57.54, -59), (57.54, -32.62)],
    }
    for name, coordinates in top.items():
        route(board, nets[name], pcb.B_Cu, coordinates)
    # K3 goes around the rightmost switch's three non-plated mounting holes.
    route(board, nets['K3'], pcb.F_Cu,
          [(48.1, -50), (46.6, -51.5), (46.6, -57.5),
           (57.5, -57.5), (57.5, -42.5), (55, -40), (55, -32.62)])

    # Bottom row crosses the gap below the top switches on the front layer.
    bottom = {
        'K4': [(-5.9, 0), (-7.4, -1.5), (-7.4, -41), (52.46, -41), (52.46, -32.62)],
        'K5': [(12.1, 0), (10.6, -1.5), (10.6, -39), (49.92, -39), (49.92, -32.62)],
        'K6': [(30.1, 0), (28.6, -1.5), (28.6, -37), (47.38, -37), (47.38, -32.62)],
        'K7': [(48.1, 0), (47.38, -0.72), (47.38, -17.38)],
    }
    for name, coordinates in bottom.items():
        route(board, nets[name], pcb.F_Cu, coordinates)

    for layer in (pcb.F_Cu, pcb.B_Cu):
        add_ground_zone(board, nets['GND'], layer)
    pcb.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    pcb.SaveBoard(str(BOARD), board)
    check_board(pcb.LoadBoard(str(BOARD)))
    print(f'Routed {len(list(board.GetTracks()))} segments and filled two GND zones: {BOARD}')


if __name__ == '__main__':
    main()
