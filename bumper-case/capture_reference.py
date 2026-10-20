from pathlib import Path
import hashlib
import json

import pcbnew as pcb

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
OUT = ROOT / 'reference'
SOURCES = REPO / 'ergogen-kikad/generated/pcbs'


def main():
    OUT.mkdir(exist_ok=True)
    geometry_path = REPO / 'ergogen-kikad/generated/board_geometry.json'
    geometry = json.loads(geometry_path.read_text())
    origin = geometry['assembly_origin_kicad']
    manifest = {'coordinate_system': 'millimetres, fixed switch-layout datum, main PCB top z=0; pcb_bounds_mm records the enlarged outline',
                'source_files': {}, 'footprints': [], 'width': 114.25, 'height': 55.0,
                'pcb_thickness': 1.6, 'origin_kicad': origin,
                'pcb_bounds_mm': geometry['assembly_bounds_mm'],
                'pcb_width': geometry['width'], 'pcb_height': geometry['height']}
    manifest['source_files'][str(geometry_path.relative_to(REPO))] = hashlib.sha256(geometry_path.read_bytes()).hexdigest()
    spec_path = REPO / 'ergogen-kikad/design/battery.json'
    manifest['battery'] = json.loads(spec_path.read_text())
    manifest['source_files'][str(spec_path.relative_to(REPO))] = hashlib.sha256(spec_path.read_bytes()).hexdigest()
    for name in ('macropad', 'baseplate'):
        source = SOURCES / f'{name}.kicad_pcb'
        manifest['source_files'][str(source.relative_to(REPO))] = hashlib.sha256(source.read_bytes()).hexdigest()
    board = pcb.LoadBoard(str(SOURCES / 'macropad.kicad_pcb'))
    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        entry = {'reference': fp.GetReference(), 'x': round(pcb.ToMM(fp.GetPosition().x) - origin[0], 6),
                 'y': round(origin[1] - pcb.ToMM(fp.GetPosition().y), 6), 'rotation': fp.GetOrientationDegrees(),
                 'models': []}
        for model in fp.Models():
            path = model.m_Filename
            record = {'filename': path, 'offset': [model.m_Offset.x, model.m_Offset.y, model.m_Offset.z],
                      'rotation': [model.m_Rotation.x, model.m_Rotation.y, model.m_Rotation.z],
                      'scale': [model.m_Scale.x, model.m_Scale.y, model.m_Scale.z]}
            if path.endswith('.wrl'):
                source = REPO / 'ergogen-kikad/design/models' / Path(path).name
                manifest['source_files'][str(source.relative_to(REPO))] = hashlib.sha256(source.read_bytes()).hexdigest()
                record['source_path'] = str(source.relative_to(REPO))
            entry['models'].append(record)
        manifest['footprints'].append(entry)
    (OUT / 'placements.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Captured current KiCad component placements and source hashes; no assembly geometry embedded')


if __name__ == '__main__':
    main()
