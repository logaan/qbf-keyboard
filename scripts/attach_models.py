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
        reference = footprint.GetReference()
        if reference.startswith('S'):
            add_model(footprint, 'choc_reference.wrl')
            add_model(footprint, 'mbk_15u.wrl')
        elif reference.startswith('MCU'):
            add_model(footprint, 'nice_nano_reference.wrl', rotation=(0, 0, 180))
        elif reference.startswith('LCD'):
            add_model(footprint, 'nice_view_reference.wrl')
            add_model(footprint, 'display_socket.wrl')
        elif reference.startswith('BAT'):
            add_model(footprint, 'battery_301055.wrl')
        elif reference.startswith('PWR'):
            add_model(footprint, 'Button_Switch_THT.3dshapes/SW_Slide_SPDT_Straight_CK_OS102011MS2Q.step', standard=True)
        elif reference.startswith('RST'):
            add_model(footprint, 'Button_Switch_THT.3dshapes/SW_PUSH_6mm_H4.3mm.step', offset=(-3.25, 2.25, 0), standard=True)
        elif reference == 'J1':
            add_model(footprint, 'Connector_JST.3dshapes/JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal.step', offset=(-1, 0, 0), standard=True)
            add_model(footprint, 'battery_plug_reference.wrl')


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
                if 'mbk_15u' in model.m_Filename or 'nice_view_reference' in model.m_Filename:
                    model.m_Show = False
                model.m_Filename = model.m_Filename.replace(LOCAL, str(ROOT / 'ergogen-kikad/design/models') + '/')
                footprint.Models().append(model)
        pcb.SaveBoard(str(args.inspection), board)
    else:
        attach_models(board)
        pcb.SaveBoard(str(args.source), board)


if __name__ == '__main__':
    main()
