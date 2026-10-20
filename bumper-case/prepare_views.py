from pathlib import Path
import json
import sys

import pcbnew as pcb

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def add_model(board, path, reference, position=(152.875, 176), offset=(0, 0, 0), rotation=(0, 0, 0)):
    fp = pcb.FOOTPRINT(board)
    fp.SetReference(reference)
    fp.SetPosition(pcb.VECTOR2I(round(position[0] * 1e6), round(position[1] * 1e6)))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    model = pcb.FP_3DMODEL()
    model.m_Filename = str(path)
    model.m_Offset = pcb.VECTOR3D(*offset)
    model.m_Rotation = pcb.VECTOR3D(*rotation)
    model.m_Scale = pcb.VECTOR3D(1, 1, 1)
    fp.Models().append(model)
    board.Add(fp)


def main():
    stage = Path(sys.argv[1])
    source = REPO / 'ergogen-kikad/generated/pcbs/macropad.kicad_pcb'
    inventory = {}
    for name in ('assembled', 'inspection', 'exploded'):
        board = pcb.LoadBoard(str(source))
        visible = []
        hidden = []
        for fp in board.GetFootprints():
            models = list(fp.Models())
            fp.Models().clear()
            for model in models:
                model.m_Filename = model.m_Filename.replace('${KIPRJMOD}/../../design/models/', str(REPO / 'ergogen-kikad/design/models') + '/')
                model.m_Show = not (name != 'assembled' and 'mbk_15u' in model.m_Filename)
                key = fp.GetReference() + '/' + Path(model.m_Filename).name
                (visible if model.m_Show else hidden).append(key)
                fp.Models().append(model)
        for part in ('left_bumper', 'right_bumper', 'upper_guard'):
            offset = (0, 0, (32 if part == 'upper_guard' else 18) if name == 'exploded' else 0)
            add_model(board, ROOT / 'generated' / (part + '.wrl'), part.upper(), offset=offset)
        for item in ('baseplate', 'fasteners', 'feet'):
            if name == 'exploded' and item == 'fasteners':
                continue
            add_model(board, stage / (item + '.wrl'), item.upper())
        pcb.SaveBoard(str(stage / (name + '.kicad_pcb')), board)
        inventory[name] = {'visible_keyboard_models': sorted(visible),
                           'hidden_keyboard_models': sorted(hidden),
                           'case_and_hardware': ['left_bumper', 'right_bumper', 'upper_guard', 'baseplate', 'feet']
                           + ([] if name == 'exploded' else ['fasteners'])}
    with_caps = set(inventory['assembled']['visible_keyboard_models'])
    no_caps = set(inventory['inspection']['visible_keyboard_models'])
    expected_hidden = {m for m in with_caps if 'mbk_15u.wrl' in m}
    if len(expected_hidden) != 10 or with_caps - no_caps != expected_hidden or no_caps - with_caps:
        raise RuntimeError('Assembly previews must differ only by the ten keycap models')
    if len([m for m in no_caps if m.endswith('/choc_reference.wrl')]) != 10:
        raise RuntimeError('Cap-free assembly must retain all ten key switches')
    if 'LCD1/nice_view_reference.wrl' not in no_caps:
        raise RuntimeError('Cap-free assembly must retain the display')
    if inventory['assembled']['case_and_hardware'] != inventory['inspection']['case_and_hardware']:
        raise RuntimeError('Both assembly previews must retain the same boards, case, feet and hardware')
    inventory['verified'] = True
    (ROOT / 'generated/preview-components.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print('Prepared temporary assembly views; the original PCB and case CAD files are unchanged')


if __name__ == '__main__':
    main()
