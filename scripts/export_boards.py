import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

from modules import check
from toolchain import kicad_cli

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description='Export checked PCB fabrication review bundles; physical release approval is separate.')
parser.add_argument('board', nargs='?', choices=['all', 'qbf', 'module1', 'module2', 'module3'], default='all')
args = parser.parse_args()
selected = ['qbf', 'module1', 'module2', 'module3'] if args.board == 'all' else [args.board]
cli = kicad_cli()
for name in selected:
    if name == 'qbf':
        subprocess.run([str(ROOT / 'scripts/check.sh')], check=True)
        folder = ROOT / 'ergogen-kikad/generated'
        boards = [folder / 'pcbs' / f'{part}.kicad_pcb' for part in ('macropad', 'baseplate')]
    else:
        check(name)
        folder = ROOT / 'boards/modules/generated' / name
        boards = [folder / 'pcbs' / f'{name}.kicad_pcb']
    with tempfile.TemporaryDirectory(prefix='qbf-export-') as temporary:
        stage = Path(temporary)
        for board in boards:
            target = stage / board.stem
            target.mkdir()
            subprocess.run([cli, 'pcb', 'export', 'gerbers', '--check-zones', '--layers',
                            'F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts', '-o', str(target) + '/', str(board)], check=True)
            subprocess.run([cli, 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-separate-th', '--generate-map',
                            '--map-format', 'svg', '-o', str(target) + '/', str(board)], check=True)
        if name != 'qbf':
            electrical = json.loads((folder / 'electrical.json').read_text())
            with (stage / 'pin-map.csv').open('w') as stream:
                writer = csv.writer(stream, lineterminator='\n')
                writer.writerow(['Reference', 'Pad', 'Net', 'Side'])
                for footprint in electrical['footprints']:
                    for pad, net in footprint['pads'].items():
                        writer.writerow([footprint['reference'], pad, net, footprint['side']])
            spec = json.loads((ROOT / 'boards/modules/design.json').read_text())
            module = spec['modules'][name]
            bom = {'status': 'procurement review required', 'controller': spec['controller']['part'],
                   'display': spec['display']['part'], 'switches': {'part': 'Kailh Choc v1 soldered', 'quantity': len(electrical['keys'])},
                   'battery': spec['battery'], 'keycap_rows': module['rows'], 'keycap_sizes_mm': spec['keycaps'],
                   'footprints': electrical['footprints'], 'trackpad': spec['trackpad'] if 'trackpad_y' in module else None}
            (stage / 'bom.json').write_text(json.dumps(bom, indent=2) + '\n')
        manifest = {'status': 'PCB fabrication review only; not a manufacturing release',
                    'board_sha256': {board.name: hashlib.sha256(board.read_bytes()).hexdigest() for board in boards},
                    'files': {str(p.relative_to(stage)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*')) if p.is_file()},
                    'required_reviews': ['Purchased parts and cable polarity', 'Charging and protected battery specification',
                                         'Antenna clearance', 'Physical assembly stack and component access']}
        (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        destination = folder / 'fabrication-review'
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(stage, destination)
        with zipfile.ZipFile(folder / f'{name}-fabrication-review.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(destination.rglob('*')):
                if path.is_file():
                    archive.write(path, str(path.relative_to(destination)))
    print(f'{name}: checked fabrication review bundle exported; physical release still required')
