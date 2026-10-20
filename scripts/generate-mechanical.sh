#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
freecad_python=${FREECAD_PYTHON:-/Applications/FreeCAD.app/Contents/Resources/bin/python}
freecad_lib=${FREECAD_LIB:-/Applications/FreeCAD.app/Contents/Resources/lib}
if [ ! -x "$freecad_python" ]; then
    freecad_python=python3
fi
if [ -d "$freecad_lib" ]; then
    export PYTHONPATH="$freecad_lib${PYTHONPATH:+:$PYTHONPATH}"
fi
export QT_QPA_PLATFORM=offscreen
exec "$freecad_python" "$repo_root/modular-case/build.py"
