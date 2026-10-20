# QBF ten-key board

Ten direct-wired Kailh Choc v1 keys and a recessed Seeed XIAO nRF52840 Plus, with no display or separate reset. The main PCB and circuit-free baseplate are **97.7 × 58.5 mm**, nominally 1.6 mm each. Eight portrait 1.5U caps are 16.5 × 26.5 mm; t5/b5 use 17.5 × 16.5 mm 1U caps. Key geometry is symmetric about y48, with 19.05 mm main column pitch, 27.5 mm main row pitch and aligned outer cap edges. Four M2 holes secure the stack. At least 2.25 mm of PCB surrounds the outer caps.

The controller is in an open-right cutout, USB facing right. It rests on insulating film over the baseplate and uses controlled hand-solder bridges to its native castellations. This mounting process needs a sample trial. Read the [assembly requirements](design/ASSEMBLY.md), including the **0.2 mm edge-copper fabrication requirement**, before ordering boards. The retained protected 301055 pack occupies its own main-PCB-only well, on an intact insulated baseplate floor. Power is a left-facing C&K PCM12 slider entirely inside the PCB outline; the battery connector is JST-SH.

## Wiring

| Key | XIAO net | nRF52840 GPIO | Default key |
| --- | --- | --- | --- |
| t1 | D0 | P0.02 | 1 |
| t2 | D1 | P0.03 | 2 |
| t3 | D2 | P0.28 | 3 |
| t4 | D3 | P0.29 | 4 |
| t5 | D4 | P0.04 | 9 |
| b1 | D5 | P0.05 | 5 |
| b2 | D6 | P1.11 | 6 |
| b3 | D7 | P1.12 | 7 |
| b4 | D8 | P1.13 | 8 |
| b5 | D9 | P1.14 | 0 |

Each switch connects its GPIO directly to GND. Firmware uses internal pull-ups and active-low inputs; no diodes or matrix are fitted. Standard XIAO castellations 1..14 preserve D0..D10, 3V3, GND and VBUS. The nine extra Plus castellations remain unconnected and clear of the solder bridges.

JST-SH pad 1 is battery positive and pad 2 is GND. PCM12 pad 3 receives battery positive; common pad 2 feeds BW1, whose insulated underside wire connects to XIAO BAT+. The unused throw is pad 1. USB can power the controller with battery switched off; charging the pack requires the switch on. Keep the native approximately 50 mA charging setting. Check factory plug polarity and the protected pack's finished dimensions.

## Sources and outputs

- [Ergogen configuration](design/config.yaml) and [footprint sources](design/footprints/) define layout and nets.
- [Assembly parameters](design/assembly.json) and [battery envelope](design/battery.json) record mounting and source dimensions.
- [Official XIAO project snapshots](design/sources/) establish native contacts and component locations.
- [Main PCB](generated/pcbs/macropad.kicad_pcb) and [circuit-free baseplate](generated/pcbs/baseplate.kicad_pcb) are routed/generated KiCad outputs.
- [Layout preview](generated/layout.png), [copper preview](generated/routing.png), [assembled preview](generated/assembly-3d.png) and [cap-free inspection](generated/inspection-3d.png) use native KiCad plots/renders.
- [Assembly contract](generated/assembly-contract.json) records poses, board/source hashes, Z stack and operating clearances for the later case stage.
- [Model assumptions](design/models/README.md) distinguish supplier STEP, rendering mesh and simplified references.

The fixed frame has x right, y up and main PCB top z0. PCB bounds are x0.4..98.1, y18.75..77.25. `generated/board_geometry.json` records both the lower-left PCB frame and its KiCad page translation; the contract records the fixed assembly frame. The main PCB occupies z−1.6..0, baseplate z−3.2..−1.6, battery z−1.4..2.1, and supported module PCB z−1.55..0.05.

## Regenerate and verify

With KiCad closed, run from the repository root:

```sh
./scripts/generate.sh
./scripts/build-3d-models.sh
./scripts/generate.sh
./scripts/check-assembly.sh
./scripts/render-3d.sh
```

Node/npm, KiCad and FreeCAD are required. The first generation establishes the actual baseplate; model rebuilding exports its native shape, and the second attaches the complete assembly. Board generation is transactional: both native DRC reports and the STEP battery-floor proof must pass before replacing production outputs. `./scripts/check.sh` repeats DRC; `./scripts/check-battery-well.sh` repeats the continuous-floor proof. Reports live in `generated/checks/`.

The assembly check uses actual native PCB solids and filled copper, tests all 23 XIAO castellations, four fasteners, full cap travel, battery, connector reserve, complete power stroke, USB reference-cable access and a 2 mm onboard-reset probe. Its limits remain explicit: purchased hardware, solder process, actual cap cavity/clip seating, module thickness and wireless performance require a prototype. The current case files belong to the earlier design; the separate mechanical stage follows the reviewed firmware stage.

## Firmware

The [shield and numerical keymap](config/boards/shields/qbf_macropad/) build for `xiao_ble/nrf52840/zmk`. Each board works independently over USB or Bluetooth; split transport and display are disabled. The numerical map above is preserved. P0.13 is explicitly an input without pulls, retaining the native approximately 50 mA charge setting.

```sh
./scripts/build-firmware.sh /path/to/zmk-repository
```

Pass the directory containing `app/`, within an initialized west workspace. Run with west and the Zephyr SDK available. The build script resolves the actual Zephyr tree from its build cache and checks compiled GPIOs, pull-ups, standalone settings, key transform and charge input. The retained [UF2](generated/firmware/qbf_macropad.uf2) and [validation report](generated/firmware/validation.json) were built offline with ZMK revision `4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85` in the existing ZMK build container. Both halves may use this same standalone image. Double-tap the onboard reset to enter the supplied UF2 bootloader, then copy the UF2 to its mounted drive. Hardware flashing, key input and charging remain to be tested on a physical prototype.
