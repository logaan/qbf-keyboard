# Automated Mikoto debugging

This fixture uses the **SuperMini nRF52840** as an electronic button-presser. Your laptop can reset the Mikoto, enter its UF2 bootloader, install a test keyboard, and check four GPIO inputs through real USB HID press/release events.

Start with the [HTML wiring guide](wiring/index.html). It contains an embedded SVG circuit overview, component list and breadboard hole coordinates. The [research notes](RESEARCH.md) link the primary sources and explain the limits of the test.

**Reset is pulled to ground, never powered.** Each controller has its own USB cable; only ground is joined between their power systems. The transistor/resistor circuits in the wiring guide are the recommended arrangement. This tests independent input-to-ground keys, not a row/column switch matrix.

## 1. Set up the SuperMini once

Do this with the inter-board wiring disconnected, so its current firmware cannot drive the Mikoto accidentally.

1. Connect the SuperMini to USB with a data-capable cable. To enter its bootloader, briefly bridge its **RST to GND twice within 500 ms**, or double-press its reset button if it has one. Keep it powered between the two resets. Never bridge a supply pin to RST.
2. Open the boot drive's `INFO_UF2.TXT`. Check that this is the SuperMini, and that its bootloader is **0.6.1 or newer**. CircuitPython 10.3.1 needs that minimum version. If it is older, follow the board-specific instructions on the [official SuperMini CircuitPython page](https://circuitpython.org/board/supermini_nrf52840/); do not install a Feather bootloader on it. This package does not change either board's bootloader.
3. Copy [supermini-circuitpython-10.3.1.uf2](dist/supermini-circuitpython-10.3.1.uf2) onto **the SuperMini boot drive**. This official stable runtime is specifically for `supermini_nrf52840`, not another board named SuperMini. A new drive called `CIRCUITPY` should appear.
4. Copy **all three files** from [firmware/supermini](firmware/supermini/) to the root of that SuperMini `CIRCUITPY` drive: `boot.py`, `code.py`, `fixture.py`. No additional CircuitPython libraries are needed.
5. Unplug and reconnect the SuperMini so `boot.py` can configure USB. It should now expose a console serial port and a separate **data serial port**. It deliberately exposes no HID keyboard interface.

The UF2 installs CircuitPython; the three files provide the fixture logic. They are both needed. For convenience, [supermini-install.zip](dist/supermini-install.zip) contains the runtime and those files. Keep the originals and the current Mikoto firmware if you want to restore them later.

The SuperMini needs that one-time physical setup. Once it is running this code, entering **Mikoto** UF2 mode requires no manual key press or reset gesture.

## 2. Prepare the laptop

The supplied observer targets macOS. It listens only to the USB device with product name **Mikoto Test**, so ordinary typing on your other keyboards is not mistaken for target input.

From this repository:

```sh
cd diagnostics/mikoto
python3 -m venv .venv
.venv/bin/pip install -r host/requirements.txt
swiftc host/hid_watch.swift -o host/hid-watch
.venv/bin/python host/fixture_cli.py ports
```

Choose the SuperMini **data** port from the output (usually `/dev/cu.usbmodem...`). With two CDC interfaces, the data port is often the second one; confirm with `status`, rather than assuming based on its name:

```sh
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT status
```

A correct reply includes `protocol: mikoto-fixture-v1`. A timeout usually means the console port was selected, `boot.py` has not been applied, or a serial monitor is already using the port. Close serial monitors while running these commands. Baud rate is a nominal USB CDC setting.

To read keyboard input, macOS may require **System Settings → Privacy & Security → Input Monitoring** permission for the terminal/application running the observer. Grant it yourself, then quit and reopen that application. A permission error is a laptop setup issue, not evidence of a damaged Mikoto. The checker does not bypass this setting or change permissions automatically.

## 3. Check reset and UF2 first

Build only **Q0**, the reset transistor circuit, plus the shared ground. Connect both USB cables after inspecting the wiring. Leave batteries and power-rail connections out.

```sh
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT bootloader
```

The SuperMini sinks Mikoto RESET for 50 ms, releases it for 150 ms, then sinks it for another 50 ms. The laptop waits for a drive whose `INFO_UF2.TXT` has Board-ID `nRF52840-mikoto-rev520`. The usual drive name is `MIKOTO-BOOT`. The Board-ID names a bootloader build and may remain `rev520` on a newer physical PCB.

If no drive appears, inspect USB data cables, GND, the transistor's lead order, reset wiring and the target's power. Do not interpret this as a GPIO test result. See the research notes for the SWD recovery boundary.

