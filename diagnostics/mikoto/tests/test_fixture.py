import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


firmware = load("fixture", ROOT / "firmware/supermini/fixture.py")
host = load("fixture_cli", ROOT / "host/fixture_cli.py")


class Output:
    value = False


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.outputs = [Output() for _ in range(5)]
        self.fixture = firmware.Fixture(self.outputs, lambda: self.now)

    def advance(self, duration):
        self.now += duration
        self.fixture.tick()

    def test_bootloader_has_two_distinct_low_pulses(self):
        self.fixture.command({"cmd": "bootloader"})
        self.assertTrue(self.outputs[0].value)
        self.advance(0.051)
        self.assertFalse(self.outputs[0].value)
        self.advance(0.151)
        self.assertTrue(self.outputs[0].value)
        self.advance(0.051)
        self.assertFalse(self.outputs[0].value)
        self.advance(0.101)
        self.assertFalse(self.fixture.status()["busy"])

    def test_late_tick_does_not_collapse_reset_pulses(self):
        self.fixture.command({"cmd": "bootloader"})
        self.advance(1)
        self.assertFalse(self.outputs[0].value)
        self.advance(0.149)
        self.assertFalse(self.outputs[0].value)
        self.advance(0.002)
        self.assertTrue(self.outputs[0].value)

    def test_every_chord_releases_and_never_asserts_reset(self):
        for mask in range(1, 16):
            keys = [key for key in range(1, 5) if mask & (1 << (key - 1))]
            response = self.fixture.command({"cmd": "chord", "keys": keys, "ms": 100})
            self.assertEqual(response["keys"], keys)
            self.assertFalse(self.outputs[0].value)
            self.advance(0.101)
            self.assertFalse(any(output.value for output in self.outputs))
            self.advance(0.101)

    def test_bad_commands_release_an_active_key(self):
        requests = [None, {}, {"cmd": "bad"}, {"cmd": "tap", "keys": [True]},
                    {"cmd": "hold", "keys": [1], "ms": 5001},
                    {"cmd": "tap", "keys": [1, 1]}]
        for request in requests:
            self.fixture.command({"cmd": "hold", "keys": [1], "ms": 5000})
            self.assertTrue(self.outputs[1].value)
            # Invalid commands while busy either reject without replacing or release.
            response = self.fixture.command(request)
            self.assertFalse(response["ok"])
            self.fixture.release()
            response = self.fixture.command(request)
            self.assertFalse(response["ok"])
            self.assertFalse(any(output.value for output in self.outputs))

    def test_release_cancels_reset_or_key_sequence(self):
        self.fixture.command({"cmd": "bootloader"})
        self.fixture.command({"cmd": "release"})
        self.advance(10)
        self.assertFalse(any(output.value for output in self.outputs))

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


if __name__ == "__main__":
    unittest.main()
