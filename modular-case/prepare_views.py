import json
import sys
from pathlib import Path
import pcbnew as pcb

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from attach_models import attach_modular_case_models
C=json.loads((ROOT/'ergogen-kikad/generated/assembly-contract.json').read_text())
P=json.loads((ROOT/'modular-case/parameters.json').read_text())
OUT=ROOT/'modular-case/generated'
stage=Path(sys.argv[1])
origin=C['origin_kicad']
inventory={}
for name in ('assembled','inspection','joined','protected','solo_closed'):
    board=pcb.LoadBoard(str(ROOT/'ergogen-kikad/generated/pcbs/macropad.kicad_pcb'))
    visible=[]
    hidden=[]
    for fp in board.GetFootprints():
        models=list(fp.Models())
        fp.Models().clear()
        for model in models:
            model.m_Filename=model.m_Filename.replace('${KIPRJMOD}/../../design/models/',str(ROOT/'ergogen-kikad/design/models')+'/')
            model.m_Show=not (name=='inspection' and 'mbk_' in model.m_Filename)
            key=fp.GetReference()+'/'+Path(model.m_Filename).name
            if not fp.GetReference().startswith('H'):
                (visible if model.m_Show else hidden).append(key)
            fp.Models().append(model)
    attach_modular_case_models(board,OUT,origin,cover=name in ('protected','solo_closed'))
    if name in ('joined','protected'):
        center=pcb.VECTOR2I(round((origin[0]+49.25)*1e6),round((origin[1]-48)*1e6))
        delta=pcb.VECTOR2I(round((97.7+P['joined_gap'])*1e6),0)
        for item in [*board.GetFootprints(),*board.GetDrawings(),*board.GetTracks(),*board.Zones()]:
            try:
                duplicate=item.Duplicate(False)
            except TypeError:
                duplicate=item.Duplicate()
            duplicate.Rotate(center,pcb.EDA_ANGLE(180,pcb.DEGREES_T))
            duplicate.Move(delta)
            if isinstance(duplicate,pcb.FOOTPRINT):
                duplicate.SetReference(duplicate.GetReference()+'_R')
            board.Add(duplicate)
        attach_modular_case_models(board,OUT,origin,only_bridge=True)
    inventory[name]={'visible_keyboard_models':sorted(visible),'hidden_keyboard_models':sorted(hidden),'case_models':[Path(m.m_Filename).name for f in board.GetFootprints() if f.GetReference().startswith('CASE_') for m in f.Models()]}
    pcb.SaveBoard(str(stage/(name+'.kicad_pcb')),board)
a=set(inventory['assembled']['visible_keyboard_models'])
b=set(inventory['inspection']['visible_keyboard_models'])
expected={m for m in a if '/mbk_' in m}
assert len(expected)==10 and a-b==expected and not b-a
assert len([m for m in b if 'choc_reference' in m])==10
assert inventory['assembled']['case_models']==inventory['inspection']['case_models']
assert any('baseplate_native' in m for m in b)
inventory['verified']=True
(OUT/'preview-components.json').write_text(json.dumps(inventory,indent=2)+'\n')
print('Native previews preserve all parts; inspection removes exactly ten caps')
