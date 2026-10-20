1. Commit as you go.
2. Edit `ergogen-kikad/design/config.yaml` and its footprints; regenerate KiCad boards with `./scripts/generate.sh` while KiCad is closed. The script routes both boards and runs DRC before replacing outputs.
3. After board dimensions or mounts change, run `./scripts/generate-mechanical.sh`.
4. Keep the ZMK shield and keymap aligned with switch nets. Do not add code comments.
