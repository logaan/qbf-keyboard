import json
import hashlib
import sys
from pathlib import Path
import pcbnew as pcb

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=Path(sys.argv[1])
geometry=json.loads((OUTPUT/'board_geometry.json').read_text())
spec=json.loads((ROOT/'ergogen-kikad/design/assembly.json').read_text())
origin=geometry['assembly_origin_kicad']
board=pcb.LoadBoard(str(OUTPUT/'pcbs/macropad.kicad_pcb'))


def fixed(p):
    return [round(pcb.ToMM(p.x)-origin[0],6),round(origin[1]-pcb.ToMM(p.y),6)]


def polygon(bounds):
    x0,y0,x1,y1=bounds
    p=pcb.SHAPE_POLY_SET();p.NewOutline()
    for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:p.Append(pcb.FromMM(x+origin[0]),pcb.FromMM(origin[1]-y))
    return p


rf=polygon(spec['module']['rf_keepout_bounds'])
violations=[];tested=0
for layer in [pcb.F_Cu,pcb.B_Cu]:
    for item in [*board.GetTracks(),*[p for f in board.GetFootprints() for p in f.Pads()]]:
        if not item.IsOnLayer(layer):continue
        shape=pcb.SHAPE_POLY_SET()
        item.TransformShapeToPolygon(shape,layer,0,pcb.FromMM(.002),pcb.ERROR_OUTSIDE)
        shape.BooleanIntersection(rf);tested+=1
        if shape.Area()>1:violations.append(type(item).__name__)
    for zone in board.Zones():
        if zone.GetIsRuleArea() or not zone.IsOnLayer(layer):continue
        shape=pcb.SHAPE_POLY_SET(zone.GetFilledPolysList(layer));shape.BooleanIntersection(rf);tested+=1
        if shape.Area()>1:violations.append('filled copper zone')
if violations:raise RuntimeError('Copper enters the RF keepout: '+str(violations))
footprints=[]
for f in board.GetFootprints():
    footprints.append({'reference':f.GetReference(),'value':f.GetValue(),'center':fixed(f.GetPosition()),'rotation':f.GetOrientationDegrees(),
                       'pads':[{'number':p.GetNumber(),'net':p.GetNetname(),'center':fixed(p.GetPosition()),'size':[pcb.ToMM(p.GetSize().x),pcb.ToMM(p.GetSize().y)]} for p in f.Pads()],
                       'models':[m.m_Filename for m in f.Models()]})
source=ROOT/'ergogen-kikad/design/sources/XIAO-Plus.kicad_pcb'
module=pcb.LoadBoard(str(source));u4=next(f for f in module.GetFootprints() if f.GetReference()=='U4');center=u4.GetPosition()
contacts=[]
for p in u4.Pads():
    x,y=pcb.ToMM(p.GetPosition().x-center.x),pcb.ToMM(center.y-p.GetPosition().y)
    if abs(abs(y)-8.89)<.01:contacts.append({'number':p.GetNumber(),'center':[x,y],'copper_diameter':pcb.ToMM(p.GetSize().x),'drill':pcb.ToMM(p.GetDrillSize().x)})
assert len(contacts)==23,len(contacts)
assert hashlib.sha256(source.read_bytes()).hexdigest()==spec['sources']['module_pcb_sha256']
schematic=source.with_suffix('.kicad_sch')
assert hashlib.sha256(schematic.read_bytes()).hexdigest()==spec['sources']['module_schematic_sha256']
base=pcb.LoadBoard(str(OUTPUT/'pcbs/baseplate.kicad_pcb'))
assert not list(base.GetTracks()) and not list(base.Zones())
assert all(p.GetAttribute()==pcb.PAD_ATTRIB_NPTH for f in base.GetFootprints() for p in f.Pads())
assert abs(pcb.ToMM(board.GetDesignSettings().GetBoardThickness())-1.6)<.001
assert abs(pcb.ToMM(base.GetDesignSettings().GetBoardThickness())-1.6)<.001
report={'footprints':footprints,'native_module_castellations':contacts,'rf_copper_objects_checked':tested,'rf_copper_intersections':0,'baseplate_copper_objects':0,'baseplate_npth_count':sum(1 for f in base.GetFootprints() for p in f.Pads()),'source_pcb_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
(OUTPUT/'checks/assembly-board.json').write_text(json.dumps(report,indent=2)+'\n')
print('Native copper audit passed; all 23 module castellations captured')
