import argparse
import itertools
import json
import math
from pathlib import Path

import pcbnew as pcb
import route_board as router

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('destination', type=Path)
parser.add_argument('spec', type=Path)
parser.add_argument('--strategy', choices=['shortest', 'longest', 'signals-first'], default='longest')
args = parser.parse_args()
spec = json.loads(args.spec.read_text())['routing']
router.CLEARANCE_MM = spec['clearance']
board = pcb.LoadBoard(str(args.source))
if pcb.Version().split('.')[0] != '10':
    raise SystemExit('KiCad 10 is required')
if list(board.GetTracks()) or list(board.Zones()):
    raise SystemExit('Router requires a fresh placement board')
keepout = spec['antenna_keepout']
rf = [100 + keepout[0], 100 - keepout[3], 100 + keepout[2], 100 - keepout[1]]
exclusions = [(rf, 0)]
endpoints = {}
for footprint in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
    for pad in sorted(footprint.Pads(), key=lambda p: p.GetNumber()):
        if pad.GetNetname():
            endpoints.setdefault(pad.GetNetname(), []).append(pad)
fanouts = {}
fanout_vias = []
for name, pads in sorted(endpoints.items()):
    if len(pads) < 2:
        continue
    for pad in pads:
        if pad.GetParentFootprint().GetReference() != 'MCU1':
            continue
        x, y = router.mm_point(pad.GetPosition())
        target = (87.4 if x < 100 else 112.6, y)
        router.WIDTH_MM = spec['power_width'] if name in {'VBAT', 'BAT_P', '3V3'} else spec['signal_width']
        router.route(board, board.FindNet(name), pcb.B_Cu, [(x, y), target])
        via = pcb.PCB_VIA(board)
        via.SetPosition(router.point(target))
        via.SetWidth(pcb.FromMM(spec['via_diameter']))
        via.SetDrill(pcb.FromMM(spec['via_drill']))
        via.SetLayerPair(pcb.F_Cu, pcb.B_Cu)
        via.SetNetCode(pad.GetNetCode())
        board.Add(via)
        fanout_vias.append(via)
        terminal = pcb.PAD(pad.GetParentFootprint())
        terminal.SetPosition(router.point(target))
        terminal.SetAttribute(pcb.PAD_ATTRIB_PTH)
        terminal.SetLayerSet(pcb.LSET.AllCuMask())
        terminal.SetNetCode(pad.GetNetCode())
        fanouts[(pad.GetParentFootprint().GetReference(), pad.GetNumber())] = terminal
connections = []
for name, pads in sorted(endpoints.items()):
    pads = [fanouts.get((p.GetParentFootprint().GetReference(), p.GetNumber()), p) for p in pads]
    if name == 'GND':
        continue
    connected, pending = pads[:1], pads[1:]
    while pending:
        first, last = min(itertools.product(connected, pending), key=lambda pair: math.dist(router.mm_point(pair[0].GetPosition()), router.mm_point(pair[1].GetPosition())))
        connections.append((name, first, last))
        connected.append(last)
        pending.remove(last)
power = {'VBAT', 'BAT_P', '3V3'}
connections.sort(key=lambda c: ((0 if c[0] in power else 1) * (-1 if args.strategy == 'signals-first' else 1), math.dist(router.mm_point(c[1].GetPosition()), router.mm_point(c[2].GetPosition())) * (-1 if args.strategy == 'longest' else 1), c[0]))
for name, first, last in connections:
    router.WIDTH_MM = spec['power_width'] if name in power else spec['signal_width']
    print(f'Routing {name} at {router.WIDTH_MM:.2f} mm', flush=True)
    router.route_connection(board, board.FindNet(name), first, last, exclusions)
