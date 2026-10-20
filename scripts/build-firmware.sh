#!/bin/sh
set -eu

repo_root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
workspace=$(CDPATH= cd "${1:?Pass the ZMK workspace directory}" && pwd)
output=${QBF_FIRMWARE_OUTPUT:-$repo_root/ergogen-kikad/generated/firmware}
mkdir -p "$output"
cd "$workspace"
west build -p always -s "$workspace/app" -d "$output/build" -b xiao_ble/nrf52840/zmk -- \
    -DSHIELD=qbf_macropad -DZMK_CONFIG="$repo_root/ergogen-kikad/config"
cp "$output/build/zephyr/zmk.uf2" "$output/qbf_macropad.uf2"
git -c safe.directory="$workspace/app" -C "$workspace/app" rev-parse HEAD > "$output/zmk-revision.txt"

python3 "$repo_root/scripts/check_firmware.py" "$output" "$workspace"
