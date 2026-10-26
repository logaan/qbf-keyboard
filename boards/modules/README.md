# Compact Braille keyboard review

Editable Ergogen design and routed KiCad review files for a twelve-key wireless keyboard. The top and bottom rows have portrait 1.5U key envelopes; the middle row has 1U envelopes. The nice!nano, nice!view and battery are underneath, with the display between the controller and battery.

## Latest placement revision (26 October, NOT ROUTED)

Following the request to inset edge hardware and lower the bottom keys, the editable sources and **placement-only** boards have been updated: `ergogen/config.yaml`, `scripts/build_modules.py`, `ergogen/module{2,3}/config.yaml`, `kicad/module1_inset_placement.kicad_pcb`, and `kicad/module{2,3}_placement.kicad_pcb`. Module 1's controller/USB is moved 1.5 mm south, reset 2 mm inward, power 1.5 mm north and JST 1.3 mm north. Modules 2 and 3's bottom switches are 4 mm south (towards the bottom edge); both power switches are 1.5 mm north. Module 2's JST is 2.5 mm north to avoid the power-switch courtyard. The 75.2 mm outline, MX/Sofle v1 horizontal pitch and screw positions remain unchanged.

**Do not manufacture these placement boards:** they contain unrouted connections (40 / 24 / 26 respectively), as shown in `kicad/moduleN-new-placement-drc.txt`. The files named `*_routed.kicad_pcb` are the **earlier layout**, not copper for these changed placements: they must not be combined with the new Ergogen files. Freerouting v2.2.4 completed module 2's routing passes but stalled before saving a session (`kicad/module2-new-routing.log`); dragging the old traces onto moved pads caused shorts and was discarded. The existing module 2/3 routed boards retain zero unconnected pads and no copper shorts for their **old** geometry. Module 1's original routed board still has one missing connection and pre-existing DRC errors. All three require a fresh reroute and clearance/mechanical verification before fabrication. No previews were rendered.

## Additional module studies (not fabrication-ready)

- **Module 2:** `ergogen/module2/config.yaml`, `kicad/module2_placement.kicad_pcb`. Four original portrait 1.5U top-row keys plus two 1U bottom corner keys; controller, display, 12 × 30 mm provisional cell, reset and power on the front. The cell requires an insulated elevated mounting shelf; the PCB outline is unchanged.
- **Module 3:** `ergogen/module3/config.yaml`, `kicad/module3_placement.kicad_pcb`. Four 1U keys at the bottom, a 43 × 43 mm Azoteq TPS43 (Toucan2) touch-surface envelope, front controller/display/reset/power, and a provisional 50 × 50 × 3 mm LiPo envelope on the back. The touch sensor must be carried on a raised insulated assembly above the controller/display: their projected footprints overlap. `ergogen/footprints/local/tps43_interface.js` provides **only an abstract six-signal adapter pad pattern**, not the Toucan2 7-way FPC connector/pinout. Do not mate a sensor directly to these pads. Confirm TPS43 connector, wiring, mechanical thickness, glass, battery and mounting before fabrication.

Both share the 75.2 × 75.2 mm nominal board, corner mounting holes and the original independent grounded Choc switch scheme. Both use the same nice!nano/nice!view nets, JST battery connector and disconnect/reset convention as module 1. Sources are independent; `scripts/build_modules.py` regenerates their Ergogen YAML from module 1. Rebuild with `python3 scripts/build_modules.py`, copy each `ergogen/moduleN.yaml` to `ergogen/moduleN/config.yaml`, then run `node_modules/.bin/ergogen ergogen/moduleN -o output/moduleN` (N = 2 or 3). `ergogen/moduleN/footprints` links to the shared footprint directory. KiCad sources are copies of the generated PCB files.

**Routing update (26 October):** `kicad/module2_routed.kicad_pcb` and `kicad/module3_routed.kicad_pcb` now have **zero unconnected pads**. The reset switches were inset 2.7 mm, module 2's JST was moved 5.6 mm inward away from the power switch, all four reset pads were connected (using vias where necessary), and module 3's TP_SCL was completed with a two-via, two-layer route. Both retain the original 75.2 mm square outline, mounting holes and 19.05 mm (MX/Sofle v1) horizontal spacing. KiCad DRC reports **no copper/edge/clearance/short/courtyard errors** on either board; the remaining 42 (module 2) and 44 (module 3) findings are missing external footprint-library registrations and silkscreen/text warnings. See `kicad/moduleN-routed-drc.txt`. Original router copper is preserved as `kicad/moduleN_autorouted_base.kicad_pcb`; rerun `python3 scripts/finish_module_routes.py` followed by `python3 scripts/route_touch_clock.py` to recreate the final routed files, then run `kicad-cli pcb drc --severity-all -o kicad/moduleN-routed-drc.txt kicad/moduleN_routed.kicad_pcb` (N=2,3). Do not rerun `route_modules.py` against the revised placement files without reviewing the result: Freerouting 2.2.4 sometimes stalls after routing and before writing its session.

