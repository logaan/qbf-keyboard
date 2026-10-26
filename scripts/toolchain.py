import os
from pathlib import Path
import shutil
import subprocess
import sys


def kicad_cli():
    executable = os.environ.get('KICAD_CLI') or shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
    version = subprocess.check_output([executable, 'version'], text=True).strip()
    if version.split('.')[0] != '10':
        raise ValueError(f'KiCad 10 is required; found {version}')
    return executable


def kicad_python():
    override = os.environ.get('KICAD_PYTHON')
    if override:
        return override
    mac = Path('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3')
    if mac.exists():
        return str(mac)
    candidates = sorted(Path('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions').glob('*/bin/python3.*'))
    return str(candidates[-1]) if candidates else '/usr/bin/python3'
