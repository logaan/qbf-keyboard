# QBF ten-key macro pad

Ten direct-wired Choc v1 switches for a Seeed Studio XIAO nRF52840 Plus running ZMK. The original eight portrait 1.5U caps are 16.5 × 26.5 mm, with 19.05 mm horizontal spacing and 27.5 mm row pitch for a 1 mm cap gap. A fifth column contains the controller with USB facing right and one portrait 1U key above and below it. The 1U caps are 16.5 × 17.5 mm ([MBK dimensions](https://shop.dailycraft.jp/en/products/keycaps_mbk)); their outer edges align with the original rows, leaving 0.6 mm to the controller. The PCB and base plate measure 100.65 × 55 mm.

## Files

- `design/config.yaml` — Ergogen layout, board outline, switch nets, and controller position.
- `design/footprints/choc_v1_15u_portrait.js` — rotated Choc v1 switch footprint with parameterized 1U/1.5U cap outlines.
- `design/footprints/xiao_nrf52840.js` — XIAO footprint for two 1×7, 2.54 mm socket strips; USB end points toward the right edge.
- `design/footprints/m2_mount.js` — four matching 2.2 mm M2 fastening holes between columns 1/2 and 3/4, in the main PCB and base plate.
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

The leg facing the center of the board connects to the labeled GPIO; the outer leg joins GND. The GPIO labels appear on the front silkscreen. ZMK uses its direct GPIO scanner with internal pull-ups and active-low inputs. The shield disables I²C and moves SPI to the Plus underside pins, leaving every key directly wired without diodes.

## Display prototype

The JDI LPM009M360A reflective memory LCD sits above the controller, between t5 and b5. Its landscape glass is 24.01 × 12.455 mm; the custom adapter is 25.5 × 18 mm, with 0.5 mm to each adjacent cap. The main board is 4.7 mm wider than the layout without a display. It has no backlight. The [manufacturer specification](https://file2.dzsc.com/product/23/06/15/1205976_145554084.pdf) lists typical panel power of 2 µW static and 7 µW at one full refresh per second, at 3 V. These exclude controller and adapter losses. [nice!view](https://nicekeyboards.com/nice-view/) lists roughly 10 µA and a 36 × 14 mm module.

Use **XIAO nRF52840 Plus**; the original XIAO lacks the necessary exposed pins. Its outer dimensions remain 21 × 17.8 mm. Five insulated jumpers connect the Plus underside pads to W1 beneath the controller:

| W1 pad | Signal | Plus pad | MCU pin |
| --- | --- | --- | --- |
| 1 | LCD_CLK | D17 | P1.03 |
| 2 | LCD_SI | D19 | P1.07 |
| 3 | LCD_CS | D18 | P1.05 |
| 4 | LCD_COM | D11 | P0.15 |
| 5 | LCD_EN | D12 | P0.19 |

`generated/pcbs/display.kicad_pcb` is an **unproven custom adapter**, not a ready-made display module. Fabricate it at 0.8 mm thickness. Connect its eight 1.27 mm solder positions to the corresponding LCD1 pads on the main PCB with short flexible insulated wires: CLK, SI, CS, COM, EN, 3V3, NC, GND. Pin 1 is the top end in the layout. Do not fit a vertical rigid header: it crosses the USB plug path. Use insulated supports placing the adapter underside 8 mm above the main PCB, with the socketed controller and wiring below 6.8 mm; route wires clear of the USB opening. The modeled display top is at most 9.744 mm above the PCB before adhesive.

The panel's 10.3 mm ribbon must fold beneath the glass. Its eight 0.5 mm pitch contacts require delicate direct soldering to adapter pads 9–16, matching panel pins 1–8; pin 7 stays unconnected. Check ribbon contact orientation against the manufacturer drawing before soldering. Insulate the ribbon and underside components from the controller. Fit one 0805 1 µF ceramic capacitor across pads 17/18 (VDD/GND), and one 0805 0.1 µF across 19/20 (DISP/GND). Source the exact panel and prove the ribbon bend, support height, USB plug clearance, solder access, and mechanical support on a prototype before ordering production boards.

The local Zephyr module drives the panel in monochrome at 144 × 72 landscape resolution. It sends changed frames at most once per second and pulses EXTCOMIN once per second for 0.5 Hz VCOM inversion. Blanking disables the panel and inversion timer. The base plate has two oval header-clearance slots.

## Base plate and MagSafe ring

The bottom plate follows [Horizon's circuit-free plate approach](https://github.com/skarrmann/horizon#pcbs): it shares the main board outline and has non-plated holes for the ten switches, XIAO socket pins, and four M2 fasteners. The switch lead openings are 2.8 mm to clear socket bodies and solder fillets; XIAO pin openings are 2.0 mm. The four M2 holes are at local board coordinates (18.275, 13.75), (56.375, 13.75), (18.275, 41.25), and (56.375, 41.25) mm, measured from the lower-left board corner. Their vertical spacing is 27.5 mm. They can anchor a neck strap or the optional printed bumpers.

The **outside face** of the base plate has four short alignment ticks on `B.SilkS` at the 23 mm radius. Center a 46 mm inner / 56 mm outer diameter MagSafe-compatible adhesive metal ring on those ticks. The ring may overlap clearance holes; check the purchased ring, solder joints, and adhesion before applying it. The ring is for magnetic attachment; the keyboard has no wireless charging circuit. The optional bumpers cover strips at the plate edges and can be removed for direct magnetic mounting.

## Switch socket option

Each Choc v1 signal pad is a 2.4 mm plated pad with a 1.6 mm finished drill. This supports direct soldering or the **Mill-Max 7305** solder-mount receptacle family, whose specified minimum mounting hole is 1.52 mm and whose flange is 1.96 mm diameter ([Mill-Max metric catalog, p. 179](https://www.mill-max.com/sites/default/files/external/catalog/2019-10/153M-201M_0.pdf)). Fit-test the exact Choc switch pins in the chosen receptacles before populating all 20 sockets. The board is not intended for Kailh surface-mount hot-swap sockets.

## Printed carrier

The printable bumper rails and reversible two-board case are in [`../mechanical/README.md`](../mechanical/README.md). The four M2 holes can also be used for strap attachment when the bumper is not fitted.

## Regenerate

```sh
./scripts/generate.sh
```

Run from the repository root with KiCad closed. Requires Node/npm and KiCad; override `KICAD_PYTHON` and `KICAD_CLI` if needed. The script installs missing dependencies, runs Ergogen, routes signals, fills GND, generates the base plate and display adapter, renders a layout preview, and runs KiCad DRC in a temporary directory before replacing outputs. Project settings are preserved. Reports are in `generated/checks/`. Run `./scripts/check.sh` to repeat DRC.

After changing dimensions or mounts, run `./scripts/generate-mechanical.sh` to rebuild the carrier from `generated/board_geometry.json`.

All three PCBs pass KiCad DRC. Firmware compiles against ZMK revision `4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85`. Physical assembly, display operation, power consumption, ribbon folding, cap travel, and Bluetooth antenna performance beneath the display have not been tested.

For ZMK, run `./scripts/build-firmware.sh /path/to/zmk-workspace` with west and the Zephyr SDK available. This includes the local display module and builds `qbf_macropad` for `xiao_ble//zmk` (see `build.yaml`). The sample keymap preserves 1–8 on the original keys and assigns 9/0 above/below the controller.
