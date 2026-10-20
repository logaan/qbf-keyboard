#!/bin/sh
set -eu
case_root=$(CDPATH= cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$case_root")
kicad_cli=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
kicad_python=${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9}
freecad_python=${FREECAD_PYTHON:-/Applications/FreeCAD.app/Contents/Resources/bin/python}
freecad_lib=${FREECAD_LIB:-/Applications/FreeCAD.app/Contents/Resources/lib}
export PYTHONPATH="$freecad_lib${PYTHONPATH:+:$PYTHONPATH}"
export QT_QPA_PLATFORM=offscreen
assembly_origin=$("$kicad_python" -c 'import json,sys; p=json.load(open(sys.argv[1]))["origin_kicad"]; print(f"{p[0]}x{p[1]}mm")' "$case_root/reference/placements.json")
stage=$(mktemp -d "${TMPDIR:-/tmp}/qbf-bumper.XXXXXX")
trap 'rm -rf "$stage"' EXIT HUP INT TERM
"$kicad_cli" pcb export step --force --user-origin "$assembly_origin" --output "$stage/kicad-assembly.step" "$repo_root/ergogen-kikad/generated/pcbs/macropad.kicad_pcb" > "$stage/assembly-export.log" 2>&1 || {
    if [ ! -s "$stage/kicad-assembly.step" ]; then
        cat "$stage/assembly-export.log"
        exit 1
    fi
}
"$kicad_cli" pcb export step --force --board-only --user-origin "$assembly_origin" --output "$stage/kicad-baseplate.step" "$repo_root/ergogen-kikad/generated/pcbs/baseplate.kicad_pcb" > "$stage/baseplate-export.log" 2>&1
"$freecad_python" "$case_root/check_assembly.py" "$stage"
unset PYTHONPATH
"$kicad_python" "$case_root/prepare_views.py" "$stage" > "$stage/views.log" 2>&1
for view in assembled inspection exploded; do
    "$kicad_cli" pcb render --width 2000 --height 1100 --background opaque --quality high --floor --rotate 315,0,12 --zoom 1.15 --output "$case_root/generated/$view.png" "$stage/$view.kicad_pcb" > "$stage/$view.log" 2>&1 || { cat "$stage/$view.log"; exit 1; }
    printf 'Rendered %s\n' "$view"
done
