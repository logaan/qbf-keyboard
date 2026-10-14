import importlib.util
import json
from pathlib import Path
import runpy
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


firmware = load("fixture", ROOT / "firmware/supermini/fixture.py")
host = load("fixture_cli", ROOT / "host/fixture_cli.py")


class Output:
    value = True


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.outputs = [Output() for _ in range(5)]
        self.fixture = firmware.Fixture(self.outputs, lambda: self.now)

    def advance(self, duration):
        self.now += duration
        self.fixture.tick()

    def test_startup_releases_all_signals_and_reports_direct_wiring(self):
        self.assertTrue(all(output.value for output in self.outputs))
        status = self.fixture.status()
        self.assertEqual(status["protocol"], "mikoto-fixture-v2")
        self.assertEqual(status["wiring"], "direct-open-drain")
        self.assertFalse(status["reset"])
        self.assertEqual(status["keys"], [])

    def test_status_reports_commanded_state_when_target_holds_a_pin_low(self):
        self.outputs[1].value = False  # model a low pad reading after release
        self.assertEqual(self.fixture.status()["keys"], [])
        self.assertFalse(self.fixture.status()["reset"])

    def test_bootloader_has_two_distinct_low_pulses(self):
        self.fixture.command({"cmd": "bootloader"})
        self.assertFalse(self.outputs[0].value)
        self.advance(0.051)
        self.assertTrue(self.outputs[0].value)
        self.advance(0.151)
        self.assertFalse(self.outputs[0].value)
        self.advance(0.051)
        self.assertTrue(self.outputs[0].value)
        self.advance(0.101)
        self.assertFalse(self.fixture.status()["busy"])

    def test_late_tick_does_not_collapse_reset_pulses(self):
        self.fixture.command({"cmd": "bootloader"})
        self.advance(1)
        self.assertTrue(self.outputs[0].value)
        self.advance(0.149)
        self.assertTrue(self.outputs[0].value)
        self.advance(0.002)
        self.assertFalse(self.outputs[0].value)

    def test_every_chord_releases_and_never_asserts_reset(self):
        for mask in range(1, 16):
            keys = [key for key in range(1, 5) if mask & (1 << (key - 1))]
            response = self.fixture.command({"cmd": "chord", "keys": keys, "ms": 100})
            self.assertEqual(response["keys"], keys)
            self.assertEqual([i for i in range(1, 5) if not self.outputs[i].value], keys)
            self.assertTrue(self.outputs[0].value)
            self.advance(0.101)
            self.assertTrue(all(output.value for output in self.outputs))
            self.advance(0.101)

    def test_bad_commands_release_an_active_key(self):
        requests = [None, {}, {"cmd": "bad"}, {"cmd": "tap", "keys": [True]},
                    {"cmd": "hold", "keys": [1], "ms": 5001},
                    {"cmd": "tap", "keys": [1, 1]}]
        for request in requests:
            self.fixture.command({"cmd": "hold", "keys": [1], "ms": 5000})
            self.assertFalse(self.outputs[1].value)
            # Invalid commands while busy either reject without replacing or release.
            response = self.fixture.command(request)
            self.assertFalse(response["ok"])
            self.fixture.release()
            response = self.fixture.command(request)
            self.assertFalse(response["ok"])
            self.assertTrue(all(output.value for output in self.outputs))

    def test_release_cancels_reset_or_key_sequence(self):
        self.fixture.command({"cmd": "bootloader"})
        self.fixture.command({"cmd": "release"})
        self.advance(10)
        self.assertTrue(all(output.value for output in self.outputs))

    def test_busy_does_not_overwrite_sequence(self):
        self.fixture.command({"cmd": "hold", "keys": [4]})
        self.assertFalse(self.fixture.command({"cmd": "reset"})["ok"])
        self.assertEqual(self.fixture.status()["keys"], [4])

    def test_line_framing_and_oversize_recovery(self):
        framing = firmware.LineBuffer(8)
        self.assertEqual(framing.feed(b"abc"), [])
        self.assertEqual(framing.feed(b"d\nxy\n"), [b"abcd", b"xy"])
        self.assertEqual(framing.feed(b"123456789tail\nok\n"), [None, b"ok"])


class HostTests(unittest.TestCase):
    def test_host_rejects_old_firmware_or_wrong_wiring_before_sending_actions(self):
        for hello in ({"protocol": "mikoto-fixture-v1"},
                      {"protocol": host.PROTOCOL, "wiring": "transistor"}):
            port = Mock()
            with patch.dict(sys.modules, {"serial": SimpleNamespace(Serial=lambda *a, **k: port)}), \
                    patch.object(host.time, "sleep"), \
                    patch.object(host.Client, "request", return_value=hello) as request:
                with self.assertRaises(RuntimeError):
                    host.Client("test-port")
                request.assert_called_once_with("hello")
                port.close.assert_called_once()

    def test_reports_require_both_edges_and_reject_other_inputs(self):
        events = [{"type": "key", "usage": 104, "pressed": True},
                  {"type": "key", "usage": 104, "pressed": False}]
        self.assertEqual(host.assess_events(events, [1]), [])
        self.assertTrue(host.assess_events(events[:1], [1]))
        self.assertTrue(host.assess_events(list(reversed(events)), [1]))
        self.assertTrue(host.assess_events(events + events, [1]))
        self.assertTrue(host.assess_events(events, [2]))

    def test_uf2_refuses_bootloader_or_wrong_family_writes(self):
        def block(address=0x26000, family=0xADA52840):
            result = bytearray(512)
            struct.pack_into("<8I", result, 0, 0x0A324655, 0x9E5D5157, 0x2000,
                             address, 256, 0, 1, family)
            struct.pack_into("<I", result, 508, 0x0AB16F30)
            return result
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.uf2"
            path.write_bytes(block())
            self.assertEqual(host.validate_uf2(path), block())
            for data in (block(0), block(0xF4000), block(family=0xE48BFF56), b"bad"):
                path.write_bytes(data)
                with self.assertRaises(ValueError):
                    host.validate_uf2(path)


