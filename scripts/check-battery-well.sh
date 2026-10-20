#!/bin/sh
set -eu
repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
output=${1:-$repo_root/ergogen-kikad/generated}
kicad_cli=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
freecad_python=${FREECAD_PYTHON:-/Applications/FreeCAD.app/Contents/Resources/bin/python}
freecad_lib=${FREECAD_LIB:-/Applications/FreeCAD.app/Contents/Resources/lib}
stage=$(mktemp -d "${TMPDIR:-/tmp}/qbf-well.XXXXXX")
trap 'rm -rf "$stage"' EXIT HUP INT TERM
origin=$(/usr/bin/python3 - "$output/board_geometry.json" <<'PYCODE'
import json
import sys
origin = json.load(open(sys.argv[1]))['origin_kicad']
print(f'{origin[0]}x{origin[1]}mm')
PYCODE
)
for board in macropad baseplate; do
    "$kicad_cli" pcb export step --force --board-only --user-origin "$origin" --output "$stage/$board.step" "$output/pcbs/$board.kicad_pcb" > "$stage/$board.log" 2>&1 || { cat "$stage/$board.log"; exit 1; }
done
export PYTHONPATH="$freecad_lib${PYTHONPATH:+:$PYTHONPATH}"
export QT_QPA_PLATFORM=offscreen
"$freecad_python" "$repo_root/scripts/check_battery_well.py" "$output" "$stage"
