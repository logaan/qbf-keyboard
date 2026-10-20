#!/bin/sh
set -eu
repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
freecad_python=${FREECAD_PYTHON:-/Applications/FreeCAD.app/Contents/Resources/bin/python}
freecad_lib=${FREECAD_LIB:-/Applications/FreeCAD.app/Contents/Resources/lib}
export PYTHONPATH="$freecad_lib${PYTHONPATH:+:$PYTHONPATH}"
export QT_QPA_PLATFORM=offscreen
"$freecad_python" "$repo_root/modular-case/render_parts.py"
"$freecad_python" "$repo_root/modular-case/draw.py"
"$freecad_python" "$repo_root/scripts/render_svg.py" "$repo_root/modular-case/generated/dimensions.svg"
"$freecad_python" "$repo_root/modular-case/package.py"
