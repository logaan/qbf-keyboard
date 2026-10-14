"""Direct open-drain fixture: False sinks a signal; True releases it."""

PROTOCOL = "mikoto-fixture-v2"
WIRING = "direct-open-drain"


class Fixture:
    def __init__(self, outputs, clock):
        # outputs: [reset, key1, key2, key3, key4], configured OPEN_DRAIN.
        self.outputs = outputs
        self.clock = clock
        self.steps = []
        self.deadline = 0
        self.release()

    def release(self):
        self.steps = []
        self.reset_asserted = False
        self.pressed_keys = []
        for output in self.outputs:
            output.value = True  # high impedance; never actively drive high

    def status(self):
        # Report commanded state. A released pin can still read low if the
        # target holds it low, so pin.value is not an acknowledgement of a press.
        return {"ok": True, "protocol": PROTOCOL, "wiring": WIRING,
                "busy": bool(self.steps), "reset": self.reset_asserted,
                "keys": list(self.pressed_keys)}

    def _apply(self, step):
        reset, keys, milliseconds = step
        self.reset_asserted = reset
        self.pressed_keys = list(keys)
        self.outputs[0].value = not reset
        for i in range(1, 5):
            self.outputs[i].value = i not in keys
        self.deadline = self.clock() + milliseconds / 1000

    def tick(self):
        if self.steps and self.clock() >= self.deadline:
            self.steps.pop(0)
            if self.steps:
                # Each pulse gets its full duration even after a delayed tick.
                self._apply(self.steps[0])
            else:
                self.release()

    def command(self, request):
        try:
            return self._command(request)
        except (ValueError, TypeError, KeyError) as error:
            self.release()
            return {"ok": False, "error": str(error)}

    def _command(self, request):
        if not isinstance(request, dict):
            raise ValueError("request must be an object")
        command = request.get("cmd")
        if command in ("hello", "status"):
            return self.status()
        if command == "release":
            self.release()
            return self.status()
        if command not in ("reset", "bootloader", "tap", "hold", "chord"):
            raise ValueError("unknown command")
        if self.steps:
            return {"ok": False, "error": "busy; use release to cancel"}
        if command == "reset":
            self.steps = [(True, [], 50), (False, [], 100)]
        elif command == "bootloader":
            self.steps = [(True, [], 50), (False, [], 150),
                          (True, [], 50), (False, [], 100)]
        else:
            keys = request.get("keys")
            if (not isinstance(keys, list) or not keys or len(keys) > 4
                    or any(type(key) is not int or key < 1 or key > 4 for key in keys)
                    or len(set(keys)) != len(keys)):
                raise ValueError("keys must be distinct integers from 1 to 4")
            duration = request.get("ms", 150)
            if type(duration) is not int or not 20 <= duration <= 5000:
                raise ValueError("ms must be an integer from 20 to 5000")
            if command == "tap" and len(keys) != 1:
                raise ValueError("tap requires exactly one key")
            self.steps = [(False, keys, duration), (False, [], 100)]
        self._apply(self.steps[0])
        return self.status()


class LineBuffer:
    """Bounded line framing; discard a whole oversized line, never its tail."""
    def __init__(self, limit=128):
        self.limit = limit
        self.buffer = bytearray()
        self.discarding = False

    def reset(self):
        self.buffer = bytearray()
        self.discarding = False

    def feed(self, data):
        lines = []
        for byte in data:
            if byte == 10:
                lines.append(None if self.discarding else bytes(self.buffer))
                self.reset()
            elif not self.discarding:
                if len(self.buffer) >= self.limit:
                    self.buffer = bytearray()
                    self.discarding = True
                else:
                    self.buffer.append(byte)
        return lines