class RuntimeTests(unittest.TestCase):
    """Exercise the actual CircuitPython entry point with a GPIO/USB model."""
    def run_runtime(self, command=None, disconnect=False, fail_pin=None):
        class StopLoop(BaseException):
            pass

        now = [0.0]
        pins = []
        log = []
        stream = SimpleNamespace(connected=True)
        packet = bytearray((json.dumps(command) + "\n").encode() if command else b"")

        class GPIO:
            def __init__(self, pin):
                self.pin = pin
                self.drive_mode = None
                self.level = True
                self.configuration = None
                pins.append(self)

            def switch_to_output(self, *, value, drive_mode):
                if self.pin == fail_pin:
                    raise ValueError("pin configuration failed")
                self.configuration = {"value": value, "drive_mode": drive_mode}
                self.drive_mode = drive_mode
                self.value = value

            @property
            def value(self):
                return self.level

            @value.setter
            def value(self, value):
                self.level = value
                state = "low" if not value else (
                    "high-z" if self.drive_mode == "open-drain" else "driven-high")
                log.append((now[0], self.pin, state))

            def deinit(self):
                log.append((now[0], self.pin, "input"))

        class Stream:
            timeout = None
            write_timeout = None
            replies = []

            @property
            def connected(self):
                return stream.connected

            @property
            def in_waiting(self):
                return len(packet)

            def read(self, count):
                result = bytes(packet[:count])
                del packet[:count]
                return result

            def write(self, data):
                self.replies.append(json.loads(data))
                return len(data)

            def reset_input_buffer(self):
                packet.clear()

        class Watchdog:
            feeds = 0

            def feed(self):
                self.feeds += 1
                if disconnect and self.feeds == 20:
                    stream.connected = False
                if self.feeds == 30:
                    raise StopLoop()

        watchdog = Watchdog()

        def sleep(duration):
            now[0] += duration

        names = ("P0_06", "P0_08", "P0_17", "P0_20", "P0_22")
        modules = {
            "board": SimpleNamespace(**{name: name for name in names}),
            "digitalio": SimpleNamespace(DigitalInOut=GPIO,
                                         DriveMode=SimpleNamespace(OPEN_DRAIN="open-drain")),
            "microcontroller": SimpleNamespace(watchdog=watchdog),
            "watchdog": SimpleNamespace(WatchDogMode=SimpleNamespace(RESET="reset")),
            "usb_cdc": SimpleNamespace(data=Stream()),
            "time": SimpleNamespace(monotonic=lambda: now[0], sleep=sleep),
            "fixture": firmware,
        }
        with patch.dict(sys.modules, modules):
            with self.assertRaises(ValueError if fail_pin else StopLoop):
                runpy.run_path(str(ROOT / "firmware/supermini/code.py"))
        self.assertFalse(any(state == "driven-high" for _, _, state in log))
        for pin in pins:
            if pin.pin != fail_pin:
                self.assertEqual(pin.configuration, {"value": True, "drive_mode": "open-drain"})
            self.assertEqual([state for _, name, state in log if name == pin.pin][-1], "input")
        return log

    def test_entrypoint_starts_released_without_ever_driving_high(self):
        log = self.run_runtime()
        self.assertFalse(any(state == "low" for _, _, state in log))

    def test_usb_disconnect_releases_a_held_key_before_its_deadline(self):
        log = self.run_runtime({"cmd": "hold", "keys": [1], "ms": 5000}, disconnect=True)
        states = [(time, state) for time, pin, state in log if pin == "P0_08"]
        low_index = next(i for i, (_, state) in enumerate(states) if state == "low")
        release_time = next(time for time, state in states[low_index + 1:] if state == "high-z")
        self.assertLess(release_time, 0.025)

    def test_exception_releases_all_active_signals(self):
        log = self.run_runtime({"cmd": "chord", "keys": [1, 4], "ms": 5000})
        for pin in ("P0_08", "P0_22"):
            states = [state for _, name, state in log if name == pin]
            self.assertIn("low", states)
            self.assertEqual(states[-2:], ["high-z", "input"])

    def test_partial_gpio_configuration_is_cleaned_up(self):
        self.run_runtime(fail_pin="P0_17")


if __name__ == "__main__":
    unittest.main()
