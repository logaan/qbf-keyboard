#!/bin/sh
set -eu
export PYTHONDONTWRITEBYTECODE=1

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
kicad_python=${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9}
if [ ! -x "$kicad_python" ]; then
    kicad_python=python3
fi
exec "$kicad_python" "$repo_root/scripts/route_board.py" "$@"
