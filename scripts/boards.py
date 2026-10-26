import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('qbf', 'module1', 'module2', 'module3')


def run(*command):
    subprocess.run([str(c) for c in command], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description='Build and inspect the four keyboards; no npm or Python setup commands required.')
    parser.add_argument('action', nargs='?', choices=['list', 'setup', 'build', 'check', 'preview', 'status', 'firmware', 'mechanical', 'test'])
    parser.add_argument('board', nargs='?', choices=[*NAMES, 'all'], default='all')
    parser.add_argument('--workspace', type=Path)
    args = parser.parse_args()
    if args.action is None:
        if not sys.stdin.isatty():
            parser.print_help()
            return
        actions = ['status', 'setup', 'build', 'check', 'preview', 'test', 'firmware', 'mechanical']
        for i, action in enumerate(actions, 1):
            print(f'{i}. {action}')
        choice = input('Action number [1]: ').strip() or '1'
        args.action = actions[int(choice) - 1]
        if args.action not in ('setup', 'test'):
            print('Boards: ' + ', '.join(NAMES) + ', all')
            args.board = input('Board [all]: ').strip() or 'all'
            if args.board not in (*NAMES, 'all'):
                parser.error('Unknown board')
    if args.action in ('list', 'status'):
        print('qbf: existing routed PCB, firmware and active modular-case; physical validation still required')
        for name in NAMES[1:]:
            path = ROOT / 'boards/modules/generated' / name / 'validation.json'
            status = json.loads(path.read_text()) if path.exists() else {}
            print(f'{name}: {status.get("stage", "not built")}; review {status.get("review", "pending")}; NOT fabrication-ready')
        return
    if args.action == 'setup':
        extra = []
        if sys.stdin.isatty() and input('Install system tools using Homebrew/apt as well? [y/N] ').lower() == 'y':
            extra = ['--install-system']
        run(ROOT / 'scripts/setup.sh', *extra)
        return
    if args.action in ('build', 'check', 'test', 'preview'):
        run(ROOT / 'scripts/setup.sh', *(['--dependencies-only'] if args.action in ('test', 'preview') else []))
        venv = ROOT / '.tools/venv/bin/python'
        if Path(sys.prefix).resolve() != venv.parent.parent.resolve():
            os.execv(str(venv), [str(venv), str(Path(__file__)), *sys.argv[1:]] if len(sys.argv) > 1 else [str(venv), str(Path(__file__)), args.action, args.board])
    if args.action == 'test':
        run(sys.executable, '-m', 'unittest', 'discover', '-s', 'tests')
        return
    selected = NAMES if args.board == 'all' else [args.board]
    failures = []
    for name in selected:
        try:
            if args.action == 'build':
                if name == 'qbf':
                    run(ROOT / 'scripts/generate.sh')
                else:
                    from modules import build
                    build(name)
            elif args.action == 'check':
                if name == 'qbf':
                    run(ROOT / 'scripts/check.sh')
                else:
                    from modules import check
                    check(name)
            elif args.action == 'preview':
                if name != 'qbf':
                    from modules import check
                    check(name)
                path = ROOT / ('ergogen-kikad/generated/layout.svg' if name == 'qbf' else f'boards/modules/generated/{name}/layout.svg')
                if not path.exists():
                    raise ValueError(f'Build {name} first')
                opener = shutil.which('open' if sys.platform == 'darwin' else 'xdg-open')
                if opener:
                    run(opener, path)
                else:
                    print(path)
            elif args.action in ('firmware', 'mechanical'):
                if name != 'qbf':
                    raise ValueError('Blocked: Ergogen layout review, KiCad implementation and review must precede firmware and mechanical work')
                if args.action == 'firmware':
                    if not args.workspace and sys.stdin.isatty():
                        args.workspace = Path(input('Existing ZMK workspace path: ')).expanduser()
                    if not args.workspace:
                        raise ValueError('Select an existing ZMK workspace with --workspace; automated ZMK workspace provisioning remains TODO')
                    run(ROOT / 'scripts/build-firmware.sh', args.workspace.resolve())
                else:
                    run(ROOT / 'scripts/generate-mechanical.sh')
        except (ValueError, OSError, subprocess.CalledProcessError) as error:
            failures.append(f'{name}: {error}')
    if failures:
        sys.exit('\n'.join(failures))


if __name__ == '__main__':
    main()
