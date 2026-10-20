#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
workspace=$(CDPATH= cd "${1:?Pass the ZMK workspace directory}" && pwd)
output=${QBF_FIRMWARE_OUTPUT:-$repo_root/ergogen-kikad/generated/firmware}
mkdir -p "$output"
cd "$workspace"
west build -s "$workspace/app" -d "$output/build" -b xiao_ble//zmk -- \
    -DSHIELD=qbf_macropad -DZMK_CONFIG="$repo_root/ergogen-kikad/config" \
    -DZMK_EXTRA_MODULES="$repo_root/ergogen-kikad/config/module"
cp "$output/build/zephyr/zmk.uf2" "$output/qbf_macropad.uf2"
git -C "$workspace/app" rev-parse HEAD > "$output/zmk-revision.txt"