for via in fanout_vias:
    if via.GetNetname() == 'GND':
        continue
    position = router.mm_point(via.GetPosition())
    layers = {track.GetLayer() for track in board.GetTracks() if not isinstance(track, pcb.PCB_VIA)
              and track.GetNetCode() == via.GetNetCode()
              and router.point_to_segment_distance(position, router.mm_point(track.GetStart()), router.mm_point(track.GetEnd())) < 1e-6}
    if len(layers) < 2:
        board.Remove(via)
router.WIDTH_MM = spec['signal_width']
vias = [track for track in board.GetTracks() if isinstance(track, pcb.PCB_VIA)]
removed = set()
for index, first in enumerate(vias):
    if index in removed:
        continue
    for other, last in enumerate(vias[index + 1:], index + 1):
        if other in removed or first.GetNetCode() != last.GetNetCode():
            continue
        start, end = router.mm_point(first.GetPosition()), router.mm_point(last.GetPosition())
        if math.dist(start, end) < spec['via_drill'] + spec['clearance']:
            for layer in (pcb.F_Cu, pcb.B_Cu):
                router.route(board, board.FindNet(first.GetNetname()), layer, router.smooth_path(router.terminal(start, end)))
            board.Remove(last)
            removed.add(other)
ground = board.FindNet('GND')
blocked = router.route_blocked(board, ground, exclusions)
left, top, right, bottom = router.board_bounds(board)
stitches = []
for x in range(math.ceil((left + 2) / 8) * 8, math.floor(right - 2) + 1, 8):
    for y in range(math.ceil((top + 2) / 8) * 8, math.floor(bottom - 2) + 1, 8):
        if min(x - left, right - x, y - top, bottom - y) > 10:
            continue
        gx, gy = router.grid_point((x, y))
        if any((gx + dx, gy + dy) in blocked[layer] for layer in (0, 1) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue
        via = pcb.PCB_VIA(board)
        via.SetPosition(router.point((x, y)))
        via.SetWidth(pcb.FromMM(spec['via_diameter']))
        via.SetDrill(pcb.FromMM(spec['via_drill']))
        via.SetLayerPair(pcb.F_Cu, pcb.B_Cu)
        via.SetNetCode(ground.GetNetCode())
        board.Add(via)
        stitches.append((x, y))
for layer in (pcb.F_Cu, pcb.B_Cu):
    router.add_rule_area(board, rf, 'Controller antenna reservation', layer)
    router.add_ground_zone(board, ground, layer)
board.BuildConnectivity()
pcb.ZONE_FILLER(board).Fill(board.Zones())
board.BuildConnectivity()
opens = board.GetConnectivity().GetUnconnectedCount(False)
args.destination.parent.mkdir(exist_ok=True)
pcb.SaveBoard(str(args.destination), board)
area = (right - left) * (bottom - top)
zones = []
for zone in board.Zones():
    if not zone.GetIsRuleArea():
        zone.CalculateFilledArea()
        filled = zone.GetFilledArea() / 1e12
        zones.append({'layer': board.GetLayerName(zone.GetLayer()), 'net': zone.GetNetname(),
                      'filled_area_mm2': round(filled, 3), 'board_bbox_coverage': round(filled / area, 4)})
report = {'router': 'shared QBF two-layer A*', 'unconnected': opens, 'ground_zones': zones,
          'ground_stitching_vias': len(stitches), 'track_count': len(list(board.GetTracks())),
          'signal_width_mm': spec['signal_width'], 'power_width_mm': spec['power_width'],
          'clearance_mm': spec['clearance'], 'antenna_keepout_kicad': rf, 'fabrication_ready': False}
(args.destination.parent.parent / 'routing.json').write_text(json.dumps(report, indent=2) + '\n')
if opens:
    raise SystemExit(f'Router left {opens} unconnected items; inspect staged outputs')
if len(zones) != 2 or any(z['net'] != 'GND' or z['board_bbox_coverage'] < 0.6 for z in zones):
    raise SystemExit('Expected two broad ground pours, each covering at least 60% of the board')
print(f'Routed {len(connections)} connections; {len(stitches)} ground stitches; zero opens', flush=True)
