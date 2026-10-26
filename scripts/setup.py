import argparse
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / '.tools'
parser = argparse.ArgumentParser(description='Install project dependencies and check the shared CAD toolchain.')
parser.add_argument('--dependencies-only', action='store_true')
parser.add_argument('--install-system', action='store_true', help='Install Node, KiCad and FreeCAD using Homebrew or apt; may request administrator permission')
args = parser.parse_args()

def run(command):
    subprocess.run(command, cwd=ROOT, check=True)

if args.install_system:
    if platform.system() == 'Darwin' and not shutil.which('brew'):
        if not sys.stdin.isatty() or input('Install Homebrew using its official installer? [y/N] ').lower() != 'y':
            sys.exit('System setup cancelled; no Homebrew installer was run.')
        TOOLS.mkdir(exist_ok=True)
        installer = TOOLS / 'homebrew-install.sh'
        with urllib.request.urlopen('https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh', timeout=60) as response:
            installer.write_bytes(response.read())
        run(['/bin/bash', str(installer)])
    if shutil.which('brew'):
        run(['brew', 'install', 'node', 'python@3.12'])
        run(['brew', 'install', '--cask', 'kicad', 'freecad', 'blender'])
    elif shutil.which('apt-get'):
        run(['sudo', 'apt-get', 'update'])
        run(['sudo', 'apt-get', 'install', '-y', 'nodejs', 'npm', 'python3-venv', 'python3-yaml', 'kicad', 'freecad', 'blender'])
    else:
        sys.exit('No supported package manager found. Install Homebrew on macOS or use an apt-based Linux system, then reopen setup.sh.')
if not shutil.which('npm') or not shutil.which('node'):
    sys.exit('Node.js is missing. Reopen scripts/setup.sh with --install-system, or select setup in scripts/boards.sh.')
major = int(subprocess.check_output(['node', '-p', 'process.versions.node.split(".")[0]'], text=True))
if major < 20:
    sys.exit('Node.js 20 or newer is required. Use setup.sh --install-system to update the system tools.')
TOOLS.mkdir(exist_ok=True)
lock = ROOT / 'package-lock.json'
digest = hashlib.sha256(lock.read_bytes() + (ROOT / 'package.json').read_bytes()).hexdigest()
stamp = TOOLS / 'npm.sha256'
if not (ROOT / 'node_modules/.bin/ergogen').exists() or not stamp.exists() or stamp.read_text() != digest:
    run(['npm', 'ci', '--ignore-scripts', '--allow-remote=all', '--cache', str(TOOLS / 'npm-cache')])
    stamp.write_text(digest)
venv = TOOLS / 'venv'
python = venv / 'bin/python'
if not python.exists():
    interpreter = sys.executable
    if not (3, 9) <= sys.version_info[:2] <= (3, 12):
        candidates = [shutil.which('python3.12'), '/usr/bin/python3', '/opt/homebrew/opt/python@3.12/bin/python3.12', '/usr/local/opt/python@3.12/bin/python3.12']
        interpreter = None
        for candidate in candidates:
            if not candidate or not Path(candidate).is_file():
                continue
            version = subprocess.check_output([candidate, '-c', 'import sys; print(sys.version_info.major, sys.version_info.minor)'], text=True).split()
            if (3, 9) <= tuple(map(int, version)) <= (3, 12):
                interpreter = candidate
                break
        if interpreter is None:
            sys.exit('Python 3.9–3.12 is required for the pinned dependencies. Select system-tool installation in scripts/start.command.')
    run([interpreter, '-m', 'venv', str(venv)])
requirements = ROOT / 'scripts/requirements.txt'
digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
stamp = TOOLS / 'python.sha256'
if not stamp.exists() or stamp.read_text() != digest:
    run([str(python), '-m', 'pip', 'install', '-r', str(requirements)])
    stamp.write_text(digest)
if not args.dependencies_only:
    cli = os.environ.get('KICAD_CLI') or shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
    if not Path(cli).is_file():
        sys.exit('Dependencies ready; KiCad is missing. Use setup.sh --install-system to install CAD tools.')
    version = subprocess.check_output([cli, 'version'], text=True).strip()
    if version.split('.')[0] != '10':
        sys.exit(f'KiCad 10 is required for all boards; found {version}. Update KiCad before continuing.')
    print(f'KiCad {version}; Node {major}; dependencies ready on {platform.system()}.')
