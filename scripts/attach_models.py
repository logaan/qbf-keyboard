from pathlib import Path
import argparse

import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
LOCAL = '${KIPRJMOD}/../../design/models/'
STANDARD = '${KICAD10_3DMODEL_DIR}/'


def add_model(footprint, name, offset=(0, 0, 0), rotation=(0, 0, 0), standard=False):
    if not standard and not (ROOT / 'ergogen-kikad/design/models' / name).exists():
        raise RuntimeError('Missing assembly model; run ./scripts/build-3d-models.sh')
    model = pcb.FP_3DMODEL()
    model.m_Filename = (STANDARD if standard else LOCAL) + name
    model.m_Offset = pcb.VECTOR3D(*offset)
    model.m_Rotation = pcb.VECTOR3D(*rotation)
    model.m_Scale = pcb.VECTOR3D(1, 1, 1)
    model.m_Show = True
    footprint.Models().append(model)


def attach_models(board):
    for footprint in board.GetFootprints():
        footprint.Models().clear()
        reference=footprint.GetReference()
        if reference.startswith('S'):
            add_model(footprint,'choc_reference.wrl')
            cap='mbk_1u_reference.wrl' if footprint.GetValue()=='Choc v1 1U' else 'mbk_15u.wrl'
            if (ROOT/'ergogen-kikad/design/models'/cap).exists():add_model(footprint,cap)
        elif reference.startswith('MCU'):
            if (ROOT/'ergogen-kikad/design/models/xiao_plus_reference.wrl').exists():add_model(footprint,'xiao_plus_reference.wrl')
        elif reference.startswith('BAT'):
            add_model(footprint,'battery_301055.wrl')
        elif reference.startswith('PWR'):
            add_model(footprint,'Button_Switch_SMD.3dshapes/SW_SPDT_PCM12.step',standard=True)
        elif reference=='J1':
            add_model(footprint,'Connector_JST.3dshapes/JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal.step',standard=True)
            if (ROOT/'ergogen-kikad/design/models/jst_sh_plug_allowance.wrl').exists():add_model(footprint,'jst_sh_plug_allowance.wrl')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('--inspection', type=Path)
    args = parser.parse_args()
    board = pcb.LoadBoard(str(args.source))
    if args.inspection:
        for footprint in board.GetFootprints():
            models = list(footprint.Models())
            footprint.Models().clear()
            for model in models:
                if 'mbk_' in model.m_Filename:
                    model.m_Show = False
                model.m_Filename = model.m_Filename.replace(LOCAL, str(ROOT / 'ergogen-kikad/design/models') + '/')
                footprint.Models().append(model)
        pcb.SaveBoard(str(args.inspection), board)
    else:
        attach_models(board)
        pcb.SaveBoard(str(args.source), board)


if __name__ == '__main__':
    main()
