# QBF 4×2 macro pad

An 8-key Choc v1 macro pad for a **Seeed Studio XIAO nRF52840** running ZMK. The keys use 1.5U caps in portrait orientation, with 18 mm column spacing and 50 mm row spacing to fit the controller between the rows. The XIAO sits near the right edge with its USB port facing outward. The drawn cap clearance assumes a 26.5 × 16.5 mm cap (common MBK 1.5U size). Every switch connects directly between one controller GPIO and GND. There is no row/column matrix and there are no diodes.

## Files

- `design/config.yaml` — Ergogen layout, board outline, switch nets, and controller position.
- `design/footprints/choc_v1_15u_portrait.js` — rotated Choc v1 switch footprint with 1.5U cap clearance outline.
- `design/footprints/xiao_nrf52840.js` — XIAO footprint for two 1×7, 2.54 mm socket strips; USB end points toward the right edge.
- `generated/pcbs/macropad.kicad_pcb` — generated KiCad PCB with routed signals and filled GND copper on both sides.
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

## Regenerate

```sh
./scripts/generate.sh
```

Run this from the repository root with the KiCad PCB editor closed. The script installs dependencies with `npm ci --allow-git=all` (needed with npm 12 because Ergogen 4.2.1 has Git-hosted dependencies), using an ignored project-local npm cache, then generates the PCB. Generation routes 0.30 mm signal tracks using only horizontal, vertical, and 45° segments, with no 90° turns and 1.8 mm spacing between parallel traces so GND copper fills the gaps. It fills front and back GND zones and checks for unconnected nets, clearance from pads and traces, and GND copper between each adjacent pair of signal traces. It centers the board on the A3 drawing and stamps the generation date in the title block. It requires KiCad's Python `pcbnew` module; on macOS the script uses the bundled interpreter at `/Applications/KiCad`. Set `KICAD_PYTHON` to another interpreter if needed. Regeneration overwrites the generated PCB while preserving the KiCad project settings. KiCad's local `.history` directory is not used for project versioning; use the repository instead.

Before fabrication, run KiCad's full DRC and verify the XIAO header and USB fit against the physical module. No firmware build or physical PCB validation has been performed.

For ZMK, use the `config` directory as your ZMK user config and build the `qbf_macropad` shield for `xiao_ble//zmk` (see `build.yaml`). The sample keymap sends 1–8 in visual order.
