# Two recessed-XIAO / nice!view concepts

`xiao-stack-comparison.png` compares two diagram-only concepts at the same physical scale. Both retain the 98 × 96 mm outline and original eight switches. Both move the fifth-column key centers outward by 8.5 mm to y=75.25/20.75, preserving reflection symmetry about y=48. The XIAO nRF52840 Plus body is represented as 21 × 17.8 mm at (87.5,48), recessed coplanar with the main PCB, with USB projecting approximately 1.5 mm past its right edge. The display sits above the controller; its native five-pin socket attaches directly to the main PCB.

The portrait nice!view occupies x=80.5..94.5, y=30..66. It has 1 mm plan clearance to each fifth-column cap and 4.2 mm to column four. Its native socket sits below the controller in plan, clear of the XIAO body. The onboard reset center at (96.073,53.721) remains exposed, but the nominal display-to-reset-body gap is only 0.273 mm; operating access needs validation.

The horizontal nice!view occupies x=62..98, y=41..55. It overlaps column four's cap projection by 14.3 mm in width. Its 14 mm body and 12.7 mm socket also exceed the 12.5 mm nominal switch-shoulder gap. Low mounting conflicts with key travel; raising it above the caps would obstruct the paired-key pressing area. It also covers the onboard reset, whose access is unresolved. No vertical stack geometry is asserted by this top-view diagram.

The protected 301055 battery remains below the main cap overhang. Power and JST-PH are shown in provisional upper positions to vacate the controller area. Their wiring and the battery-lead route are deferred. Coplanar mounting requires designed conductive edge pads, mechanical support and solder access; the cutout and castellated mounting concept are not fabrication validated. Actual recess depth, module height, USB geometry, socket height, cap cavities and operating access still require assembled geometry checks.

These artifacts do not modify the selected B Ergogen source, active configuration, production boards, firmware or case.

Placements are recorded in `xiao-stack-comparison-placements.json`. To regenerate the diagram from the repository root:

```sh
python3 ergogen-kikad/design/alternatives/draw_xiao_stack_comparison.py
QT_QPA_PLATFORM=offscreen PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib /Applications/FreeCAD.app/Contents/Resources/bin/python scripts/render_svg.py ergogen-kikad/design/alternatives/xiao-stack-comparison.svg
```
