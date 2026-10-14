#!/usr/bin/env python3
"""macOS fixture CLI: serial control, validated UF2 copy, device-specific HID tests."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import queue
import struct
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "mikoto-fixture-v2"
WIRING = "direct-open-drain"
MIKOTO_BOARD_ID = "nRF52840-mikoto-rev520"


class Client:
    def __init__(self, port):
        import serial
        self.serial = serial.Serial(port, 115200, timeout=0.1, write_timeout=2)
        self.serial.dtr = True
        time.sleep(0.15)
        self.serial.reset_input_buffer()
        try:
            hello = self.request("hello")
            if hello.get("protocol") == "mikoto-fixture-v1":
                raise RuntimeError("Old transistor firmware detected. Disconnect all signal wires, "
                                   "install the updated SuperMini Python files, then reset it")
            if hello.get("protocol") != PROTOCOL:
                raise RuntimeError("This is not the fixture data port; try the other SuperMini port")
            if hello.get("wiring") != WIRING:
                raise RuntimeError("Fixture wiring mode must be direct-open-drain")
        except BaseException:
            self.serial.close()
            raise

    def request(self, command, **arguments):
        packet = (json.dumps({"cmd": command, **arguments}) + "\n").encode()
        self.serial.write(packet)
        deadline = time.monotonic() + 3
        buffer = bytearray()
        while time.monotonic() < deadline:
            buffer.extend(self.serial.read(1))
            if len(buffer) > 1024:
                raise RuntimeError("Unexpected serial response")
            if buffer.endswith(b"\n"):
                response = json.loads(buffer)
                if not response.get("ok"):
                    raise RuntimeError(response.get("error", "fixture rejected command"))
                return response
        raise TimeoutError("Fixture did not reply; use its data port and close other serial clients")

    def wait_idle(self, timeout=7):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not self.request("status")["busy"]:
                return
            time.sleep(0.02)
        raise TimeoutError("Fixture action did not complete")

    def close(self):
        try:
            self.request("release")
        except (OSError, RuntimeError, TimeoutError, ValueError):
            # Dropping DTR also releases the fixture; preserve the original error.
            pass
        finally:
            self.serial.close()


def validate_uf2(path):
    data = Path(path).read_bytes()
    if not data or len(data) % 512:
        raise ValueError("UF2 must contain complete 512-byte blocks")
    count = len(data) // 512
    seen = set()
    for offset in range(0, len(data), 512):
        block = data[offset:offset + 512]
        m0, m1, flags, address, size, number, total, family = struct.unpack_from("<8I", block)
        end_magic, = struct.unpack_from("<I", block, 508)
        if (m0, m1, end_magic) != (0x0A324655, 0x9E5D5157, 0x0AB16F30):
            raise ValueError("Invalid UF2 magic")
        if flags != 0x2000 or family != 0xADA52840:
            raise ValueError("Expected an nRF52840 application UF2 with family ID")
        if (not 0 < size <= 476 or size % 4 or address % 4
                or address < 0x26000 or address + size > 0xEC000):
            raise ValueError("UF2 writes outside the Mikoto ZMK application partition")
        if total != count or number >= count or number in seen:
            raise ValueError("Inconsistent UF2 block numbering")
        seen.add(number)
    return data


def board_id(drive):
    try:
        text = (drive / "INFO_UF2.TXT").read_text()
    except OSError:
        return None
    for line in text.splitlines():
        if line.startswith("Board-ID:"):
            return line.split(":", 1)[1].strip()
    return None


def wait_drive(expected_id, explicit=None, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        candidates = [Path(explicit)] if explicit else list(Path("/Volumes").iterdir())
        found = [drive for drive in candidates if board_id(drive) == expected_id]
        if len(found) > 1:
            raise RuntimeError("Multiple matching boot drives; pass --drive for the Mikoto")
        if found:
            return found[0]
        time.sleep(0.1)
    raise TimeoutError("No matching Mikoto boot drive; check reset wiring, USB and INFO_UF2.TXT")


def flash(client, path, expected_id=MIKOTO_BOARD_ID, drive=None):
    data = validate_uf2(path)  # verify before pulsing the target
    if "mikoto" not in expected_id.lower():
        raise ValueError("Board-ID must identify a Mikoto, not the fixture")
    client.request("bootloader")
    client.wait_idle()
    target = wait_drive(expected_id, drive)
    print("Flashing", target, "with", Path(path).name, flush=True)
    with (target / "MIKOTEST.UF2").open("wb") as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())
    return {"drive": str(target), "sha256": hashlib.sha256(data).hexdigest()}


class Observer:
    def __init__(self):
        executable = ROOT / "host/hid-watch"
        if not executable.exists():
            raise RuntimeError("Build the HID observer using the README command first")
        self.process = subprocess.Popen([str(executable)], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True)
        self.events = queue.Queue()
        threading.Thread(target=self._read, daemon=True).start()
        try:
            ready = self.events.get(timeout=5)
            if ready.get("type") != "ready":
                raise RuntimeError(str(ready))
        except BaseException:
            self.close()
            raise

    def _read(self):
        for line in self.process.stdout:
            try:
                self.events.put(json.loads(line))
            except ValueError:
                self.events.put({"type": "error", "error": line.strip()})
        self.events.put({"type": "error", "error": "HID observer exited"})

    def drain(self):
        result = []
        while True:
            try:
                result.append(self.events.get_nowait())
            except queue.Empty:
                return result

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process.stdout.close()
        self.process.stderr.close()


def assess_events(events, keys):
    expected = {103 + key for key in keys}  # HID usages F13=104 through F16=107
    states = {usage: [] for usage in expected}
    errors = []
    for event in events:
        if event.get("type") != "key":
            errors.append(str(event))
        elif event.get("usage") not in expected:
            errors.append("Unexpected HID usage " + str(event.get("usage")))
        else:
            states[event["usage"]].append(event["pressed"])
    for usage, transitions in states.items():
        if transitions != [True, False]:
            errors.append("Usage %s expected press/release, received %s" % (usage, transitions))
    return errors


def run_tests(client, repeats=3, chords=False):
    client.request("release")
    observer = Observer()
    results = []
    try:
        time.sleep(0.2)
        initial = observer.drain()
        if initial:
            raise RuntimeError("Target has unexpected idle input: " + str(initial))
        patterns = [[key] for _ in range(repeats) for key in range(1, 5)]
        if chords:
            patterns += [list(keys) for n in range(2, 5)
                         for keys in itertools.combinations(range(1, 5), n)]
        for keys in patterns:
            stray = observer.drain()
            client.request("tap" if len(keys) == 1 else "chord", keys=keys, ms=200)
            client.wait_idle()
            time.sleep(0.15)
            events = stray + observer.drain()
            errors = assess_events(events, keys)
            results.append({"keys": keys, "pass": not errors, "events": events, "errors": errors})
            print(("PASS" if not errors else "FAIL"), keys, "; ".join(errors), flush=True)
        return {"pass": all(result["pass"] for result in results), "tests": results}
    finally:
        try:
            client.request("release")
        finally:
            observer.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="SuperMini's data CDC port, e.g. /dev/cu.usbmodem...")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("ports")
    sub.add_parser("status")
    sub.add_parser("release")
    sub.add_parser("reset")
    sub.add_parser("bootloader")
    tap = sub.add_parser("tap")
    tap.add_argument("keys", type=int, nargs="+")
    tap.add_argument("--ms", type=int, default=200)
    for name in ("flash", "test", "run"):
        command = sub.add_parser(name)
        if name != "test":
            command.add_argument("firmware", type=Path)
            command.add_argument("--drive", help="Optional explicit Mikoto boot volume")
            command.add_argument("--board-id", default=MIKOTO_BOARD_ID)
        if name != "flash":
            command.add_argument("--repeats", type=int, default=3)
            command.add_argument("--chords", action="store_true")
            command.add_argument("--report", type=Path, default=ROOT / "reports/latest.json")
    args = parser.parse_args()
    if args.action == "ports":
        from serial.tools import list_ports
        for port in list_ports.comports():
            print(port.device, port.description, port.serial_number, port.interface)
        return 0
    if not args.port:
        parser.error("--port is required for this action")
    if hasattr(args, "repeats") and not 1 <= args.repeats <= 100:
        parser.error("--repeats must be 1–100")
    client = Client(args.port)
    try:
        result = {}
        if args.action in ("flash", "run"):
            result["flash"] = flash(client, args.firmware, args.board_id, args.drive)
        if args.action == "run":
            time.sleep(3)  # allow target USB enumeration after UF2 copy
        if args.action in ("test", "run"):
            result["hid"] = run_tests(client, args.repeats, args.chords)
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, indent=2) + "\n")
            print("Report:", args.report)
            return 0 if result["hid"]["pass"] else 1
        elif args.action == "tap":
            print(client.request("tap" if len(args.keys) == 1 else "chord",
                                 keys=args.keys, ms=args.ms))
            client.wait_idle()
        elif args.action == "bootloader":
            print(client.request("bootloader"))
            client.wait_idle()
            print("Mikoto boot drive:", wait_drive(MIKOTO_BOARD_ID))
        elif args.action in ("reset", "status", "release"):
            print(client.request(args.action))
            client.wait_idle()
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, TimeoutError, ValueError) as error:
        print("Error:", error, file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)
