#!/bin/sh
set -eu
repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
kicad_cli=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
kicad_python=${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9}
stage=$(mktemp -d "${TMPDIR:-/tmp}/qbf-modular-render.XXXXXX")
trap 'rm -rf "$stage"' EXIT HUP INT TERM
"$kicad_python" "$repo_root/modular-case/prepare_views.py" "$stage"
for view in assembled inspection joined protected solo_closed; do
    "$kicad_cli" pcb render --width 2000 --height 1100 --background opaque --quality high --floor --rotate 315,0,12 --zoom 1.05 --output "$repo_root/modular-case/generated/$view.png" "$stage/$view.kicad_pcb" > "$stage/$view.log" 2>&1 || { cat "$stage/$view.log"; exit 1; }
    printf 'Rendered %s\n' "$view"
done
