#!/bin/sh
set -eu
repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
freecad_python=${FREECAD_PYTHON:-/Applications/FreeCAD.app/Contents/Resources/bin/python}
freecad_lib=${FREECAD_LIB:-/Applications/FreeCAD.app/Contents/Resources/lib}
export PYTHONPATH="$freecad_lib${PYTHONPATH:+:$PYTHONPATH}"
export QT_QPA_PLATFORM=offscreen
export PYTHONDONTWRITEBYTECODE=1
kicad_cli=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
origin=$(/usr/bin/python3 - "$repo_root/ergogen-kikad/generated/board_geometry.json" <<'PYCODE'
import json
import sys
origin=json.load(open(sys.argv[1]))['assembly_origin_kicad']
print(f'{origin[0]}x{origin[1]}mm')
PYCODE
)
"$kicad_cli" pcb export step --force --board-only --user-origin "$origin" --output "$repo_root/ergogen-kikad/design/models/source/baseplate.step" "$repo_root/ergogen-kikad/generated/pcbs/baseplate.kicad_pcb" > /dev/null 2>&1
"$freecad_python" "$repo_root/scripts/build_3d_models.py"
