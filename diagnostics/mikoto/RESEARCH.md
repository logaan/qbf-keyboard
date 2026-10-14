# Mikoto automated test fixture — researched 13 October, updated 15 October 2026

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

Use **direct open-drain GPIO connections** with five **1 kΩ series resistors** (one for reset and one per key), plus a direct shared-ground connection. The SuperMini connects each signal to ground to assert it, then releases it to high impedance. The Mikoto's own pull-ups restore the high level. No external transistor or extra pull-up is required for this fixture.

[CircuitPython's open-drain mode](https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/index.html#digitalio.DriveMode) implements low output and high-impedance release. The updated firmware explicitly selects `OPEN_DRAIN` and starts every pin at `value=True` (released); asserting a signal sets `value=False`. Shutdown deinitializes the pins. Protocol `mikoto-fixture-v2` identifies this wiring, and the updated laptop tool rejects the earlier transistor firmware. Status reports commanded states rather than interpreting a target-held-low pad as a commanded key press.

At 3.3 V, a 1 kΩ series resistor bounds an accidental output conflict to roughly 3.3 mA. With the Mikoto's internal pull-up enabled, this series resistance still permits a valid low input. These values are engineering choices for short, slow breadboard tests, not a manufacturer's reference fixture. The resistors reduce conflict current; they do not provide galvanic isolation, make GPIOs 5 V tolerant, protect against arbitrary miswiring, or make connections to an unpowered controller safe.

**Keep both boards powered while the five signal wires are connected.** Connect GND first, power both controllers over their own USB cables with signal wires unattached, then attach the signals. Disconnect all signal wires before removing either board's USB power. An unpowered board's allowable GPIO voltage falls with VDD; the powered board's pull-ups can feed current through the unpowered board's protection circuitry. Open-drain release alone does not remove that path. Supply rails stay separate; batteries remain disconnected.

Do breadboard component changes with USB unplugged and signal wires removed. Inspect solder bridges before powering. A controller that gets hot or causes USB overcurrent needs power removed and physical inspection first.

The previous external-transistor design has been replaced. If it was installed, disconnect all signal wires before updating all three SuperMini Python files and rebuilding the circuit. The supplied CircuitPython runtime and Mikoto test images do not need changing for this migration.

**No keyboard diodes are needed** for four independent input-to-ground keys. This does not emulate a scanned row/column matrix: that needs switches between rows and columns (for example suitable analog switches or PhotoMOS relays), and potentially the matrix's normal diodes. Pulling arbitrary matrix pins to ground is not an interchangeable solution.

## Test boundaries

The supplied test keyboard uses four direct inputs and produces USB HID F13–F16 press/release events. Passing demonstrates the tested header connections, GPIO inputs/pull-ups, execution and USB HID path under these conditions. It does not prove all header pins, drive strength, radio/antenna, charging, battery life, or a full switch matrix. Repeat with revised firmware/pin assignments to investigate other pins; exclude reset, power, charger and onboard peripheral pins.

If reset pulses do not produce the boot drive, check wiring, USB data cables, the voltage rail and reset pin. A missing/corrupted bootloader can require a separate SWD debugger (SWDIO, SWCLK, GND and reference voltage) and a verified Mikoto bootloader. UF2 cannot revive a bootloader that no longer runs.

A one-time **SuperMini** setup still needs its own double reset or equivalent access. After setup, Mikoto reset and UF2 entry are automated. Physical wiring and initial checks cannot be automated away.