## 4. Install the matching Mikoto test keyboard

Check the PCB revision printed on the **Mikoto**. The package provides:

| Physical Mikoto revision | Test image |
| --- | --- |
| 5.20 | `dist/mikoto-test-5.20.0.uf2` |
| 6.1 | `dist/mikoto-test-6.1.0.uf2` |
| 6.3 | `dist/mikoto-test-6.3.0.uf2` |
| 7.2 | `dist/mikoto-test-7.2.0.uf2` |

Do not infer the PCB revision from `INFO_UF2.TXT`. For earlier/unlisted revisions, check compatibility before selecting an image. The designer marks 7.1 as broken; it is not a supported fixture target.

For example, for a **5.20** PCB:

```sh
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT flash dist/mikoto-test-5.20.0.uf2
```

This replaces the Mikoto's current keyboard application, leaving its reserved bootloader/SoftDevice/storage partitions outside the write range. The test image disables Bluetooth, battery reporting and sleep; it creates a USB keyboard named `Mikoto Test`. It uses the internal pull-ups on:

| Fixture key | Mikoto printed GPIO | ZMK connector name | USB key |
| --- | --- | --- | --- |
| 1 | P0.08 | D1 | F13 |
| 2 | P0.17 | D2 | F14 |
| 3 | P0.20 | D3 | F15 |
| 4 | P0.22 | D4 | F16 |

Disconnect both USB cables before adding **Q1–Q4**, then check the wiring and reconnect. The laptop tool accepts only nRF52840 application UF2 blocks inside the Mikoto ZMK application partition. It checks the target drive's exact Board-ID rather than copying to any newly mounted drive. For multiple Mikotos, add `--drive /Volumes/MIKOTO-BOOT` to select an explicit target. If a verified Mikoto uses another Mikoto Board-ID, use `--board-id THE_EXACT_ID` on `flash`/`run`; do not bypass a mismatching SuperMini identifier.

## 5. Run the end-to-end test

```sh
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT test --chords
```

The checker repeats each individual key three times, then tests all multi-key combinations. Each test requires the expected F13–F16 **press and release** edges, and rejects unexpected key events. It writes detailed results to `reports/latest.json` and exits with status 0 for a pass, 1 for a failed HID test, or 2 for a setup/communication error. F13–F16 can still trigger custom shortcuts: close applications that bind them while testing.

To automatically enter UF2, copy a fresh image and then test it in one command:

```sh
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT run dist/mikoto-test-5.20.0.uf2 --chords
```

Use the image for your actual revision. No physical Mikoto key presses are involved. A successful file copy alone is not a pass; the HID test establishes that the installed application responds.

Other useful commands:

```sh
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT reset
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT tap 1
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT tap 1 3 --ms 500
.venv/bin/python host/fixture_cli.py --port /dev/cu.usbmodemYOUR_DATA_PORT release
```

A plain-text serial client can also send newline-terminated JSON such as `{"cmd":"bootloader"}` or `{"cmd":"chord","keys":[1,3],"ms":200}`. Supported commands are `hello`, `status`, `release`, `reset`, `bootloader`, `tap`, `hold`, `chord`. Key duration is bounded to 20–5000 ms. Responses confirm acceptance and current state; poll `status` until `busy` is false to confirm completion. `release` cancels immediately. Disconnecting the data serial connection releases outputs. A two-second hardware watchdog resets the SuperMini if its loop stalls.

## Validation and rebuilding

Software tests cover pulse sequencing, all key masks, cancellation, bounded serial framing, event verification and refusing invalid/protected-area UF2 files. The four Mikoto images were compiled against the pinned ZMK source listed in [BUILD.json](dist/BUILD.json). The macOS observer was compiled locally. The wiring SVG was visually checked.

**Physical validation is still required.** Neither your controllers nor a wired fixture have been tested here. A four-pin pass does not certify all GPIOs, output drivers, Bluetooth, charging or an entire matrix. A failure can be in the fixture, firmware choice, laptop permissions or the target. The guide includes stages to distinguish these.

```sh
python3 -m unittest discover -s tests -v
sh firmware/build-mikoto.sh
```

The rebuild command uses the official ZMK compiler container, downloads pinned dependencies, and writes all four UF2 files to `dist/`. It needs Docker and network access; its temporary container is removed on completion. The SuperMini runtime comes from the official CircuitPython download rather than a local C build. Its fixture code is readable/editable directly on `CIRCUITPY`.

[SHA256SUMS](dist/SHA256SUMS) records the delivered files. Upstream source and license notices are in [dist/LICENSES](dist/LICENSES/).
