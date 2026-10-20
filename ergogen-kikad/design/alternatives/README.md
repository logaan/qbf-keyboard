# Provisional five-column layouts

The selected B revision is shown in `selected-B.png`. Its current source is `five-column-15u.yaml`, with a native KiCad placement preview in `five-column-15u/layout.png`. The earlier side-by-side `comparison.png` is retained as a historical comparison, using its frozen `comparison-placements.json` snapshot.

These alternatives show ten keys in a five-column, two-row arrangement. They are design comparisons only. They do not replace `../config.yaml` or the production boards, and have no routing, fabrication, fastener, case or assembly validation.

| Variant | Main eight caps | Fifth-column caps | Column pitch | Row pitch | PCB outline |
| --- | --- | --- | --- | --- | --- |
| A | 1U, 17.5 × 16.5 mm | Same 1U | 19.05 mm | 19.05 mm | 98 × 80 mm |
| B | Portrait 1.5U, 16.5 × 26.5 mm | 1U, 17.5 × 16.5 mm | 19.05 mm | 27.5 mm | 98 × 96 mm |

Version A has a 2.55 mm gap between rows of caps and a 1.55 mm horizontal gap. Version B has a 1 mm gap between the large caps and a 2.55 mm horizontal gap across its four large-cap columns. Using 19.05 mm row pitch with the portrait 1.5U caps would overlap them by 7.45 mm. Both versions preserve horizontal reflection symmetry of the key centers and caps.

The outer column centers are 76.2 mm apart. Adding a 17.5 mm cap produces a 93.7 mm cap span before any PCB edge margin, so neither five-column layout fits the original 80 mm width target. The diagrams mark that original 80 × 80 mm target with red dashes and use the same physical scale.

The 19.05 mm pitch reference comes from the [Sofle Choc PCB source](https://raw.githubusercontent.com/josefadamcik/SofleKeyboard/master/Sofle_Choc/PCB/SofleKeyboard.kicad_pcb): SW1 x=120.55 mm and SW2 x=139.6 mm differ by 19.05 mm; SW13 y=88.1 mm and SW19 y=107.15 mm differ by 19.05 mm. The Sofle itself includes column stagger; these alternatives apply its nominal pitch to a regular grid.

The selected B revision keeps the main eight switch centers unchanged: x=10.9/29.95/49/68.05 mm, y=34.25/61.75 mm. Its fifth-column centers are x=87.1 mm, y=29.25/66.75 mm, so every lower cap edge is at y=21 and every upper cap edge is at y=75. The complete key geometry remains symmetric about y=48 mm.

Reset is at (81.5,53), with power to its right at (91.5,53). The JST-PH connector is at (89.5,43), pointing left, in the free space between the fifth-column keys. Its full mating envelope starts at x=77.25, leaving 0.95 mm to the fourth-column cap edge at x=76.3. These taller parts clear the full cap projection.

The nice!nano remains at (20,85.75), with its USB port facing left. The nice!view moves to (60,85.75), on the controller's right, and uses its native five-pin footprint with a direct socket. The two module body envelopes have a 4 mm gap and no vertical overlap in plan. Socket height and assembled model assignments remain deferred.

The protected 301055 pack returns between the main rows, centered at (32,48). The reserved 57.5 × 10.5 × 3.5 mm envelope fits the 12.5 mm gap between nominal switch shoulders; the 58.1 × 11.1 mm PCB well has 0.7 mm clearance to each row's shoulder envelope. The reserved 301230 width of 13 mm and its 13.6 mm well would not fit. The selected pack sits on the intact baseplate in a main-PCB-only well. At bottom z=-1.4 its top is z=2.1, below the assumed full-travel cap underside z=4. A future 1 mm roof with a 0.3 mm battery gap would top out at z=3.4. Low wires leave the pack at x=60.75,y=48, run toward x=74.8, then turn into the JST plug at (77.25,43); their maximum reserved top is z=1.95. `selected-B-battery.json` records this provisional envelope without changing the active battery specification.

`selected-B-layout-checks.json` records numerical layout checks: the stationary main eight, cap edge alignment, reflection symmetry, conservative component body envelopes, every pad/drill rectangle at least 0.5 mm from the battery well and PCB edge, and at least 0.2 mm clearance between pad/drill rectangles belonging to different footprints. All assertions run over all pairs; the report retains counts and the closest 20 clearances. These are placement-envelope checks, not routed-board DRC or native assembled model validation. The six mount holes remain provisional, without fastener clearance claims.

`selected-B.png` is the current dimensioned layout, derived from actual generated switch placements in `placements.json`. `comparison.png` is the earlier dimensioned comparison. Each variant directory contains an unrouted Ergogen PCB, board outline, native KiCad SVG plots and their PNG rasterizations. The native plots include all component and pad details; they are not routed-board previews.

To reproduce the placement previews from the repository root:

```sh
python3 ergogen-kikad/design/alternatives/build.py five-column-15u
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 ergogen-kikad/design/alternatives/check_selected_b.py
python3 ergogen-kikad/design/alternatives/draw_selected_b.py
QT_QPA_PLATFORM=offscreen PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib /Applications/FreeCAD.app/Contents/Resources/bin/python scripts/render_svg.py ergogen-kikad/design/alternatives/selected-B.svg
```

`build.py` checks that the generated PCB contains all ten keys, the intended cap dimensions and the selected row pitch. It invokes the existing native KiCad SVG plot and rasterization workflow in an isolated staging folder.
