#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
output=${1:-$repo_root/ergogen-kikad/generated}
kicad_python=${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9}
if [ ! -x "$kicad_python" ]; then
    kicad_python=python3
fi
"$kicad_python" "$repo_root/scripts/preview_board.py" "$output"
freecad_python=${FREECAD_PYTHON:-/Applications/FreeCAD.app/Contents/Resources/bin/python}
freecad_lib=${FREECAD_LIB:-/Applications/FreeCAD.app/Contents/Resources/lib}
if [ -x "$freecad_python" ]; then
    export PYTHONPATH="$freecad_lib${PYTHONPATH:+:$PYTHONPATH}"
    export QT_QPA_PLATFORM=offscreen
    "$freecad_python" "$repo_root/scripts/render_svg.py" "$output/layout.svg"
fi
