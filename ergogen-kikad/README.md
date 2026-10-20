# QBF ten-key macro pad

Ten direct-wired Choc v1 switches, a socketed **nice!nano v2**, and a ready-made **nice!view** display running ZMK. All user soldering is through-hole: switches, controller sockets, and the five display connections, battery connector, and power/reset controls. The purchased modules arrive with their small components assembled.

The eight portrait 1.5U caps are 16.5 × 26.5 mm, with 19.05 mm horizontal spacing and a 1 mm row gap. The fifth column has two landscape 26.5 × 16.5 mm 1.5U caps ([MBK dimensions](https://shop.dailycraft.jp/en/products/keycaps_mbk)); all five outer cap edges align across each row. The fifth-column centers shift 5 mm right to keep the same 2.55 mm cap gap to column four. The controller shifts right beneath the display while the original four columns retain their pitch. The PCB and base plate measure **111.15 × 55 mm**, 10.5 mm wider than the former bare-panel version.

## Files

- `design/config.yaml` — Ergogen layout, board outline, switch nets, and controller position.
- `design/footprints/choc_v1_15u_portrait.js` — rotated Choc v1 switch footprint with parameterized 1U/1.5U cap outlines.
- `design/footprints/nice_nano.js` — two 1×12, 2.54 mm controller socket strips; USB faces right.
- `design/footprints/nice_view.js` — module placement outline and a separate five-pin, 2.54 mm through-hole connection.
- `design/footprints/m2_mount.js` — six matching 2.2 mm M2 fastening holes between columns 1/2 and 3/4 and between columns 4/5, in the main PCB and base plate.
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

Mount the display horizontally above the nice!nano, between t5 and b5. Its 14 mm height leaves 3.5 mm to each landscape cap, and its left edge clears column 4 by 0.5 mm. The controller footprint reserves a conservative 36 × 18.3 mm envelope. Fit the controller component-side up, USB facing right, using its two standard 12-pin rows. Leave the separate B+/B− holes outside those socket strips. The board requires no underside controller-pad soldering.

LCD1 is the vertical five-hole connection beside b5, next to the power slider. Pin 1 is its top end. Use short insulated wires from a through-hole header/socket here to the labeled nice!view pins, matching signal names:

| LCD1 pad | Signal | nice!nano pin |
| --- | --- | --- |
| 1 | GND | GND |
| 2 | 3V3 | VCC |
| 3 | LCD_CLK / SCL | D3 / P0.20 |
| 4 | LCD_SI / SDA | D2 / P0.17 |
| 5 | LCD_CS / CS | D1 / P0.06 |

The header is displaced below the controller to keep a rigid connector out of the USB plug path. Support the module on insulated spacers, with its underside 8 mm above the PCB and the socketed controller below 6.8 mm. This places the display top at 10.9 mm, within the carrier's modeled 11.3 mm protected clearance. Check the purchased sockets, support height, cap travel, USB plug, and wireless performance on the assembled prototype. No custom display PCB, ribbon connection, or surface-mount component needs soldering.

Firmware uses ZMK's standard `nice_view` shield with the built-in landscape status screen. The former custom JDI adapter and driver have been removed.

## Battery, power and reset

Use a protected 3.7 V **301230, 110 mAh LiPo** with a JST-PH 2-pin plug. The selected [VCELL VP301230 specification](https://vcellpower-battery.com/3.7v/3-7v-110mah-301230-mini-lipo-battery-with-connector.html) gives a maximum pack size of **32.5 × 12.5 × 3.2 mm including PCM**, and a 110 mA maximum charge current. Specify a JST-PH plug when ordering this pack; its connector is configurable. [KEEBD](https://keebd.com/products/301230-3-7v-110mah-lipo-battery) also lists a nominal 30 × 12 × 3 mm protected 110 mAh pack with PH connector options. Packs sharing a size code can have different protection boards and charge limits; use the specified envelope and charge rating.

BAT1 marks the pack envelope on `Cmts.User`, centered between the original switch rows and spanning columns 2/3. The nominal footprint body gap is 13.5 mm, leaving 0.5 mm per side around the 12.5 mm pack envelope. A 0.2 mm insulating adhesive layer puts its top 3.4 mm above the PCB. There are no drilled holes or exposed pads inside this rectangle. The exact cap underside and full-travel clearance still require an assembled fit check; do not use the caps to hold the pouch under pressure. Route the insulated leads through the central channel and beneath the socketed controller to J1, clear of moving keys and the USB port.

| Position | Part | Connection |
| --- | --- | --- |
| Beside t5, lower | JST **B2B-PH-K-S**, 2 mm pitch, vertical through-hole | J1 pin 1 = battery positive, pin 2 = GND |
| Beside t5, upper | 6 × 6 mm through-hole tactile, **4.3 mm high**, standard 6.5 × 4.5 mm pin pattern | RST1 momentarily connects nice!nano RST to GND |
| Beside b5, right | C&K **OS102011MS2QN1**, vertical actuator, through-hole | J1 positive → pin 1; common pin 2 → nice!nano RAW; pin 3 unconnected |

Both switches face upward. The reset footprint is rotated so its leads fit within the existing outline. Double-tap reset to enter the nice!nano bootloader. Battery negative stays connected to GND. The power slider disconnects battery positive from RAW in OFF; USB can still power the controller, and the battery only charges with the slider ON. Leave the nice!nano charge-boost jumper open for the 110 mAh pack. Match the purchased battery plug polarity to J1's +/− markings.

The third M2 pair now sits between columns 4/5, leaving the right-hand corners for controls. The outline remains 111.15 × 55 mm. The base plate includes clearance slots for the battery and display headers and power-slider leads, plus four reset-lead holes. The carrier follows the revised screw positions.

## Base plate and MagSafe ring

The bottom plate follows [Horizon's circuit-free plate approach](https://github.com/skarrmann/horizon#pcbs): it shares the main board outline and has non-plated holes for the ten switches, controller socket pins, and six M2 fasteners. The switch lead openings are 2.8 mm to clear socket bodies and solder fillets; controller pin openings are 2.0 mm. The six M2 holes use local x coordinates 18.275, 56.375, and 75.425 mm at y = 13.75 and 41.25 mm, measured from the lower-left board corner. Their vertical spacing is 27.5 mm. They can anchor a neck strap or the optional printed bumpers.

The **outside face** of the base plate has four short alignment ticks on `B.SilkS` at the 23 mm radius. Center a 46 mm inner / 56 mm outer diameter MagSafe-compatible adhesive metal ring on those ticks. The ring may overlap clearance holes; check the purchased ring, solder joints, and adhesion before applying it. The ring is for magnetic attachment; the keyboard has no wireless charging circuit. The optional bumpers cover strips at the plate edges and can be removed for direct magnetic mounting.

## Switch socket option

Each Choc v1 signal pad is a 2.4 mm plated pad with a 1.6 mm finished drill. This supports direct soldering or the **Mill-Max 7305** solder-mount receptacle family, whose specified minimum mounting hole is 1.52 mm and whose flange is 1.96 mm diameter ([Mill-Max metric catalog, p. 179](https://www.mill-max.com/sites/default/files/external/catalog/2019-10/153M-201M_0.pdf)). Fit-test the exact Choc switch pins in the chosen receptacles before populating all 20 sockets. The board is not intended for Kailh surface-mount hot-swap sockets.

## Printed carrier

The printable bumper rails and reversible two-board case are in [`../mechanical/README.md`](../mechanical/README.md). The six M2 holes can also be used for strap attachment when the bumper is not fitted.

## Regenerate

```sh
./scripts/generate.sh
```

Run from the repository root with KiCad closed. Requires Node/npm and KiCad; override `KICAD_PYTHON` and `KICAD_CLI` if needed. The script installs missing dependencies, runs Ergogen, routes signals, fills GND, generates the base plate, renders a layout preview, and runs KiCad DRC in a temporary directory before replacing outputs. Project settings are preserved. Reports are in `generated/checks/`. Run `./scripts/check.sh` to repeat DRC.

After changing dimensions or mounts, run `./scripts/generate-mechanical.sh` to rebuild the carrier from `generated/board_geometry.json`.

Both PCBs pass KiCad DRC. Firmware compiles against ZMK revision `4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85`. Physical assembly, display operation, power consumption, cap travel, and Bluetooth antenna performance beneath the display have not been tested.

For ZMK, run `./scripts/build-firmware.sh /path/to/zmk-workspace` with west and the Zephyr SDK available. This builds `qbf_macropad nice_view` for `nice_nano@2.0.0//zmk` (see `build.yaml`). The sample keymap preserves 1–8 on the original keys and assigns 9/0 above/below the controller.
