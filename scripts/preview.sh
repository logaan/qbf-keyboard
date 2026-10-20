#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
output=${1:-$repo_root/ergogen-kikad/generated}
kicad_cli=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
if [ ! -x "$kicad_cli" ]; then
    kicad_cli=kicad-cli
fi
"$kicad_cli" pcb export svg --layers F.Fab,F.SilkS,Dwgs.User,Cmts.User,Edge.Cuts --sketch-pads-on-fab-layers --page-size-mode 2 --exclude-drawing-sheet --mode-single --output "$output/layout.svg" "$output/pcbs/macropad.kicad_pcb"
"$kicad_cli" pcb export svg --layers F.Cu,B.Cu,F.SilkS,Dwgs.User,Cmts.User,Edge.Cuts --page-size-mode 2 --exclude-drawing-sheet --mode-single --output "$output/routing.svg" "$output/pcbs/macropad.kicad_pcb"
freecad_python=${FREECAD_PYTHON:-/Applications/FreeCAD.app/Contents/Resources/bin/python}
freecad_lib=${FREECAD_LIB:-/Applications/FreeCAD.app/Contents/Resources/lib}
if [ -x "$freecad_python" ]; then
    export PYTHONPATH="$freecad_lib${PYTHONPATH:+:$PYTHONPATH}"
    export QT_QPA_PLATFORM=offscreen
    "$freecad_python" "$repo_root/scripts/render_svg.py" "$output/layout.svg"
    "$freecad_python" "$repo_root/scripts/render_svg.py" "$output/routing.svg"
fi
