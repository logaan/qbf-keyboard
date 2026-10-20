# Reversible two-board carrier

This set holds **two identical QBF boards** in one printed case. Fit one lower and one upper bumper rail to each board, for four rails total. The case has two slide-in bays. Rotate the left board 180° in the plane of the keys so both USB-C ports face the outside ends. Both bays accept the same rail profile.

| Orientation | Insertion | Result |
| --- | --- | --- |
| Exposed | Keycaps up, with bumper rails below the boards | Two keyboard halves share a rigid base for typing. Both USB-C ends stay open. |
| Protected | Flip each board and rail assembly keycaps down | The solid floor faces the keys, with modeled clearance so the case does not press them. |

The rails sit on the **outside of the base plate**, underneath its long edges in typing orientation. They project 2.5 mm beyond each long board edge to engage the case grooves. They do not cover the central USB-C end. Their edges remain below the PCB and keycaps in typing orientation. The two detents near each bay's outward end engage matching rail notches. Slide the boards out by pushing firmly and evenly at the two corners; do not pull on the USB connector.

## Files and print quantities

- [`generated/bumper_lower.stl`](generated/bumper_lower.stl) — print 2.
- [`generated/bumper_upper.stl`](generated/bumper_upper.stl) — print 2.
- [`generated/two_board_case.stl`](generated/two_board_case.stl) — print 1.
- Matching `.step` files are provided for CAD editing.
- [`QBF_carrier.FCMacro`](QBF_carrier.FCMacro) rebuilds the three native Part solids and saves a FreeCAD document. [`build_parts.py`](build_parts.py) generates the STEP and STL files from the same native solids.

Print the rails flat and the case with its solid floor on the bed. The case grooves have a 2.6 mm horizontal bridge and are designed to print without support. Start with PETG or another slightly compliant material, then test the 0.5 mm vertical slot clearance and the 0.4 mm detent interference on the actual printer before printing a final case.

## Fit and fastening

The PCB and base plate are each nominally 1.6 mm thick. Each 4 mm rail has two 2.0 mm locating pegs, for four pegs per board, aligned with the 2.2 mm board holes. Each rail has two tabs reaching the internal mounting holes. Each peg is 1.4 mm high, so it stays below the component face of a 1.6 mm board and cannot touch a moving keycap. Fix the rails to the underside of the base plate with thin double-sided adhesive tape; the pegs locate the rails and resist sliding. Keep the adhesive off the MagSafe ring area. The rails can also attach directly under a PCB without a base plate if the solder joints clear them. Remove the rails to use the holes for M2 neck-strap fittings.

The protected orientation places the component face about 13.8 mm above the outside bottom of the case when the PCB and base plate are both fitted. The floor's inside face is at 2.5 mm, leaving **11.3 mm maximum component/cap projection below the PCB face** before contact. Measure the built switch, cap, and socketed XIAO stack before relying on this clearance. If it is taller, increase `SLOT_BOTTOM` and `CASE_TOP` together in the CAD source and regenerate the case. The exposed orientation keeps the case walls outside the board and cap outline.

The outside dimensions of the case are 201.9 × 65 × 22.2 mm. The two board outlines are 95.95 × 55 mm with a 4 mm middle gap. Tabs on each rail reach the mounting holes between switch columns; the hole rows are 27.5 mm apart.

The parts are geometric prototypes. No physical print, cap-travel, USB-plug, fastener, or drop test has been done.

## Regenerate

Run from the repository root after regenerating the electronics:

```sh
./scripts/generate-mechanical.sh
```

Requires FreeCAD. Override `FREECAD_PYTHON` and `FREECAD_LIB` if needed. Board dimensions and mount positions come from `ergogen-kikad/generated/board_geometry.json`. This rebuilds the FreeCAD document and STEP/STL exports, checking that every part is a valid solid.
