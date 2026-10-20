# Stage 1: approved Ergogen layout

The active source is `../config.yaml`. This stage defines geometry and placement only. The native KiCad SVG/PNG previews here come from isolated temporary Ergogen output; production boards have not been regenerated or routed.

The PCB is 97.7 × 58.5 mm, with bounds x=0.4..98.1, y=18.75..77.25 in the fixed switch-layout frame. All outer cap edges have at least 2.25 mm of PCB border. The main eight switches retain x=10.9/29.95/49/68.05 and y=34.25/61.75, portrait 16.5 × 26.5 mm caps, 19.05 mm column pitch and 27.5 mm row pitch. The 1U fifth pair uses 17.5 × 16.5 mm caps at (87.1,66.75)/(87.1,29.25), aligning every top edge at y=75 and every bottom edge at y=21. Four M2 holes remain at x=20.425/58.525, y=23.5/72.5.

The no-display controller placement is a 21 × 17.8 mm Seeed XIAO nRF52840 Plus centered at (87.5,48), with USB right and onboard reset. `xiao_nrf52840_plus_reference.js` intentionally contains no electrical pads or fabricated cutout. Its contact marks are placement references derived from the supplied XIAO SMD footprint, not a coplanar solder pattern. Stage 2 must design conductive edge lands, support, cutout clearance, battery-input attachment and RF keepout from the official module files. This Stage 1 output is not manufacturing-ready.

The protected 301055 envelope and well are centered at (35.5,48). The battery stays 57.5 × 10.5 × 3.5 mm, in a main-PCB-only 58.1 × 11.1 mm well on the intact baseplate. The PCM12 footprint origin is (3.8,48), rotated left. Its complete nominal actuator is 0.25 mm inside the board and its rear copper clears the battery well by 0.47 mm. The well clears the nominal switch shoulders by 0.7 mm. The JST-SH origin is (71.875,48), facing left, with an 8 × 6 mm mating allowance; full mated geometry and the lead path remain to be checked.

PCM12 and JST-SH pad/body geometry is transcribed from the installed KiCad `SW_SPDT_PCM12` and `JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal` footprints. Models remain assigned only through `scripts/attach_models.py` in the later KiCad stage. Historical unused nice!nano, display, reset and JST-PH footprint source files are retained, but the active configuration references none of them.

Logical direct-wire signal names are t1–t5 = D0–D4 and b1–b5 = D5–D9, each paired with GND. The XIAO physical pin landing and later firmware GPIO mapping must implement these names consistently. Battery positive passes through the PCM12 before the XIAO battery input.

`validation.json` records the isolated generated placements, cap margins, four holes, power containment, well clearances and absence of legacy active parts. Reproduce without replacing production boards:

```sh
./ergogen-kikad/node_modules/.bin/ergogen ergogen-kikad/design --output /private/tmp/qbf-stage1-ergogen
./scripts/preview.sh /private/tmp/qbf-stage1-ergogen
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 ergogen-kikad/design/stage1/validate.py /private/tmp/qbf-stage1-ergogen/pcbs/macropad.kicad_pcb
```

Stage 2 KiCad work must follow Stage 1 review. Firmware follows KiCad; mechanical and case work come last.
