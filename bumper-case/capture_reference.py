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
    manifest = {'coordinate_system': 'millimetres, origin at PCB lower left, PCB top z=0',
                'source_files': {}, 'footprints': [], 'width': 114.25, 'height': 55.0,
                'pcb_thickness': 1.6, 'origin_kicad': [152.875, 176.0]}
    for name in ('macropad', 'baseplate'):
        source = SOURCES / f'{name}.kicad_pcb'
        manifest['source_files'][str(source.relative_to(REPO))] = hashlib.sha256(source.read_bytes()).hexdigest()
    board = pcb.LoadBoard(str(SOURCES / 'macropad.kicad_pcb'))
    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        entry = {'reference': fp.GetReference(), 'x': round(pcb.ToMM(fp.GetPosition().x) - 152.875, 6),
                 'y': round(176 - pcb.ToMM(fp.GetPosition().y), 6), 'rotation': fp.GetOrientationDegrees(),
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
