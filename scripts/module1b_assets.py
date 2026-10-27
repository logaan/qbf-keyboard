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
    f.SetFPID(pcb.LIB_ID('Module1b',ref))
    f.SetPath(pcb.KIID_PATH('/'+rootid+'/'+str(uuid.uuid5(uuid.NAMESPACE_URL,'qbf-module1b/symbol/'+ref))))
    pcb.PCB_IO_MGR.FindPlugin(pcb.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(lib),f)
(OUT/'components.json').write_text(json.dumps(parts,indent=2)+'\n')
pcb.SaveBoard(str(path),board)
