# QBF modular case

Two independent cases join flat using a removable underside bridge. The second keyboard rotates 180° so both controllers face the centre. Each case has its own snap-on key cover. Joining, splitting and removing covers require no tools; initial board installation uses four screws per half. There is no hinge or folding mechanism.

![Joined, solo and protected configurations](generated/overview.png)

## Files and dimensions

- [Print bundle](generated/qbf-print-files.zip): four STL designs, quantities and this guide.
- [Editable FreeCAD assembly](generated/qbf_modular_case.FCStd), containing the four separate case parts in assembly coordinates. Edit the geometry through `build.py` and `parameters.json`, or use the exported solids in your CAD application.
- STEP: [tray](generated/tray.step), [rim](generated/rim.step), [cover](generated/cover.step), [bridge](generated/bridge.step).
- [Dimensioned drawing](generated/dimensions.png), [case parts](generated/case_parts.png), [underside connection](generated/bridge_underside.png), and [print orientation](generated/print_orientation.png).
- [Native assembled view](generated/assembled.png), [cap-free inspection](generated/inspection.png), and [both covers fitted](generated/protected.png).

| Configuration | Envelope, mm |
| --- | --- |
| PCB, tray and rim | 97.7 × 58.5 |
| Solo, open, including USB projection and feet | 99.09 × 58.5 × 18.77 |
| Solo, covered, including finger tabs and feet | 100.9 × 63.3 × 21.2 |
| Joined, open | 205.4 × 58.5 × 18.77 |
| Joined, covered | 208.6 × 63.3 × 21.2 |
| Gap between joined PCB edges | 10.0 |

The body of each cover is 100.9 × 61.7 mm; its two finger tabs increase overall depth to 63.3 mm. The accepted key layout produces a PCB wider than the original 80 mm target. Case walls are 2 mm thick and rest on the PCB border, leaving 0.25 mm beside the keycap envelopes. Key travel is unchanged.

## Print

For a pair, print two identical trays, two rims, two covers and one bridge. For a solo board, print one tray, one rim and one cover; the bridge is unnecessary. Use the `_print.stl` files: their orientations are already set and their bottoms are at Z=0. `_assembly.stl` and STEP files retain the electronics coordinate frame and are not pre-oriented for printing.

| Part | Quantity for two halves | Print orientation |
| --- | --- | --- |
| [Tray](generated/tray_print.stl) | 2 | Flat PCB-contact face down; feet and receiver pockets upward |
| [Rim](generated/rim_print.stl) | 2 | Upper wall and battery-roof face down |
| [Cover](generated/cover_print.stl) | 2 | Flat outer roof down; clips upward |
| [Bridge](generated/bridge_print.stl) | 1 | Flat underside down; T-heads upward |

PETG is the intended starting material for the cover and bridge flexures. Use a calibrated 0.4 mm nozzle and 0.2 mm layers, at least three perimeter lines where geometry permits, and solid thin features. The 0.4 mm rim mounting tabs need two complete layers. The tray can use moderate infill between solid surface layers. Avoid stiff, brittle or filled filament for the clips.

Inspect the slicer before printing. Receiver ledges, the bridge head shoulders and the rim's short tab spans may need local supports depending on the printer's bridging performance. Keep support scars out of the slide tracks and snap recesses. The cover's internal stop ledges have 45° ramps; the cover roof prints directly on the bed. These are prescribed print orientations, not a claim of a tested support-free print. Compensate first-layer expansion so the tray's PCB contact face and cover roof remain flat.

The bridge heads have 0.3 mm side clearance and 0.1/0.2 mm vertical clearance in their pockets. The cover has 0.3 mm shell clearance around the rim. Check a first set before printing the second: it should slide and clip with finger pressure without whitening or cracking. Remove burrs rather than forcing parts against an installed battery or controller.

## Install a keyboard

For each half, use **four M2 × 6 mm screws** with heads no larger than **3.8 mm diameter × 1.6 mm high**, and **four M2 thin nuts, 4 mm across flats × 1.2 mm thick**. This case hardware replaces the M2 × 5 mm screws and thicker nuts used in the electronics-only clearance reference. Do not mix the stacks.

