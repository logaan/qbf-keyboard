# Mikoto automated test fixture — research, 13 October 2026

The plan is viable **provided the target still has working power, USB, reset and a bootloader**. A SuperMini cannot repair a damaged processor or USB connector by flashing it. Bootloader enumeration is itself a useful first diagnostic.

## Findings

- [KEEBD's Mikoto listing](https://keebd.com/products/mikoto-controller) specifies nRF52840 and an Adafruit bootloader with UF2 support. [KEEBD's SuperMini listing](https://keebd.com/products/supermini-controller) identifies the nRF52840 nice!nano-compatible board; this is not an ESP32 or RP2040 SuperMini.
- The [Adafruit bootloader](https://github.com/adafruit/Adafruit_nRF52_Bootloader) detects two resets within **500 ms**. Reset is active low: briefly sink RESET to GND, release, then repeat. The fixture uses 50 ms low, 150 ms released, 50 ms low. Both boards remain powered by their own USB cables.
- The [Mikoto bootloader definition](https://github.com/adafruit/Adafruit_nRF52_Bootloader/blob/master/src/boards/mikoto/board.h) sets a 3.3 V GPIO supply, volume label `MIKOTO-BOOT`, Board-ID `nRF52840-mikoto-rev520`. That identifier names the bootloader build; it does **not** reliably identify the physical PCB revision.
- The [designer's revision notes](https://github.com/zhiayang/mikoto/blob/master/CHANGELOG.md) document different header power pins and a D6 change between 5.x and 6.x. This fixture leaves power pins alone and uses D1–D4, whose mappings remain P0.08, P0.17, P0.20, P0.22 in both the [v5](https://github.com/zmkfirmware/zmk/blob/main/app/module/boards/zhiayang/mikoto/arduino_pro_micro_pins_v5.dtsi) and [v6](https://github.com/zmkfirmware/zmk/blob/main/app/module/boards/zhiayang/mikoto/arduino_pro_micro_pins_v6.dtsi) maps. Earlier or unlisted revisions need their own pin-map check. Revision 7.1 has a known hardware problem in the designer's notes.
- [Nordic's limits](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/abs_max_ratings.html) constrain GPIO to VDD + 0.3 V at a 3.3 V supply. A pin is **not 5 V tolerant** just because the board accepts USB 5 V. Do not connect VBUS, RAW, EXT_5V, B+, VDDH or VCC between USB-powered boards.
- [CircuitPython supports this SuperMini](https://circuitpython.org/board/supermini_nrf52840/) with a downloadable UF2. Stable 10.3.1 was available when checked. CircuitPython 8.2+ requires bootloader >=0.6.1. Check the SuperMini's `INFO_UF2.TXT` before installing; an old bootloader requires a board-specific update, not a randomly chosen Feather updater.
- CircuitPython's [SuperMini pin definitions](https://github.com/adafruit/circuitpython/blob/main/ports/nordic/boards/supermini_nrf52840/pins.c) expose raw `P0_06`, `P0_08`, `P0_17`, `P0_20`, `P0_22`, avoiding ambiguous Arduino pin numbering. Its [USB CDC API](https://docs.circuitpython.org/en/latest/shared-bindings/usb_cdc/index.html) supports a separate data port and DTR-based disconnect detection.

## Recommended electrical arrangement

Use five **onsemi 2N3904 NPN transistors** (one reset, four direct keys), each with a **4.7 kΩ base resistor**, **100 kΩ base-to-emitter resistor**, and **1 kΩ collector series resistor**. All emitters connect to the shared ground. See the [part datasheet](https://www.onsemi.com/pdf/datasheet/2n3904-d.pdf) for the actual lead numbering. Do not substitute a different transistor by assuming its leads have the same order.

The transistor is an electronically controlled connection to ground: SuperMini output high closes it; low opens it. The base resistor limits SuperMini current (~0.55 mA); the pull-down keeps it off while firmware starts; the collector resistor limits an accidental 3.3 V output conflict to about 3 mA. These values are engineering choices for short, slow, 3.3 V breadboard tests, not a manufacturer's reference fixture. With the Mikoto's internal pull-up enabled, the 1 kΩ series resistance still permits a valid low input. No external pull-up is needed for these keys or for the reset input.

This avoids a direct driven-high path from one board into the other. It is not galvanic isolation and does not protect against arbitrary miswiring. Grounds are joined; supply rails are not. Connect with USB unplugged, leave batteries disconnected, and inspect solder bridges before powering. A controller that gets hot or causes USB overcurrent needs power removed and physical inspection first.

**No keyboard diodes are needed** for four independent input-to-ground keys. This does not emulate a scanned row/column matrix: that needs switches between rows and columns (for example suitable analog switches or PhotoMOS relays), and potentially the matrix's normal diodes. Pulling arbitrary matrix pins to ground is not an interchangeable solution.

## Test boundaries

The supplied test keyboard uses four direct inputs and produces USB HID F13–F16 press/release events. Passing demonstrates the tested header connections, GPIO inputs/pull-ups, execution and USB HID path under these conditions. It does not prove all header pins, drive strength, radio/antenna, charging, battery life, or a full switch matrix. Repeat with revised firmware/pin assignments to investigate other pins; exclude reset, power, charger and onboard peripheral pins.

If reset pulses do not produce the boot drive, check wiring, USB data cables, the voltage rail and reset pin. A missing/corrupted bootloader can require a separate SWD debugger (SWDIO, SWCLK, GND and reference voltage) and a verified Mikoto bootloader. UF2 cannot revive a bootloader that no longer runs.

A one-time **SuperMini** setup still needs its own double reset or equivalent access. After setup, Mikoto reset and UF2 entry are automated. Physical wiring and initial checks cannot be automated away.
