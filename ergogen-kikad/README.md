# QBF ten-key macro pad

Ten direct-wired Choc v1 switches for a Seeed Studio XIAO nRF52840 running ZMK. The original eight portrait 1.5U caps are 16.5 × 26.5 mm, with 19.05 mm horizontal spacing and 27.5 mm row pitch for a 1 mm cap gap. A fifth column contains the controller with USB facing right and one portrait 1U key above and below it. The 1U caps are 16.5 × 17.5 mm ([MBK dimensions](https://shop.dailycraft.jp/en/products/keycaps_mbk)); their outer edges align with the original rows, leaving 0.6 mm to the controller. The PCB and base plate measure 95.95 × 60.5 mm.

## Files

- `design/config.yaml` — Ergogen layout, board outline, switch nets, and controller position.
- `design/footprints/choc_v1_15u_portrait.js` — rotated Choc v1 switch footprint with parameterized 1U/1.5U cap outlines.
- `design/footprints/xiao_nrf52840.js` — XIAO footprint for two 1×7, 2.54 mm socket strips; USB end points toward the right edge.
- `design/footprints/m2_mount.js` — four matching 2.2 mm M2 fastening holes, two near each side edge, in the main PCB and base plate.
- `generated/pcbs/macropad.kicad_pcb` — generated KiCad PCB with routed signals and filled GND copper on both sides.
- `generated/pcbs/baseplate.kicad_pcb` — separate, circuit-free FR4 bottom plate with cutouts for every through-hole lead and locating pin.
- `../scripts/route_board.py` — routing, ground fills, base plate, and layout checks.
- `config/boards/shields/qbf_macropad/` — ZMK shield and default keymap.

## Wiring

| Key position | PCB net | XIAO pin | Default key |
| --- | --- | --- | --- |
| Top left | D6 | D6 | 1 |
| Top second | D5 | D5 | 2 |
| Top third | D4 | D4 | 3 |
| Top fourth | D3 | D3 | 4 |
| Above controller | D0 | D0 | 9 |
| Bottom left | D7 | D7 | 5 |
| Bottom second | D8 | D8 | 6 |
| Bottom third | D9 | D9 | 7 |
| Bottom fourth | D10 | D10 | 8 |
| Below controller | D1 | D1 | 0 |

The leg facing the center of the board connects to the labeled GPIO; the outer leg joins GND. The GPIO labels appear on the front silkscreen. ZMK uses its direct GPIO scanner with internal pull-ups and active-low inputs. The shield disables the XIAO's default I²C and SPI peripherals so those shared pins remain available for switches.

## Base plate and MagSafe ring

The bottom plate follows [Horizon's circuit-free plate approach](https://github.com/skarrmann/horizon#pcbs): it shares the main board outline and has non-plated holes for the ten switches, XIAO socket pins, and four M2 fasteners. The switch lead openings are 2.8 mm to clear socket bodies and solder fillets; XIAO pin openings are 2.0 mm. The four M2 holes are at local board coordinates (4.0, 2.75), (91.95, 2.75), (4.0, 57.75), and (91.95, 57.75) mm, measured from the lower-left board corner. Their vertical spacing is 55 mm. They can anchor a neck strap or the optional printed bumpers.

The **outside face** of the base plate has four short alignment ticks on `B.SilkS` at the 23 mm radius. Center a 46 mm inner / 56 mm outer diameter MagSafe-compatible adhesive metal ring on those ticks. The ring may overlap clearance holes; check the purchased ring, solder joints, and adhesion before applying it. The ring is for magnetic attachment; the keyboard has no wireless charging circuit. The optional bumpers cover strips at the plate edges and can be removed for direct magnetic mounting.

## Switch socket option

Each Choc v1 signal pad is a 2.4 mm plated pad with a 1.6 mm finished drill. This supports direct soldering or the **Mill-Max 7305** solder-mount receptacle family, whose specified minimum mounting hole is 1.52 mm and whose flange is 1.96 mm diameter ([Mill-Max metric catalog, p. 179](https://www.mill-max.com/sites/default/files/external/catalog/2019-10/153M-201M_0.pdf)). Fit-test the exact Choc switch pins in the chosen receptacles before populating all 20 sockets. The board is not intended for Kailh surface-mount hot-swap sockets.

## Printed carrier

The printable bumper rails and reversible two-board case are in [`../mechanical/README.md`](../mechanical/README.md). The four M2 holes can also be used for strap attachment when the bumper is not fitted.

## Regenerate

```sh
./scripts/generate.sh
```

Run from the repository root with KiCad closed. Requires Node/npm and KiCad; override `KICAD_PYTHON` and `KICAD_CLI` if needed. The script installs missing dependencies, runs Ergogen, routes signals, fills GND, generates the base plate, and runs KiCad DRC in a temporary directory before replacing outputs. Project settings are preserved. Reports are in `generated/checks/`. Run `./scripts/check.sh` to repeat DRC.

After changing dimensions or mounts, run `./scripts/generate-mechanical.sh` to rebuild the carrier from `generated/board_geometry.json`.

Before fabrication, run KiCad's full DRC on both PCBs and verify the XIAO header, USB, and base plate clearances against the physical parts. No firmware build or physical PCB validation has been performed.

For ZMK, use the `config` directory as your ZMK user config and build the `qbf_macropad` shield for `xiao_ble//zmk` (see `build.yaml`). The sample keymap preserves 1–8 on the original keys and assigns 9/0 above/below the controller.
