# Compact no-display layout sketch

`no-display-compact-layout.png` shows a provisional 97.5 × 57 mm outline, in the unchanged layout frame x=1..98.5, y=19.5..76.5. The main eight switches remain at x=10.9/29.95/49/68.05 and y=34.25/61.75, with 16.5 × 26.5 mm caps and 27.5 mm row pitch. The fifth pair uses 17.5 × 16.5 mm caps at (87.1,29.85)/(87.1,66.15), giving 1 mm plan clearance to the XIAO body on each side. The fourth-column cap edges have 0.7 mm clearance to the controller's left edge. Key geometry remains symmetric about y=48.

The Seeed XIAO nRF52840 Plus body remains at (87.5,48), with USB facing right and approximately 1 mm beyond the provisional PCB edge. Its onboard reset replaces the separate reset switch. It has an integrated ceramic antenna; RF keepout is deferred. The coplanar cutout, conductive edge lands, solder access and mechanical support remain a mounting concept rather than implemented PCB geometry.

The left-facing C&K PCM12SMTR power body is 6.7 × 2.6 × 1.4 mm and fits beneath column one's outer cap edge. Its 1.5 mm actuator projection extends 1 mm beyond the provisional left PCB edge. The protected 301055 battery moves to (35.5,48), reserving 57.5 × 10.5 × 3.5 mm and a 58.1 × 11.1 mm main-PCB-only well on an intact baseplate. Its well clears the power courtyard by 0.9 mm and nominal switch shoulders by 0.7 mm.

The JST-SH component is shown with an explicit 8 × 6 mm allowance including mating plug space. The verified header envelope is 4 × 4.25 × 2.9 mm, with a provisional 3 mm assembly height allowance. Exact mated geometry and battery wire routing remain unverified. This replaces the larger JST-PH in the sketch only.

Six provisional M2 holes use 2.2 mm bores and 4.6 mm screw keepout circles: x=20.425/58.525/77, y=23.5/72.5. Low-profile heads are proposed above the PCB, with nuts below. Nominal keepouts clear all switch shoulders by at least 0.3 mm and have 1.7 mm to the nearest PCB edge. The assumed 1.6 mm maximum head height leaves 2.4 mm below the assumed full-travel cap underside. Actual fasteners, case walls, baseplate attachment, native component bodies and operating clearance need later assembly checks.

The JSON source is `no-display-compact-layout.json`. `no-display-compact-checks.json` records nominal envelope checks. No production design, routed board, firmware or case files are changed. Reproduce the illustration from the repository root:

```sh
python3 ergogen-kikad/design/alternatives/draw_no_display_compact.py
QT_QPA_PLATFORM=offscreen PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib /Applications/FreeCAD.app/Contents/Resources/bin/python scripts/render_svg.py ergogen-kikad/design/alternatives/no-display-compact-layout.svg
```
