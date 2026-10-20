1. Commit as you go.
2. Edit `ergogen-kikad/design/config.yaml` and its footprints; regenerate KiCad boards with `./scripts/generate.sh` while KiCad is closed. The script routes both boards and runs DRC before replacing outputs.
3. After board dimensions or mounts change, run `./scripts/generate-mechanical.sh`.
4. Build firmware with `./scripts/build-firmware.sh /path/to/zmk-workspace`. Keep the ZMK shield and keymap aligned with switch nets. Do not add code comments.
5. Key names are t1–t5 and b1–b5, left to right; column 5 contains the controller. Keep outer cap edges aligned across each row; t5/b5 use landscape 1.5U caps with the same 2.55 mm horizontal cap gap.
6. Keep M2 pairs between columns 1/2 and 3/4 and a third pair between columns 4/5; avoid enlarging the outline for mounts.
7. Keep switches directly wired to GPIO and GND, with no diodes or matrix.
8. Keep the protected 301230 battery envelope between the original switch rows; JST-PH and upward-facing power/reset controls go beside t5/b5. Switch battery positive before nice!nano RAW; reset shorts RST to GND.
9. All user soldering must be through-hole. Use ready-made display modules with documented use in an open-source mechanical keyboard; a README or build guide is sufficient evidence.
