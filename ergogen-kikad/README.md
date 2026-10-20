# QBF ten-key macro pad

Ten direct-wired Choc v1 switches, a socketed **nice!nano v2**, and a ready-made **nice!view** display running ZMK. All user soldering is through-hole: switches, controller sockets, and the five display connections, battery connector, and power/reset controls. The purchased modules arrive with their small components assembled.

The eight portrait 1.5U caps are 16.5 × 26.5 mm, with 19.05 mm horizontal spacing and a 1 mm row gap. The fifth column has two landscape 26.5 × 16.5 mm 1.5U caps ([MBK dimensions](https://shop.dailycraft.jp/en/products/keycaps_mbk)); all five outer cap edges align across each row. The fifth-column centers shift 5 mm right to keep the same 2.55 mm cap gap to column four. The controller shifts right to clear the display socket while the original four columns retain their pitch. The PCB and base plate measure **114.25 × 55 mm**.

## Files

- `design/config.yaml` — Ergogen layout, board outline, switch nets, and controller position.
- `design/footprints/choc_v1_15u_portrait.js` — rotated Choc v1 switch footprint with parameterized 1U/1.5U cap outlines.
- `design/footprints/nice_nano.js` — two 1×12, 2.54 mm controller socket strips; USB faces right.
- `design/footprints/nice_view.js` — module placement outline and a separate five-pin, 2.54 mm through-hole connection.
- `design/footprints/m2_mount.js` — six matching 2.2 mm M2 fastening holes between columns 1/2 and 3/4 and between column five and the controls, in the main PCB and base plate.
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

Mount the display horizontally above the nice!nano, between t5 and b5. LCD1 is a **direct five-pin through-hole socket** beneath the module's left-hand contacts. Solder the matching male header to the display and plug it into LCD1. The module sits at x = 83.9 mm; the controller moves to x = 87 mm, USB facing right. A 2.54 × 12.7 mm socket body clears the controller's conservative 36 × 18.3 mm envelope by 0.53 mm. The PCB grows 3.1 mm to preserve 0.5 mm at the controller's USB end. Key positions are unchanged; the outer screws now sit between column five and the controls.

Pin 1 is the top contact when viewing the board from above, with the display header on the left:

| LCD1 pad | Signal | nice!nano pin |
| --- | --- | --- |
| 1 | LCD_SI / SDA | D2 / P0.17 |
| 2 | LCD_CLK / SCL | D3 / P0.20 |
| 3 | 3V3 | VCC |
| 4 | GND | GND |
| 5 | LCD_CS / CS | D1 / P0.06 |

The [manufacturer dimension drawing](https://nicekeyboards.com/static/2f2592ff1ff8021932814b20cb76e3c4/821da/niceview_dimensions.png) places the header 1.3 mm from the module's left edge, at 2.54 mm pitch. LCD1 matches these contacts directly; no wires or adapter are required. Use a socket/header stack and low-profile controller sockets that put the display's lowest underside at 8 mm and the controller top below 6.8 mm. The display top then stays within the carrier's 11.3 mm protected clearance. Verify the actual socket stack, full cap travel, USB plug, and wireless operation on the prototype. Add an insulated support beneath the display's free end if needed.

Firmware uses ZMK's standard `nice_view` shield with the built-in landscape status screen. The former custom JDI adapter and driver have been removed.

## Battery, power and reset

The longer candidate is the protected **Liter Energy 301055, listed at 220 mAh** (formerly 110 mAh). [theStock's product listing](https://thestock.es/products/bateria-301055-lipo-3-7v-220mah-0-814wh-1s-5c-liter-energy-battery-para-electronica-recargable-telefono-portatil-video-smartwatch-reloj-gps-no-apta-para-radio-control-57x10x3mm-220mah-301055) specifies a PCM-protected pack, **57 × 10 × 3 mm ±0.5 mm**, 25 mm leads, and a 1C maximum charge rate. BAT1 reserves **57.5 × 10.5 × 3.5 mm**, including that tolerance. It is sold without a connector: have the supplier fit a correctly polarized JST-PH PHR-2 plug, or crimp one onto the existing insulated leads. Do not solder to the pouch tabs. Capacity and dimensions are supplier claims; no manufacturer pack drawing was located, and the listing contains inconsistent charge-current boilerplate. Confirm the finished pack envelope and at least 100 mA permissible charging with the supplier before ordering; leave charge boost off.

BAT1 is now centered at (30.4, 27.5) mm measured from the lower-left PCB corner. The original pack is shifted 0.75 mm right and recessed through a **58.1 × 11.1 mm opening in the main PCB only**. The baseplate remains continuous below the entire opening. A 0.2 mm insulating adhesive layer on its top puts the battery bottom at z=−1.4 mm and top at z=2.1 mm. The opening leaves 0.3 mm side clearance and a 1.35 mm left PCB web. Smooth and insulate the cut edges; do not allow the pouch or leads to rub against FR4.

The side-entry JST-PH near the controller stays in place, with 1 mm between the pack and mated-plug envelope. The new upper case guard has a continuous 1 mm roof at z=2.3 to 3.3 mm: 0.2 mm over the battery and 0.7 mm below the conservative fully depressed caps. Pack dimensions and lead geometry are recorded in `design/battery.json`; see [the three-part case guide](../bumper-case/README.md) for the screw stack, printing and assembly.

| Position | Part | Connection |
| --- | --- | --- |
| Between original rows, near controller | JST **S2B-PH-K-S**, 2 mm pitch, side-entry through-hole | J1 pin 1 = battery positive, pin 2 = GND |
| Beside t5, aligned with its horizontal center | 6 × 6 mm through-hole tactile, **4.3 mm high**, standard 6.5 × 4.5 mm pin pattern | RST1 momentarily connects nice!nano RST to GND |
| Beside b5, right | C&K **OS102011MS2QN1**, vertical actuator, through-hole | J1 positive → pin 1; common pin 2 → nice!nano RAW; pin 3 unconnected |

Both switches face upward and share x = 99.975 mm, halfway between the fifth-column cap right edge (94.45 mm) and PCB right edge (105.5 mm). Reset aligns with t5 at y = 32.5 mm; power aligns with b5 at y = −5 mm. Both footprints remain rotated 90°. Double-tap reset to enter the nice!nano bootloader. Battery negative stays connected to GND. The power slider disconnects battery positive from RAW in OFF; USB can still power the controller, and the battery only charges with the slider ON. Leave the nice!nano charge-boost jumper open for the 220 mAh candidate. Match the purchased battery plug polarity to J1's +/− markings.

The third M2 pair sits between column five and the reset/power controls, fully inside the orange bumper. Moving it 1 mm toward the fifth-column switches leaves standard 4 mm across-flats nuts 1.225 mm from the reset casing, 2.075 mm from the power casing, and 3.05 mm from the Choc switch shoulders. The outline is 114.25 × 55 mm. The base plate includes clearance slots for the battery and display headers and power-slider leads, plus four reset-lead holes. The carrier follows the revised screw positions.

## Base plate and MagSafe ring

The bottom plate follows [Horizon's circuit-free plate approach](https://github.com/skarrmann/horizon#pcbs): it shares the main board outline and has non-plated holes for the ten switches, controller socket pins, and six M2 fasteners. The switch lead openings are 2.8 mm to clear socket bodies and solder fillets; controller pin openings are 2.0 mm. Four M2 holes remain at x=18.275/56.375 mm and y=13.75/41.25 mm, measured from the lower-left corner. The outer pair is at (102.5, 8.75) and (102.5, 46.25) mm. The main PCB has the battery opening; the baseplate has no battery opening. They can anchor a neck strap or the optional printed bumpers.

The **outside face** of the base plate has four short alignment ticks on `B.SilkS` at the 23 mm radius. Center a 46 mm inner / 56 mm outer diameter MagSafe-compatible adhesive metal ring on those ticks. The ring may overlap clearance holes; check the purchased ring, solder joints, and adhesion before applying it. The ring is for magnetic attachment; the keyboard has no wireless charging circuit. The optional bumpers cover strips at the plate edges and can be removed for direct magnetic mounting.

## Switch socket option

Each Choc v1 signal pad is a 2.4 mm plated pad with a 1.6 mm finished drill. This supports direct soldering or the **Mill-Max 7305** solder-mount receptacle family, whose specified minimum mounting hole is 1.52 mm and whose flange is 1.96 mm diameter ([Mill-Max metric catalog, p. 179](https://www.mill-max.com/sites/default/files/external/catalog/2019-10/153M-201M_0.pdf)). Fit-test the exact Choc switch pins in the chosen receptacles before populating all 20 sockets. The board is not intended for Kailh surface-mount hot-swap sockets.

## Printed bumper case and carrier

The [three-part bumper case](../bumper-case/README.md) provides a lower switch plate, controller/control cover, and upward guard with a continuous battery roof. Its four left mounts need 1.2 mm M2 thin nuts; the two right mounts use standard 1.6 mm M2 nuts.

The printable bumper rails and reversible two-board case are in [`../mechanical/README.md`](../mechanical/README.md). The six M2 holes can also be used for strap attachment when the bumper is not fitted.

## Regenerate

```sh
./scripts/generate.sh
```

Run from the repository root with KiCad closed. Requires Node/npm, KiCad and FreeCAD; override `KICAD_PYTHON` and `KICAD_CLI` if needed. The script installs missing dependencies, runs Ergogen, routes signals, fills GND, generates the base plate, exports native KiCad assembly and copper SVG plots (`layout.svg` / `routing.svg`) and rasterizes them to PNG, and runs KiCad DRC plus native STEP verification of the main-board battery opening and intact baseplate floor before replacing outputs. Project settings are preserved. Reports are in `generated/checks/`. Run `./scripts/check.sh` to repeat DRC and `./scripts/check-battery-well.sh` to repeat the solid-floor proof. The floor report is `generated/checks/battery-well.json`. MCU1 GND pad 23 uses a solid zone connection to avoid an isolated thermal; allow for its extra soldering heat.

After changing dimensions or mounts, run `./scripts/generate-mechanical.sh` to rebuild the carrier from `generated/board_geometry.json`.

Both PCBs pass KiCad DRC. Firmware compiles against ZMK revision `4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85`. Physical assembly, display operation, power consumption, cap travel, and Bluetooth antenna performance beneath the display have not been tested.

For ZMK, run `./scripts/build-firmware.sh /path/to/zmk-workspace` with west and the Zephyr SDK available. This builds `qbf_macropad nice_view` for `nice_nano@2.0.0//zmk` (see `build.yaml`). The sample keymap preserves 1–8 on the original keys and assigns 9/0 above/below the controller.

## KiCad 3D views

Run `./scripts/render-3d.sh` after regeneration. `generated/assembly-3d.png` shows resting placement; `generated/inspection-3d.png` hides caps and the display to expose the battery and controller. The saved PCB retains its 3D models for KiCad’s viewer. See [model assumptions](design/models/README.md); the MBK meshes are rendering-only and several components use simplified dimension references. Full-travel clearance beneath caps remains unverified.
