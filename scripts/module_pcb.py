import argparse
import json
from pathlib import Path

import pcbnew as pcb

parser = argparse.ArgumentParser()
parser.add_argument('board', type=Path)
parser.add_argument('config', type=Path)
args = parser.parse_args()
if pcb.Version().split('.')[0] != '10':
    raise SystemExit('KiCad 10 Python bindings required')
board = pcb.LoadBoard(str(args.board))
board.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.6))
items = list(board.GetFootprints())
controller = next(f for f in items if f.GetReference() == 'MCU1')
display = next(f for f in items if f.GetReference() == 'DISP1')
if display.GetLayer() != pcb.F_Cu:
    raise SystemExit('Display must be on the top face')
pads = {p.GetNumber(): p.GetNetname() for p in controller.Pads()}
if pads['25'] != 'GND' or pads['26'] != 'VBAT':
    raise SystemExit('Controller battery polarity mismatch')
switches = [f for f in items if f.GetFPID().GetLibItemName() == 'switch_choc_v1_v2']
key_nets = []
for switch in switches:
    nets = {p.GetNetname() for p in switch.Pads() if p.GetNetname()}
    if 'GND' not in nets or len(nets) != 2:
        raise SystemExit(f'{switch.GetReference()}: switches must be directly wired to GPIO and ground')
    net = (nets - {'GND'}).pop()
    if list(pads.values()).count(net) != 1:
        raise SystemExit(f'{net}: expected one controller GPIO connection')
    key_nets.append(net)
if len(set(key_nets)) != len(key_nets):
    raise SystemExit('Duplicate key net')
for net in ('DISPLAY_CS', 'DISPLAY_MOSI', 'DISPLAY_SCK', '3V3'):
    if net not in pads.values() or net not in {p.GetNetname() for p in display.Pads()}:
        raise SystemExit(f'{net}: display/controller connection missing')
settings = board.GetDesignSettings()
box = board.GetBoardEdgesBoundingBox()
records = [{'reference': f.GetReference(), 'position': [pcb.ToMM(f.GetPosition().x), pcb.ToMM(f.GetPosition().y)],
            'side': 'F' if f.GetLayer() == pcb.F_Cu else 'B',
            'pads': {p.GetNumber(): p.GetNetname() for p in f.Pads() if p.GetNetname()}} for f in items]
report = {'kicad': pcb.Version(), 'stage': 'placement diagnostic only', 'fabrication_ready': False,
          'keys': key_nets, 'footprints': records,
          'outline_bbox_mm': [pcb.ToMM(box.GetWidth()), pcb.ToMM(box.GetHeight())]}
args.config.write_text(json.dumps(report, indent=2) + '\n')
pcb.SaveBoard(str(args.board), board)
