from pathlib import Path
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
ERGOGEN = REPO / 'ergogen-kikad/node_modules/.bin/ergogen'


def main():
    manifest = {}
    for name in ('five-column-1u', 'five-column-15u'):
        output = ROOT / name
        with tempfile.TemporaryDirectory(prefix='qbf-layout-') as staging:
            design = Path(staging)
            (design / 'config.yaml').write_text((ROOT / (name + '.yaml')).read_text())
            (design / 'footprints').symlink_to(REPO / 'ergogen-kikad/design/footprints', target_is_directory=True)
            subprocess.run([str(ERGOGEN), str(design), '--output', str(output)], check=True)
        subprocess.run([str(REPO / 'scripts/preview.sh'), str(output)], check=True)
        pcb = (output / 'pcbs/macropad.kicad_pcb').read_text()
        switches = []
        for block in re.split(r'\n    \(module ', pcb)[1:]:
            if not block.startswith('PG1350_'):
                continue
            at = re.search(r'\(at ([\d.eE+-]+) ([\d.eE+-]+) ([\d.eE+-]+)\)', block)
            label = re.search(r'fp_text user "([tb]\d)"', block)[1]
            switches.append({'label': label, 'x': float(at[1]), 'y': -float(at[2]), 'rotation': float(at[3]), 'cap': [16.5, 26.5] if float(at[3]) == 90 else [17.5, 16.5]})
        assert len(switches) == 10
        for switch in switches:
            expected = [16.5, 26.5] if name.endswith('15u') and not switch['label'].endswith('5') else [17.5, 16.5]
            assert switch['cap'] == expected, (name, switch)
        rows = sorted({round(switch['y'], 4) for switch in switches})
        expected_pitch = 27.5 if name.endswith('15u') else 19.05
        assert len(rows) == 2 and abs(rows[1] - rows[0] - expected_pitch) < 0.00001
        manifest[name] = {'board_mm': [98, 96 if name.endswith('15u') else 80], 'switches': switches, 'status': 'Provisional Ergogen placement only; unrouted; no fabrication or assembly validation.'}
    (ROOT / 'placements.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
