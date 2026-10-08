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
| Top left | K0 | D0 | 1 |
| Top second | K1 | D1 | 2 |
| Top third | K2 | D2 | 3 |
| Top right | K3 | D3 | 4 |
| Bottom left | K4 | D4 | 5 |
| Bottom second | K5 | D5 | 6 |
| Bottom third | K6 | D6 | 7 |
| Bottom right | K7 | D7 | 8 |

The other terminal of each switch joins GND. ZMK uses its direct GPIO scanner with internal pull-ups and active-low inputs.

## Regenerate

```sh
npm ci --allow-git=all
npm run generate
```

`--allow-git=all` is needed with npm 12 because Ergogen 4.2.1 has Git-hosted dependencies. `npm run generate` creates the layout, routes 0.30 mm signal tracks, fills front and back GND zones, and checks for unconnected nets plus 0.25 mm trace clearance from other pads, non-plated holes, and traces. It requires KiCad's Python `pcbnew` module; on macOS the script uses the bundled interpreter at `/Applications/KiCad`. Set `KICAD_PYTHON` to another interpreter if needed. Regeneration overwrites the generated PCB.

Before fabrication, run KiCad's full DRC and verify the XIAO header and USB fit against the physical module. The command-line DRC did not start in this environment, and no firmware build or physical PCB validation has been performed.

For ZMK, use the `config` directory as your ZMK user config and build the `qbf_macropad` shield for `xiao_ble//zmk` (see `build.yaml`). The sample keymap sends 1–8 in visual order.