1. Assemble and test the electronics following the [board assembly requirements](../ergogen-kikad/design/ASSEMBLY.md). Keep the insulating battery adhesive, XIAO support film, protected pack, side-entry JST-SH connection and insulated BAT wire. The baseplate remains intact under the battery. Confirm all ten caps bottom out freely before fitting the case.
2. Seat the four thin nuts in the tray's underside hex pockets. Place the board/baseplate stack on the tray's flat upper face. Keep wires within the verified baseplate openings; nothing should be trapped between tray and baseplate.
3. Remove the keycaps and lower the rim over the switches. Its battery roof sits 0.3 mm above the pack and its mounting tabs sit directly on the main PCB.
4. Insert the four M2 × 6 screws from above and tighten only enough to retain the stack. Do not crush the thin printed tabs. Nominal screw tips finish 0.8 mm above the tray's underside and 2.2 mm above the feet's contact plane.
5. Refit the caps and check full travel, especially beside the low inter-column ribs. Operate the left-facing power switch through its side opening. The XIAO USB port and onboard reset remain exposed through the opposite opening. The electronics reserve allows a 2 mm reset probe.

The rim and tray have the same outline as the PCB; the PCB/baseplate edges are visible between them. Integrated printed feet support each half independently. Additional grip pads are optional and will increase the published height.

## Join and separate

Place the halves side by side, rotate the second one 180°, and leave 10 mm between their inner PCB edges. The power switches face outward and the controllers face inward. Turn the pair over or lift it to access the underside.

Position the bridge 6.5 mm away from its centred position along the long slots. Insert all four T-heads through the enlarged end openings, hold the two spring tabs down if needed, then slide the bridge 6.5 mm to centre until both detents engage. The double-ended slots work with the rotated identical tray. The crossbars and four captured heads hold the two halves flat; the two spring detents prevent unintended sliding.

To split, support the cases, press both exposed spring tabs away from the trays, slide back 6.5 mm and lift the bridge away. Lift the assembly off the desk first to give the tabs room to deflect. Either half then works independently. Store the small bridge separately when it is not fitted.

Ordinary straight USB plugs need more space than the 10 mm centre gap. Separate the halves for charging, flashing or wired use with those cables. The case connection is mechanical only; both boards retain their independent USB/Bluetooth operation.

## Protect the keys

Lower each cover squarely over its own rim until its front and back clips engage. Internal ledges stop against the rim at Z=3.6 mm, so the cover cannot move downward onto the keys as a rigid body. The roof underside sits 1.23 mm above the resting caps. Reinforcing ribs sit in the gaps between columns and clear the cap envelopes.

Pull the two cover finger tabs outward slightly and lift to remove. Covers fit with the halves joined or separated. Do not stack the halves key-to-key or fold them together. The covered pair stays flat; two separately covered halves can be carried individually.

## Checks and limits

[Validation](generated/validation.json) records 703 passing nominal CAD checks. All four parts are valid single solids with closed exported meshes. The checks include full cap travel, switch shoulders, the native power-switch and connector models, the battery and leads, controller and solder envelopes, complete power stroke, cable/reset access with covers off, actual baseplate holes, case fasteners, cover release and both rotated bridge receivers. The bridge insertion sweep checks rigid geometry separately from the deliberately deflected spring detents.

The estimated outer-fibre strain for the prescribed release movement is about 1.12% at each cover clip and 0.50% at each bridge clip. These are small-deflection geometry estimates, not a material strength or fatigue qualification. Flexure shape during movement is approximated by cleared rigid envelopes; elastic deformation is not simulated. Printed tolerance, clip retention, repeated use, rim-tab durability, drop resistance and roof deflection under transport loads require physical testing. A cover roof that bends by more than the clearance could press keys; the current work has not load-tested that condition.

The [electronics contract](../ergogen-kikad/generated/assembly-contract.json) remains authoritative for hardware assumptions and the recessed XIAO soldering process. Purchased cap cavities, module PCB thickness and the actual cable/connector must be checked. Native renders use the documented component approximations. The inspection view removes exactly ten caps and retains all other components and all installed case parts.

## Regenerate

After the earlier Ergogen, KiCad, clearance and firmware stages are complete and reviewed, run sequentially from the repository root:

```sh
./scripts/generate-mechanical.sh
./modular-case/render.sh
./modular-case/present.sh
```

The first command builds solids, validates geometry and exports CAD/meshes. It checks board and design hashes against the electronics contract and refuses stale input. The second creates temporary native KiCad views without modifying production boards; 3D assignments live in `scripts/attach_models.py`. The third renders the STL geometry, produces the dimension drawing and packages the print bundle. FreeCAD's bundled Python supplies the geometry, NumPy, Pillow and Qt dependencies on this Mac; paths can be overridden in the scripts.

The older `bumper-case/` and `mechanical/` designs are historical and do not fit this board.
