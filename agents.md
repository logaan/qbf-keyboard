1. Commit as you go.
2. Edit `ergogen-kikad/design/config.yaml` and its footprints; regenerate KiCad boards with `./scripts/generate.sh` while KiCad is closed. The script routes all three boards and runs DRC before replacing outputs.
3. After board dimensions or mounts change, run `./scripts/generate-mechanical.sh`.
4. Build firmware with `./scripts/build-firmware.sh /path/to/zmk-workspace`. Keep the ZMK shield and keymap aligned with switch nets. Do not add code comments.
5. Key names are t1–t5 and b1–b5, left to right; column 5 contains the controller. Keep outer cap edges aligned across each row.
6. Put the four M2 holes between switch columns 1/2 and 3/4, not in an outer border.
7. Keep switches directly wired to GPIO and GND, with no diodes or matrix.
