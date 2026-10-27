import os
import json
from pathlib import Path
import sys
import uuid
import pcbnew as pcb

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('MODULE1B_OUTPUT',str(ROOT/'boards/module1b/source')))
path=Path(sys.argv[1]) if len(sys.argv)>1 else OUT/'module1b.kicad_pcb'
board=pcb.LoadBoard(str(path))
parts=[]
lib=OUT/'Module1b.pretty';lib.mkdir(exist_ok=True)
rootid=str(uuid.uuid5(uuid.NAMESPACE_URL,'qbf-module1b/root'))
for f in board.GetFootprints():
    ref=f.GetReference()
    parts.append({'reference':ref,'value':f.GetValue(),'footprint':str(f.GetFPID().GetLibItemName()),'uuid':f.m_Uuid.AsString(),'pads':{x.GetNumber():x.GetNetname() for x in f.Pads() if x.GetNumber()},'side':board.GetLayerName(f.GetLayer()),'position':[pcb.ToMM(f.GetPosition().x),pcb.ToMM(f.GetPosition().y)],'angle':f.GetOrientationDegrees()})
    item=parts[-1]
    item['pad_positions']=[{'number':p.GetNumber(),'position':[pcb.ToMM(p.GetPosition().x),pcb.ToMM(p.GetPosition().y)]} for p in f.Pads() if p.GetNumber()]
    center=list(item['position']);method='Footprint package origin; supplier preview required'
    if ref.startswith('S') and ref[1:].isdigit():
        terminals=[p['position'] for p in item['pad_positions'] if p['number'] in ('1','2')]
        center=[sum(p[i] for p in terminals)/len(terminals) for i in (0,1)]
        method='World-coordinate terminal midpoint, matching socket fabrication body center'
    elif ref=='J1':
        center=[80.0026,134.875];method='Bounding-box center of actual exported USB STEP body'
    elif ref=='J2':
        center=[76.4,111.0];method='Housing outline center: local (0,0.6), transformed to actual bottom-side board coordinates'
    item['assembly_center']={'position':center,'method':method,'status':'Candidate; JLC package origin and rotation preview required'}
    f.SetFPID(pcb.LIB_ID('Module1b',ref))
    f.SetPath(pcb.KIID_PATH('/'+rootid+'/'+str(uuid.uuid5(uuid.NAMESPACE_URL,'qbf-module1b/symbol/'+ref))))
    pcb.PCB_IO_MGR.FindPlugin(pcb.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(lib),f)
(OUT/'components.json').write_text(json.dumps(parts,indent=2)+'\n')
pcb.SaveBoard(str(path),board)
