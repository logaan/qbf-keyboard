# Provisional five-column comparisons

These alternatives show ten keys in a five-column, two-row arrangement. They are design comparisons only. They do not replace `../config.yaml` or the production boards, and have no routing, fabrication, fastener, case or assembly validation.

| Variant | Main eight caps | Fifth-column caps | Column pitch | Row pitch | PCB outline |
| --- | --- | --- | --- | --- | --- |
| A | 1U, 17.5 × 16.5 mm | Same 1U | 19.05 mm | 19.05 mm | 98 × 80 mm |
| B | Portrait 1.5U, 16.5 × 26.5 mm | 1U, 17.5 × 16.5 mm | 19.05 mm | 27.5 mm | 98 × 96 mm |

Version A has a 2.55 mm gap between rows of caps and a 1.55 mm horizontal gap. Version B has a 1 mm gap between the large caps and a 2.55 mm horizontal gap across its four large-cap columns. Using 19.05 mm row pitch with the portrait 1.5U caps would overlap them by 7.45 mm. Both versions preserve horizontal reflection symmetry of the key centers and caps.

The outer column centers are 76.2 mm apart. Adding a 17.5 mm cap produces a 93.7 mm cap span before any PCB edge margin, so neither five-column layout fits the original 80 mm width target. The diagrams mark that original 80 × 80 mm target with red dashes and use the same physical scale.

The 19.05 mm pitch reference comes from the [Sofle Choc PCB source](https://raw.githubusercontent.com/josefadamcik/SofleKeyboard/master/Sofle_Choc/PCB/SofleKeyboard.kicad_pcb): SW1 x=120.55 mm and SW2 x=139.6 mm differ by 19.05 mm; SW13 y=88.1 mm and SW19 y=107.15 mm differ by 19.05 mm. The Sofle itself includes column stagger; these alternatives apply its nominal pitch to a regular grid.

Each variant reserves the same socketed nice!nano/nice!view stack, protected 301230 battery, through-hole JST-PH connector, upward power/reset controls and six provisional mount holes. The mount positions are placeholders, without fastener clearance claims.

`comparison.png` is the uncluttered dimensioned comparison, derived from actual generated switch placements in `placements.json`. Each variant directory contains an unrouted Ergogen PCB, board outline, native KiCad SVG plots and their PNG rasterizations. The native plots include all component and pad details; they are not routed-board previews.

To reproduce the placement previews from the repository root:

```sh
python3 ergogen-kikad/design/alternatives/build.py
python3 ergogen-kikad/design/alternatives/draw_comparison.py
QT_QPA_PLATFORM=offscreen PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib /Applications/FreeCAD.app/Contents/Resources/bin/python scripts/render_svg.py ergogen-kikad/design/alternatives/comparison.svg
```

`build.py` checks that the generated PCB contains all ten keys, the intended cap dimensions and the selected row pitch. It invokes the existing native KiCad SVG plot and rasterization workflow in an isolated staging folder.
