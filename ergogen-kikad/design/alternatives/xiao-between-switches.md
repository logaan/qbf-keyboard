# XIAO centered between t4 and b4

`xiao-between-switches.png` is a dimensioned top-view test of a Seeed XIAO nRF52840 Plus at (68.05,48), with USB facing right. It does not change the selected layout or any production files.

The t4/b4 switch centers remain (68.05,61.75)/(68.05,34.25). Each portrait keycap measures 16.5 × 26.5 mm. Nominal Choc shoulder envelopes measure 15 × 15 mm, leaving 27.5 − 15 = 12.5 mm between them. The controller body measures 21 × 17.8 mm, so its centered footprint overlaps each shoulder by (17.8 − 12.5) / 2 = 2.65 mm. Red hatching marks those overlaps. The schematic USB projection is excluded from the 21 mm controller-body dimension.

The inset retains all eight main switches and the outer-edge-aligned fifth pair at y=66.75/29.25. This illustration tests nominal plan-view envelopes. It does not establish recess depth, real component body detail, cap cavity, vertical clearance or operating fit.

Geometry and dimensions are recorded in `xiao-between-switches-placements.json`. To regenerate from the repository root:

```sh
python3 ergogen-kikad/design/alternatives/draw_xiao_between_switches.py
QT_QPA_PLATFORM=offscreen PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib /Applications/FreeCAD.app/Contents/Resources/bin/python scripts/render_svg.py ergogen-kikad/design/alternatives/xiao-between-switches.svg
```
