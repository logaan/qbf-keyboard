# QBF ten-key macro pad

Ten direct-wired Choc v1 switches, a socketed **nice!nano v2**, and a ready-made **nice!view** display running ZMK. All user soldering is through-hole: switches, controller sockets, and the five display connections. The purchased modules arrive with their small components assembled.

The eight portrait 1.5U caps are 16.5 × 26.5 mm, with 19.05 mm horizontal spacing and a 1 mm row gap. The fifth column has two 16.5 × 17.5 mm 1U caps ([MBK dimensions](https://shop.dailycraft.jp/en/products/keycaps_mbk)); all five outer cap edges align across each row. The controller shifts right beneath the display while key positions retain their pitch. The PCB and base plate measure **111.15 × 55 mm**, 10.5 mm wider than the former bare-panel version.

## Files

- `design/config.yaml` — Ergogen layout, board outline, switch nets, and controller position.
- `design/footprints/choc_v1_15u_portrait.js` — rotated Choc v1 switch footprint with parameterized 1U/1.5U cap outlines.
- `design/footprints/nice_nano.js` — two 1×12, 2.54 mm controller socket strips; USB faces right.
- `design/footprints/nice_view.js` — module placement outline and a separate five-pin, 2.54 mm through-hole connection.
- `design/footprints/m2_mount.js` — four matching 2.2 mm M2 fastening holes between columns 1/2 and 3/4, in the main PCB and base plate.
- `generated/pcbs/macropad.kicad_pcb` — generated KiCad PCB with routed signals and filled GND copper on both sides.
- `generated/pcbs/baseplate.kicad_pcb` — separate, circuit-free FR4 bottom plate with cutouts for every through-hole lead and locating pin.
- `../scripts/route_board.py` — routing, ground fills, base plate, and layout checks.
- `config/boards/shields/qbf_macropad/` — ZMK shield and default keymap.

## Wiring

| Key | PCB net / nice!nano Pro Micro pin | Default key |
| --- | --- | --- |
| t1 | P4 / D4 | 1 |
| t2 | P5 / D5 | 2 |
| t3 | P6 / D6 | 3 |
| t4 | P7 / D7 | 4 |
| t5 | P8 / D8 | 9 |
| b1 | P9 / D9 | 5 |
| b2 | P10 / D10 | 6 |
| b3 | P16 / D16 | 7 |
| b4 | P14 / D14 | 8 |
| b5 | P15 / D15 | 0 |

Each switch connects directly to its GPIO and GND. ZMK uses internal pull-ups and active-low inputs. No diodes or matrix are fitted. I²C is disabled so D2/D3 can serve the display SPI bus.

## Ready-made display

Use a complete [nice!view module](https://nicekeyboards.com/nice-view/), not a bare Sharp panel. Its manufacturer lists 36 × 14 × 2.9 mm, 160 × 68 pixels, 3.3 V, and approximately 10 µA typical draw. The [open-source HillSideView keyboard README](https://github.com/wannabecoffeenerd/HillSideView) names nice!view and nice!nano in its BOM; this confirms prior keyboard use without schematic inspection. The [manufacturer assembly guide](https://nicekeyboards.com/docs/nice-view/getting-started/) specifies five-pin through-hole headers and sockets.

Mount the display horizontally above the nice!nano, between t5 and b5. Its 14 mm height leaves 2.5 mm to each cap, and its left edge clears column 4 by 0.5 mm. The controller footprint reserves a conservative 36 × 18.3 mm envelope. Fit the controller component-side up, USB facing right, using its two standard 12-pin rows. Leave the separate B+/B− holes outside those socket strips. The board requires no underside controller-pad soldering.

LCD1 is the vertical five-hole connection beside t5. Pin 1 is its top end. Use short insulated wires from a through-hole header/socket here to the labeled nice!view pins, matching signal names:

| LCD1 pad | Signal | nice!nano pin |
| --- | --- | --- |
| 1 | GND | GND |
| 2 | 3V3 | VCC |
| 3 | LCD_CLK / SCL | D3 / P0.20 |
| 4 | LCD_SI / SDA | D2 / P0.17 |
| 5 | LCD_CS / CS | D1 / P0.06 |

The header is displaced above the controller to keep a rigid connector out of the USB plug path. Support the module on insulated spacers, with its underside 8 mm above the PCB and the socketed controller below 6.8 mm. This places the display top at 10.9 mm, within the carrier's modeled 11.3 mm protected clearance. Check the purchased sockets, support height, cap travel, USB plug, and wireless performance on the assembled prototype. No custom display PCB, ribbon connection, or surface-mount component needs soldering.

Firmware uses ZMK's standard `nice_view` shield with the built-in landscape status screen. The former custom JDI adapter and driver have been removed.

## Base plate and MagSafe ring

The bottom plate follows [Horizon's circuit-free plate approach](https://github.com/skarrmann/horizon#pcbs): it shares the main board outline and has non-plated holes for the ten switches, controller socket pins, and four M2 fasteners. The switch lead openings are 2.8 mm to clear socket bodies and solder fillets; Controller pin openings are 2.0 mm. The four M2 holes are at local board coordinates (18.275, 13.75), (56.375, 13.75), (18.275, 41.25), and (56.375, 41.25) mm, measured from the lower-left board corner. Their vertical spacing is 27.5 mm. They can anchor a neck strap or the optional printed bumpers.

The **outside face** of the base plate has four short alignment ticks on `B.SilkS` at the 23 mm radius. Center a 46 mm inner / 56 mm outer diameter MagSafe-compatible adhesive metal ring on those ticks. The ring may overlap clearance holes; check the purchased ring, solder joints, and adhesion before applying it. The ring is for magnetic attachment; the keyboard has no wireless charging circuit. The optional bumpers cover strips at the plate edges and can be removed for direct magnetic mounting.

## Switch socket option

Each Choc v1 signal pad is a 2.4 mm plated pad with a 1.6 mm finished drill. This supports direct soldering or the **Mill-Max 7305** solder-mount receptacle family, whose specified minimum mounting hole is 1.52 mm and whose flange is 1.96 mm diameter ([Mill-Max metric catalog, p. 179](https://www.mill-max.com/sites/default/files/external/catalog/2019-10/153M-201M_0.pdf)). Fit-test the exact Choc switch pins in the chosen receptacles before populating all 20 sockets. The board is not intended for Kailh surface-mount hot-swap sockets.

## Printed carrier

The printable bumper rails and reversible two-board case are in [`../mechanical/README.md`](../mechanical/README.md). The four M2 holes can also be used for strap attachment when the bumper is not fitted.

## Regenerate

```sh
./scripts/generate.sh
```

Run from the repository root with KiCad closed. Requires Node/npm and KiCad; override `KICAD_PYTHON` and `KICAD_CLI` if needed. The script installs missing dependencies, runs Ergogen, routes signals, fills GND, generates the base plate, renders a layout preview, and runs KiCad DRC in a temporary directory before replacing outputs. Project settings are preserved. Reports are in `generated/checks/`. Run `./scripts/check.sh` to repeat DRC.

After changing dimensions or mounts, run `./scripts/generate-mechanical.sh` to rebuild the carrier from `generated/board_geometry.json`.

Both PCBs pass KiCad DRC. Firmware compiles against ZMK revision `4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85`. Physical assembly, display operation, power consumption, cap travel, and Bluetooth antenna performance beneath the display have not been tested.

For ZMK, run `./scripts/build-firmware.sh /path/to/zmk-workspace` with west and the Zephyr SDK available. This builds `qbf_macropad nice_view` for `nice_nano@2.0.0//zmk` (see `build.yaml`). The sample keymap preserves 1–8 on the original keys and assigns 9/0 above/below the controller.
