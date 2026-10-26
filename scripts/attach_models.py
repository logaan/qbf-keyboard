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
            add_model(footprint,cap)
        elif reference.startswith('MCU'):
            add_model(footprint,'xiao_plus_reference.wrl')
            add_model(footprint,'xiao_battery_wire.wrl')
            add_model(footprint,'module_support_film.wrl')
            if (ROOT/'ergogen-kikad/design/models/baseplate_native.wrl').exists():
                add_model(footprint,'baseplate_native.wrl',offset=(-87.5,-47.5,0))
        elif reference.startswith('H'):
            add_model(footprint,'m2_low_head_reference.wrl')
        elif reference.startswith('BAT'):
            add_model(footprint,'battery_301055.wrl')
        elif reference.startswith('PWR'):
            add_model(footprint,'Button_Switch_SMD.3dshapes/SW_SPDT_PCM12.step',standard=True)
        elif reference=='J1':
            add_model(footprint,'Connector_JST.3dshapes/JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal.step',standard=True)
            add_model(footprint,'jst_sh_plug_allowance.wrl')




def attach_modular_case_models(board, case_dir, origin, cover=False, bridge=False, only_bridge=False):
    for footprint in board.GetFootprints():
        if footprint.GetReference().startswith('H'):
            footprint.Models().clear()
    names=['bridge'] if only_bridge else ['tray','rim','case_hardware'] + (['cover'] if cover else []) + (['bridge'] if bridge else [])
    for name in names:
        footprint=pcb.FOOTPRINT(board)
        footprint.SetReference('CASE_'+name.upper())
        footprint.SetPosition(pcb.VECTOR2I(round(origin[0]*1e6),round(origin[1]*1e6)))
        footprint.Reference().SetVisible(False)
        footprint.Value().SetVisible(False)
        model=pcb.FP_3DMODEL()
        model.m_Filename=str(case_dir/(name+'.wrl'))
        model.m_Scale=pcb.VECTOR3D(1,1,1)
        model.m_Show=True
        footprint.Models().append(model)
        board.Add(footprint)


def module_instances(spec, name):
    module = spec['modules'][name]
    instances = []
    model_root = ROOT / 'ergogen-kikad/design/models'

    def mesh(label, filename, position, rotation=(0, 0, 0), scale=(1, 1, 1), color=None):
        instances.append({'name': label, 'kind': 'vrml', 'source': str((model_root / filename).relative_to(ROOT)),
                          'position_mm': position, 'rotation_degrees': rotation, 'scale': scale, 'color': color})

    def box(label, size, position, color, radius=0.3):
        instances.append({'name': label, 'kind': 'box', 'size_mm': size, 'position_mm': position, 'color': color, 'bevel_mm': radius})

    for row_index, row in enumerate(module['rows']):
        for column in row['columns']:
            x, y = (column - 1.5) * spec['pitch'], row['y']
            label = f'key_r{row_index + 1}_c{column + 1}'
            mesh(label + '_switch', 'choc_reference.wrl', [x, y, 0], (0, 0, 90))
            large = row['cap'] == 'portrait_1_5u'
            mesh(label + '_cap', 'mbk_15u.wrl' if large else 'mbk_1u_reference.wrl', [x, y, 0],
                 (0, 0, 90 if large else 0), (1, 1, 1) if large else (16.5 / 17.5, 1, 1),
                 [0.68, 0.79, 0.73] if column in (0, 3) else [0.88, 0.85, 0.74])
    mesh('controller', 'nice_nano_reference.wrl', [module.get('controller_x', spec['controller']['x']), module.get('controller_y', spec['controller']['y']), -1.6], (180, 0, module.get('controller_rotation', 0)))
    bottom_display = module.get('display_side', spec['display']['side']) == 'B'
    display_position = [module.get('display_x', 0), module['display_y'], -1.6 if bottom_display else 0]
    display_rotation = (180 if bottom_display else 0, 0, module.get('display_rotation', spec['display']['rotation']) + 90)
    mesh('display', 'nice_view_reference.wrl', display_position, display_rotation)
    mesh('display_socket', 'display_socket.wrl', display_position, display_rotation)
    battery_x, battery_y = module.get('battery_x', spec['battery']['x']), module.get('battery_y', spec['battery']['y'])
    battery_size = list(spec['battery']['size'])
    if module.get('battery_rotation', 0) == 90:
        battery_size[:2] = battery_size[:2][::-1]
    box('protected_battery', battery_size, [battery_x, battery_y, -5.5], [0.65, 0.67, 0.68])
    box('battery_insulator', [battery_size[0] + 0.4, battery_size[1] + 0.4, 0.3], [battery_x, battery_y, -3.85], [0.75, 0.48, 0.08])
    box('power_switch', [6.7, 2.8, 1.4], [0, -34, -2.3], [0.22, 0.23, 0.24])
    box('power_actuator', [2, 2, 1], [0, -36, -2.2], [0.08, 0.09, 0.1])
    box('reset_switch', [3.5, 4.7, 1.8], [-32, -12, -2.5], [0.48, 0.5, 0.51])
    box('reset_actuator', [1.2, 2, 1], [-34.5, -12, -2.5], [0.12, 0.13, 0.14])
    box('battery_connector', [8, 7, 4.8], [module.get('jst_x', 22), module.get('jst_y', 12) - 3, -4], [0.86, 0.86, 0.81])
    preview_height = 13 if bottom_display else 9
    support_height = preview_height - 1.6
    inset = spec['outline']['mount_inset']
    for x in (-spec['outline']['width'] / 2 + inset, spec['outline']['width'] / 2 - inset):
        for y in (-spec['outline']['height'] / 2 + inset, spec['outline']['height'] / 2 - inset):
            instances.append({'name': f'standoff_{x}_{y}', 'kind': 'cylinder', 'radius_mm': 2,
                              'height_mm': support_height, 'position_mm': [x, y, -1.6 - support_height / 2], 'color': [0.55, 0.39, 0.15]})
    if 'trackpad_y' in module:
        x, y = module.get('trackpad_x', 0), module['trackpad_y']
        box('TPS43_module', [43, 40, 0.8], [x, y, 7.6], [0.08, 0.1, 0.11], 1)
        box('TPS43_overlay', [43, 40, 1], [x, y, 8.5], [0.13, 0.17, 0.19], 1.8)
        box('TPS43_adapter_header', [2.54, 15.24, 2.5], [-31, 15.65, -2.85], [0.12, 0.13, 0.14])
        for index, (x, y) in enumerate([(-20, 29), (-20, 24), (-13, 29), (-13, 24)], 1):
            box(f'pullup_{index}', [2, 1.25, 0.55], [x, y, -1.9], [0.12, 0.13, 0.14], 0.05)
    return {'instances': instances, 'preview_pcb_top_z_mm': preview_height, 'limitations': ['PCB and copper are native KiCad exports.',
            '1.5U caps use the retained MBK rendering mesh; switches, controller and display use existing reference meshes.',
            'TPS43, battery, small controls and standoffs are nominal envelopes, not supplier-qualified assembly models.',
            'Preview support heights do not constitute a mechanical design or physical collision validation.']}


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
