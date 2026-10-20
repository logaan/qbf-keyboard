#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
output=${1:-$repo_root/ergogen-kikad/generated}
kicad_cli=${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
if [ ! -x "$kicad_cli" ]; then
    kicad_cli=kicad-cli
fi
mkdir -p "$output/checks"
for board in macropad baseplate; do
    "$kicad_cli" pcb drc --exit-code-violations --output "$output/checks/$board.rpt" "$output/pcbs/$board.kicad_pcb"
done
