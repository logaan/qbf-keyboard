"""Export module placement PCBs to Freerouting, import sessions, and run KiCad DRC.

Requires KiCad 9 pcbnew, Freerouting 2.2.4 and Java 25+. This does not
resolve DRC or mechanical conflicts; never treat the outputs as fabrication-ready.
"""
import argparse
from pathlib import Path
import subprocess
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1] / 'kicad'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jar', type=Path, help='Freerouting JAR (omit with --import-only)')
parser.add_argument('--java', default='java', help='Java 25+ executable')
parser.add_argument('--import-only', action='store_true')
parser.add_argument('--timeout', type=int, default=240)
args = parser.parse_args()
if not args.import_only and (args.jar is None or not args.jar.is_file()):
    parser.error('Provide --jar or --import-only')
for name in ('module2', 'module3'):
    source = ROOT / f'{name}_placement.kicad_pcb'
    dsn, ses = ROOT / f'{name}.dsn', ROOT / f'{name}.ses'
    board = pcb.LoadBoard(str(source))
    if not args.import_only:
        if not pcb.ExportSpecctraDSN(board, str(dsn)):
            raise RuntimeError(f'Export failed: {name}')
        with (ROOT / f'{name}-routing.log').open('w') as log:
            subprocess.run([args.java, '-Xmx850m', '-jar', str(args.jar),
                            '-de', str(dsn), '-do', str(ses), '-mp', '2'],
                           cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                           timeout=args.timeout, check=True)
    if not pcb.ImportSpecctraSES(board, str(ses)):
        raise RuntimeError(f'Import failed: {name}')
    routed = ROOT / f'{name}_routed.kicad_pcb'
    pcb.SaveBoard(str(routed), board)
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'report',
                    '--severity-all', '-o', str(ROOT / f'{name}-routed-drc.txt'),
                    str(routed)], check=True)
    print(f'{name}: {len(list(board.GetTracks()))} copper items; see {name}-routed-drc.txt')
