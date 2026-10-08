# QBF 4×2 macro pad

An 8-key Choc v1 macro pad for a **Seeed Studio XIAO nRF52840** running ZMK. The keys use 1.5U caps in portrait orientation, with 19.05 mm horizontal spacing as on the [Sofle Choc](https://github.com/josefadamcik/SofleKeyboard/tree/master/Sofle_Choc/PCB). The row pitch is 34 mm and the board outline is 73.65 × 60.5 mm, the bounding rectangle of the modeled 26.5 × 16.5 mm caps. The XIAO sits between the switch rows with a modeled 1.1 mm gap to each 14 mm switch body. Its USB port faces the right edge. Every switch connects directly between one controller GPIO and GND. There is no row/column matrix and there are no diodes.

## Files

- `design/config.yaml` — Ergogen layout, board outline, switch nets, and controller position.
- `design/footprints/choc_v1_15u_portrait.js` — rotated Choc v1 switch footprint with 1.5U cap clearance outline.
- `design/footprints/xiao_nrf52840.js` — XIAO footprint for two 1×7, 2.54 mm socket strips; USB end points toward the right edge.
- `design/footprints/m2_mount.js` — four matching 2.2 mm M2 fastening holes, two near each side edge, in the main PCB and base plate.
- `generated/pcbs/macropad.kicad_pcb` — generated KiCad PCB with routed signals and filled GND copper on both sides.
- `generated/pcbs/baseplate.kicad_pcb` — separate, circuit-free FR4 bottom plate with cutouts for every through-hole lead and locating pin.
- `scripts/route_board.py` — repeatable routing and connectivity/clearance checks for this fixed layout.
- `config/boards/shields/qbf_macropad/` — ZMK shield and default keymap.

## Wiring

| Key position | PCB net | XIAO pin | Default key |
| --- | --- | --- | --- |
| Top left | D6 | D6 | 1 |
| Top second | D5 | D5 | 2 |
| Top third | D4 | D4 | 3 |
| Top right | D3 | D3 | 4 |
| Bottom left | D7 | D7 | 5 |
| Bottom second | D8 | D8 | 6 |
| Bottom third | D9 | D9 | 7 |
| Bottom right | D10 | D10 | 8 |

The leg facing the center of the board connects to the labeled GPIO; the outer leg joins GND. The GPIO labels appear on the front silkscreen. ZMK uses its direct GPIO scanner with internal pull-ups and active-low inputs. The shield disables the XIAO's default I²C and SPI peripherals so those shared pins remain available for switches.

## Base plate and MagSafe ring

The bottom plate follows [Horizon's circuit-free plate approach](https://github.com/skarrmann/horizon#pcbs): it shares the main board outline and has non-plated holes for the eight switches, XIAO socket pins, and four M2 fasteners. The switch lead openings are 2.8 mm to clear socket bodies and solder fillets; XIAO pin openings are 2.0 mm. The four M2 holes are at local board coordinates (3.5, 2.75), (70.15, 2.75), (3.5, 57.75), and (70.15, 57.75) mm, measured from the lower-left board corner. Their vertical spacing is 55 mm. They can anchor a neck strap or the optional printed bumpers.

The **outside face** of the base plate has four short alignment ticks on `B.SilkS` at the 23 mm radius. Center a 46 mm inner / 56 mm outer diameter MagSafe-compatible adhesive metal ring on those ticks. The ring may overlap clearance holes; check the purchased ring, solder joints, and adhesion before applying it. The ring is for magnetic attachment; the keyboard has no wireless charging circuit. The optional bumpers cover strips at the plate edges and can be removed for direct magnetic mounting.

## Switch socket option

Each Choc v1 signal pad is a 2.4 mm plated pad with a 1.6 mm finished drill. This supports direct soldering or the **Mill-Max 7305** solder-mount receptacle family, whose specified minimum mounting hole is 1.52 mm and whose flange is 1.96 mm diameter ([Mill-Max metric catalog, p. 179](https://www.mill-max.com/sites/default/files/external/catalog/2019-10/153M-201M_0.pdf)). Fit-test the exact Choc switch pins in the chosen receptacles before populating all 16 sockets. The board is not intended for Kailh surface-mount hot-swap sockets.

## Printed carrier

The printable bumper rails and reversible two-board case are in [`../mechanical/README.md`](../mechanical/README.md). The four M2 holes can also be used for strap attachment when the bumper is not fitted.

## Regenerate

```sh
./scripts/generate.sh
```

Run this from the repository root with the KiCad PCB editor closed. The script installs dependencies with `npm ci --allow-git=all` (needed with npm 12 because Ergogen 4.2.1 has Git-hosted dependencies), using an ignored project-local npm cache, then generates both PCBs. Generation routes 0.30 mm signal tracks using only horizontal, vertical, and 45° segments, with no 90° turns. Signals alternate between front and back copper to fit the compact row spacing. It fills front and back GND zones and checks for unconnected nets and clearance from pads and traces. It creates the base plate from the same board outline and hole positions and strips its nets and silkscreen labels. It centers each board on the A3 drawing and stamps the generation date in the title block. It requires KiCad's Python `pcbnew` module; on macOS the script uses the bundled interpreter at `/Applications/KiCad`. Set `KICAD_PYTHON` to another interpreter if needed. Regeneration overwrites the generated PCBs while preserving the KiCad project settings. KiCad's local `.history` directory is not used for project versioning; use the repository instead.

Before fabrication, run KiCad's full DRC on both PCBs and verify the XIAO header, USB, and base plate clearances against the physical parts. No firmware build or physical PCB validation has been performed.

For ZMK, use the `config` directory as your ZMK user config and build the `qbf_macropad` shield for `xiao_ble//zmk` (see `build.yaml`). The sample keymap sends 1–8 in visual order.
