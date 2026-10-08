#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
project_dir="$repo_root/ergogen-kikad"
pcb_dir="$project_dir/generated/pcbs"

if [ -e "$pcb_dir/~macropad.kicad_pcb.lck" ] || [ -e "$pcb_dir/~macropad.kicad_pro.lck" ] || \
   [ -e "$pcb_dir/~baseplate.kicad_pcb.lck" ] || [ -e "$pcb_dir/~baseplate.kicad_pro.lck" ]; then
    printf '%s\n' 'Close the KiCad PCB editor before regenerating the boards.' >&2
    exit 1
fi

cd "$project_dir"
npm ci --allow-git=all --cache "$project_dir/.npm-cache"
npm run generate