**Important:** Electrically connected and copper DRC-clean does **not** mean fabrication-ready. Verify the mill-max socket depth, trimmed-leg insulation and component/keycap clearances in a real mechanical stack-up (especially controller/switch and raised touch surface). The abstract TPS43 interface is **not** a verified seven-pin FPC connector or pinout: design a real adapter before ordering. Confirm the cell, polarity, charging/protection, power-switch wiring, thickness offered by JLCPCB and actual assembly height. No complete schematic, assembly hardware, charger, battery protection verification or firmware is supplied. Remaining silk and library DRC warnings need resolution before production; no preview renders were run.

## Open these files

- `docs/switch-rotation-flow.svg`: source edit and commands to propagate a switch rotation through routing, previews, checks and web publication.
- `kicad/braille_review_routed.kicad_pcb`: the main PCB for manual placement and routing changes.
- `kicad/braille_assembly_preview.kicad_pcb`: the same PCB with the assembly envelope model attached for KiCad's 3D viewer.
- `previews/assembly-top.png` and `previews/assembly-bottom.png`: complete assembly views.
- `previews/modules-bottom.png`: underside components with the acrylic hidden.
- `previews/layout-review.svg`: dimensioned layout, underside, baseplate and height study.
- `output/outlines/baseplate.dxf`: acrylic outline and matching mounting holes.
- `ergogen/config.yaml`: editable layout, component placement and mechanical parameters.
- `kicad/pin-map.csv`, `kicad/drc-routed.txt` and `kicad/review-summary.json`: wiring, outstanding checks and measured dimensions.
- `models/routed-board.step`: board-only STEP geometry. The component and assembly models are separate VRML envelopes.

Keep the directory structure when opening the preview PCB: its model paths are relative to the `models` folder.

## Current draft dimensions

| Part | Dimensions |
| --- | --- |
| PCB | 75.2 × 75.2 × 1.6 mm |
| Acrylic baseplate | 75.2 × 75.2 mm; 3 mm thickness is provisional |
| Planar assembly, including USB and reset/power actuators | 76.0 × 77.469 mm, measured from the library geometry |
| Illustrated assembly height, including the ring | 20.0 mm, provisional |

The earlier “subtle v1.1” transcription refers to Sofle v1. The draft retains the standard 19.05 mm MX/Sofle horizontal pitch and nominal keycap envelopes, rather than verified dimensions from a purchased keycap set. The illustrated height assumes 6.5 mm standoffs, socket heights and keycap/switch envelopes that still need physical confirmation. The passive adhesive ring is provisionally 56 mm outside diameter, 46 mm inside diameter and 0.4 mm thick, beneath the acrylic. Flush underside fastener heads are assumed.

## Electrical design and remaining review

Each key has an independent controller input and a ground connection, allowing simultaneous Braille chords without a diode matrix. The underside controller socket has two thirteen-contact rows, including the extra B− and B+ terminals. The provisional JST-PH battery connector feeds the battery-disconnect switch, then switched VBAT at the controller; battery negative returns to ground. The side reset connects RST to ground. The USB envelope is outside the main PCB edge.

Real copper routing is imported from Freerouting. One display MOSI connection remains unrouted, between MCU1 pad 20 and DISP1 pad 5, at the accepted controller/switch interference. The accepted header/switch-hole clashes are marked on `User.1`. The DRC report also records the nearby copper clearance issue, the two added battery contacts' 0.42 mm edge clearance against the default 0.5 mm rule, solder-mask and silkscreen findings. Missing external `ceoloide` library warnings do not remove the footprints embedded in the PCB.

This is a review draft for the requested manual KiCad correction, not a fabrication release. The power-switch mounting tabs were moved fully onto the PCB and reset was inset for edge clearance. The accepted controller clashes and key spacing were preserved. All 3D component solids are labelled dimension envelopes, not manufacturer models. Ring/fastener clearance in the preview depends on the provisional ring and flush screw heads.

An electrical schematic, ZMK firmware and an inter-module connection scheme are not included; those requirements have not been specified.

## Rebuild

Use Node.js/npm, Python with KiCad 9's `pcbnew` module, and `kicad-cli`. Mesh generation also needs the versions in `requirements-preview.txt`, installed in your Python environment or under `tools/pydeps`.

```sh
npm ci
npm run build
python3 scripts/prepare_kicad.py
python3 scripts/route_board.py --jar /path/to/freerouting-2.2.4.jar --java /path/to/java25
python3 scripts/render_review.py
npm run check
```

Routing uses Freerouting 2.2.4 and Java 25 or newer. The download bundle excludes installed dependencies, the Java runtime and the router binary. Rebuilding replaces generated outputs, so save manual KiCad changes separately first.

## References and notices

- [Ergogen documentation](https://docs.ergogen.xyz/)
- [nice!nano pinout and schematic](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/)
- [nice!view dimensions and specifications](https://nicekeyboards.com/nice-view/)
- [Ceoloide Ergogen footprints](https://github.com/ceoloide/ergogen-footprints)
- [Freerouting](https://github.com/freerouting/freerouting)

Upstream provenance is recorded in `ergogen/footprints/ceoloide/upstream.json`. Original per-file notices are preserved, including CC-BY-NC-SA-4.0 notices in the controller and display footprints; the repository's top-level MIT file does not replace those notices. The local controller adapter adds the battery-header row without discarding the upstream implementation.
