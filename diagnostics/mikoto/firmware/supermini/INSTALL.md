# SuperMini direct GPIO fixture — installation

This package is for the **SuperMini nRF52840**. The application controls a Mikoto through five open-drain signal connections, each with a **1 kΩ series resistor**, and shared GND. It pulls a signal low to assert reset/a key and leaves the wire undriven to release it. Both controllers use their own USB cables; their supply rails stay separate.

## Updating an existing fixture

1. **Disconnect all five inter-board signal connections first.** The previous transistor firmware has different polarity and must not be used with direct wiring.
2. If CircuitPython 10.3.1 is already installed, keep it. Copy the **contents** of this archive's `CIRCUITPY` folder (`boot.py`, `code.py`, `fixture.py`) to the root of the SuperMini's actual `CIRCUITPY` drive, replacing all three old files. Do not copy the folder itself into the drive.
3. Reset the SuperMini with its signal wires still disconnected. Use the updated laptop tool from the QBF repository; a `status` reply must show `protocol: mikoto-fixture-v2` and `wiring: direct-open-drain`.
4. Rebuild the breadboard following `diagnostics/mikoto/wiring/index.html` in the repository. Its current README describes the connection and test sequence. The existing Mikoto 7.2 test UF2 remains valid.

## Fresh SuperMini setup

1. Keep the SuperMini signal wires disconnected. Connect it to the laptop using a USB data cable and enter its own bootloader by briefly bridging **RST to GND twice within 500 ms** (or double-pressing its reset button, if fitted).
2. Check the SuperMini boot drive's `INFO_UF2.TXT`. CircuitPython 10.3.1 requires bootloader **0.6.1 or newer**. For an older bootloader, follow the board-specific instructions at https://circuitpython.org/board/supermini_nrf52840/; do not use an arbitrary Feather updater.
3. Copy `supermini-circuitpython-10.3.1.uf2` from this archive onto the **SuperMini** boot drive. The `CIRCUITPY` drive should appear. This UF2 installs the runtime; it is not a bootloader update and does not include the fixture application files.
4. Copy the three `.py` files from this archive's `CIRCUITPY` folder into the root of that actual drive. No extra CircuitPython libraries are needed.
5. Unplug/reconnect the SuperMini, still with its signal wires disconnected. It presents a console CDC port and a separate data CDC port. The laptop checker uses the data port.

## Operating the direct wiring

Connect shared ground first. Plug both controllers into USB with signal wires unattached, confirm the new firmware's `status`, then attach signals through their resistors. **Disconnect all five signal connections before unplugging either controller's USB cable.** A 1 kΩ resistor limits current but does not provide power-off isolation. Keep batteries disconnected and never supply 5 V to reset or GPIO.

The host checker and Mikoto test firmware are in the QBF repository, outside this SuperMini-only archive. See `diagnostics/mikoto/README.md` there for reset, automated flashing and USB HID tests. Software checks pass; the physical fixture still needs testing.
