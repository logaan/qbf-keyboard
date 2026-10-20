1. Commit as you go.
2. Edit `ergogen-kikad/design/config.yaml` and its footprints; regenerate KiCad boards with `./scripts/generate.sh` while KiCad is closed. The script routes both boards and runs DRC before replacing outputs; previews are native KiCad SVG plots rasterized to PNG.
3. After board dimensions or mounts change, run `./scripts/generate-mechanical.sh`.
4. Build firmware with `./scripts/build-firmware.sh /path/to/zmk-workspace`. Keep the ZMK shield and keymap aligned with switch nets. Do not add code comments.
5. Key names are t1–t5 and b1–b5, left to right; column 5 contains the controller. Keep outer cap edges aligned across each row; t5/b5 use landscape 1.5U caps with the same 2.55 mm horizontal cap gap.
6. Keep M2 pairs between columns 1/2 and 3/4 and a third pair between column 5 and the reset/power controls; allow PCB outline growth to support case walls resting above the PCB.
7. Keep switches directly wired to GPIO and GND, with no diodes or matrix.
8. Keep the protected 301055 battery envelope and side-entry JST-PH between the original switch rows, with the pack near the left edge in a main-PCB-only well supported by the intact baseplate and connector near the controller; upward-facing power/reset controls go beside t5/b5. Align reset with t5 and power with b5; keep their shared vertical center line at x=108.725 mm in the fixed component layout, halfway between the fifth-column cap right edge and the original functional region right edge when the PCB outline grows. Switch battery positive before nice!nano RAW; reset shorts RST to GND.
9. Through-hole and surface-mount user soldering are both permitted. Use ready-made display modules with documented use in an open-source mechanical keyboard; a README or build guide is sufficient evidence.
10. Socket the nice!view directly into its native five-pin 2.54 mm footprint; keep the socket body clear of the controller. Do not substitute flying wires.
11. Keep 3D model assignments in `scripts/attach_models.py`; run `./scripts/render-3d.sh` for native KiCad assembled and internal inspection views. Model approximations are listed in `ergogen-kikad/design/models/README.md`.
12. For bumper-case changes and recurring assembly previews, follow `bumper-case/AGENTS.md`; retain every component except keycaps in the cap-free preview.
