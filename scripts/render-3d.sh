#!/bin/sh
set -eu
repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
output="$repo_root/ergogen-kikad/generated"
kicad_cli=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
kicad_python=${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9}
stage=$(mktemp -d "${TMPDIR:-/tmp}/qbf-render.XXXXXX")
trap 'rm -rf "$stage"' EXIT HUP INT TERM
"$kicad_cli" pcb render --width 2000 --height 1100 --background opaque --quality high --floor --rotate 315,0,12 --zoom 1.25 --output "$output/assembly-3d.png" "$output/pcbs/macropad.kicad_pcb"
"$kicad_python" "$repo_root/scripts/attach_models.py" "$output/pcbs/macropad.kicad_pcb" --inspection "$stage/inspection.kicad_pcb"
"$kicad_cli" pcb render --width 2000 --height 1100 --background opaque --quality high --floor --rotate 315,0,12 --zoom 1.25 --output "$output/inspection-3d.png" "$stage/inspection.kicad_pcb"
