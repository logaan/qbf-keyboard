#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
project_dir="$repo_root/ergogen-kikad"
pcb_dir="$project_dir/generated/pcbs"

check_locks() {
    for board in macropad baseplate; do
        for extension in kicad_pcb kicad_pro; do
            if [ -e "$pcb_dir/~$board.$extension.lck" ]; then
                printf '%s\n' 'Close the KiCad PCB editor before regenerating the boards.' >&2
                exit 1
            fi
        done
    done
}

check_locks
stage=$(mktemp -d "${TMPDIR:-/tmp}/qbf-generate.XXXXXX")
trap 'rm -rf "$stage"' EXIT HUP INT TERM
cd "$project_dir"
if [ ! -x node_modules/.bin/ergogen ] || [ package-lock.json -nt node_modules/.package-lock.json ]; then
    npm ci --allow-git=all --cache "$project_dir/.npm-cache"
fi
node_modules/.bin/ergogen design --output "$stage"
"$repo_root/scripts/route.sh" --output "$stage"
for board in macropad baseplate; do
    if [ -f "$pcb_dir/$board.kicad_pro" ]; then
        cp "$pcb_dir/$board.kicad_pro" "$stage/pcbs/"
    fi
done
if ! "$repo_root/scripts/check.sh" "$stage"; then
    mkdir -p "$project_dir/generated/checks"
    cp "$stage/checks/"*.rpt "$project_dir/generated/checks/"
    exit 1
fi
"$repo_root/scripts/preview.sh" "$stage"
check_locks
mkdir -p "$project_dir/generated/outlines" "$project_dir/generated/checks" "$pcb_dir"
cp "$stage/board_geometry.json" "$stage/layout.svg" "$project_dir/generated/"
if [ -f "$stage/layout.png" ]; then
    cp "$stage/layout.png" "$project_dir/generated/"
fi
cp "$stage/outlines/board.dxf" "$project_dir/generated/outlines/"
cp "$stage/pcbs/macropad.kicad_pcb" "$stage/pcbs/baseplate.kicad_pcb" "$pcb_dir/"
cp "$stage/checks/macropad.rpt" "$stage/checks/baseplate.rpt" "$project_dir/generated/checks/"
