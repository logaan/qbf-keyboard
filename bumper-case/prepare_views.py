from pathlib import Path
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
    for name in ('assembled', 'inspection', 'exploded'):
        board = pcb.LoadBoard(str(source))
        for fp in board.GetFootprints():
            models = list(fp.Models())
            fp.Models().clear()
            for model in models:
                model.m_Filename = model.m_Filename.replace('${KIPRJMOD}/../../design/models/', str(REPO / 'ergogen-kikad/design/models') + '/')
                if name != 'assembled' and ('mbk_15u' in model.m_Filename or 'nice_view_reference' in model.m_Filename):
                    model.m_Show = False
                fp.Models().append(model)
        for part in ('left_bumper', 'right_bumper'):
            offset = (0, 0, 18 if name == 'exploded' else 0)
            add_model(board, ROOT / 'generated' / (part + '.wrl'), part.upper(), offset=offset)
        for item in ('baseplate', 'fasteners', 'feet'):
            if name == 'exploded' and item == 'fasteners':
                continue
            add_model(board, stage / (item + '.wrl'), item.upper())
        pcb.SaveBoard(str(stage / (name + '.kicad_pcb')), board)
    print('Prepared temporary assembly views; the original PCB and case CAD files are unchanged')


if __name__ == '__main__':
    main()
