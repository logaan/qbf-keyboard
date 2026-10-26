"""Create the KiCad review source, real routing exchange, and geometry report."""
from pathlib import Path
import csv
import json
import math
import pcbnew as pcb
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'kicad'
OUT.mkdir(exist_ok=True)
units = yaml.safe_load((ROOT / 'output/points/units.yaml').read_text())
points = yaml.safe_load((ROOT / 'output/points/points.yaml').read_text())
board = pcb.LoadBoard(str(ROOT / 'output/pcbs/braille_placement.kicad_pcb'))
board.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.6))

def xy(v):
    return [v.x / 1e6, v.y / 1e6]

def text(value, x, y, layer=pcb.Dwgs_User, size=0.85):
    t = pcb.PCB_TEXT(board)
    t.SetText(value)
    t.SetPosition(pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(y)))
    t.SetTextSize(pcb.VECTOR2I(pcb.FromMM(size), pcb.FromMM(size)))
    t.SetTextThickness(pcb.FromMM(0.12))
    t.SetLayer(layer)
    board.Add(t)

footprints = list(board.GetFootprints())
switches = [f for f in footprints if f.GetFPID().GetLibItemName() == 'switch_choc_v1_v2']
controller = next(f for f in footprints if f.GetReference() == 'MCU1')
display = next(f for f in footprints if f.GetReference() == 'DISP1')
mounts = [f for f in footprints if f.GetReference().startswith('MH')]
collisions = []
for fp in switches:
    for sp in fp.Pads():
        if sp.GetAttribute() != pcb.PAD_ATTRIB_NPTH:
            continue
        sx, sy = xy(sp.GetPosition())
        sr = sp.GetSize().x / 2e6
        for hp in controller.Pads():
            hx, hy = xy(hp.GetPosition())
            hr = hp.GetSize().x / 2e6
            clearance = math.hypot(sx-hx, sy-hy) - sr - hr
            if clearance < 0.25:
                item = {'switch': fp.GetReference(), 'header_pad': hp.GetNumber(),
                        'switch_hole': [sx, sy], 'header': [hx, hy],
                        'edge_clearance_mm': round(clearance, 4),
                        'status': 'ACCEPTED FOR MANUAL KICAD REVIEW'}
                collisions.append(item)
                circle = pcb.PCB_SHAPE(board)
                circle.SetShape(pcb.SHAPE_T_CIRCLE)
                circle.SetCenter(pcb.VECTOR2I(pcb.FromMM(sx), pcb.FromMM(sy)))
                circle.SetEnd(pcb.VECTOR2I(pcb.FromMM(sx+2.8), pcb.FromMM(sy)))
                circle.SetWidth(pcb.FromMM(0.16))
                circle.SetLayer(pcb.User_1)
                board.Add(circle)

cx = 100 + 1.5 * units['pitch_x']
xmin = cx - units['board_w']/2
ymin = 100 - units['board_h']/2
ymax = 100 + units['board_h']/2
text('REVIEW DRAFT - ACCEPTED HEADER/SHAFT CLASHES ON User.1', cx, ymax+4)
text('NO MANUFACTURING RELEASE - CHECK MECHANICAL STACK AND DRC', cx, ymax+5.5)
text('USB OUTWARD - KEEP CABLE ACCESS CLEAR', controller.GetPosition().x/1e6, ymin-3.2)
text('301230 CELL ENVELOPE - NO SHARP HARDWARE IN THIS VOLUME', points['battery']['x'], 100, size=0.55)

headers = {p.GetNumber(): p for p in controller.Pads()}
assert len(headers) == 26
assert headers['25'].GetNetname() == 'GND'
assert headers['26'].GetNetname() == 'VBAT'
for side in (-1, 1):
    row = sorted([p.GetPosition().y/1e6 for p in controller.Pads()
                  if (p.GetPosition().x-controller.GetPosition().x)*side > 0])
    assert len(row) == 13
    assert all(abs(b-a-2.54) < 1e-6 for a,b in zip(row,row[1:]))
assert len(switches) == 12 and len(mounts) == 4
assert controller.GetLayer() == pcb.B_Cu and display.GetLayer() == pcb.B_Cu

usb = {'left': controller.GetPosition().x/1e6-3.81,
       'right': controller.GetPosition().x/1e6+3.556,
       'top': controller.GetPosition().y/1e6-18.034,
       'bottom': controller.GetPosition().y/1e6-16.51}
assert usb['bottom'] <= ymin + 1e-5
for fp in mounts:
    x,y = xy(fp.GetPosition())
    assert xmin < x < xmin+units['board_w'] and ymin < y < ymax

records = []
for fp in footprints:
    records.append({'reference': fp.GetReference(), 'footprint': fp.GetFPID().GetLibItemName(),
                    'position': xy(fp.GetPosition()), 'angle': fp.GetOrientationDegrees(),
                    'side': 'B' if fp.GetLayer() == pcb.B_Cu else 'F',
                    'pads': [{'number': p.GetNumber(), 'net': p.GetNetname(),
                              'position': xy(p.GetPosition()), 'size': xy(p.GetSize()),
                              'drill': xy(p.GetDrillSize()), 'shape': int(p.GetShape()),
                              'attribute': int(p.GetAttribute())} for p in fp.Pads()]})
report = {'units': units, 'points': points,
          'board': {'xmin': xmin, 'ymin': ymin, 'width': units['board_w'], 'height': units['board_h']},
          'usb_envelope_from_library': usb, 'footprints': records,
          'accepted_header_clearances': collisions,
          'status': 'Review draft; accepted collisions retained; assembled heights unverified.'}
(OUT/'geometry.json').write_text(json.dumps(report, indent=2, default=str)+'\n')
with (OUT/'pin-map.csv').open('w') as f:
    writer = csv.writer(f)
    writer.writerow(['Component', 'Pad', 'Net'])
    for fp in footprints:
        for p in fp.Pads():
            if p.GetNetname(): writer.writerow([fp.GetReference(), p.GetNumber(), p.GetNetname()])

target = OUT/'braille_review_unrouted.kicad_pcb'
pcb.SaveBoard(str(target), board)
assert pcb.ExportSpecctraDSN(board, str(OUT/'braille_review.dsn'))
print(f'KiCad opened and saved the board; {len(footprints)} footprints; 26 controller sockets.')
print(f'Accepted header/shaft clearances below 0.25 mm: {len(collisions)}; minimum '
      f'{min(x["edge_clearance_mm"] for x in collisions):.3f} mm.')
print('USB envelope is outside the main PCB. Routing exchange and review geometry written.')
