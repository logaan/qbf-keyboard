"""Direct GPIO fixture. Copy all three .py files with signal wires disconnected."""
import board
import digitalio
import json
import microcontroller
import time
import usb_cdc
from watchdog import WatchDogMode
from fixture import Fixture, LineBuffer

outputs = []
controller = None
try:
    for pin in (board.P0_06, board.P0_08, board.P0_17, board.P0_20, board.P0_22):
        output = digitalio.DigitalInOut(pin)
        outputs.append(output)
        # Start released. OPEN_DRAIN turns True into high impedance, not 3.3 V.
        output.switch_to_output(value=True, drive_mode=digitalio.DriveMode.OPEN_DRAIN)
    controller = Fixture(outputs, time.monotonic)
    stream = usb_cdc.data
    if stream is None:
        raise RuntimeError("Copy boot.py and reset to enable the data serial port")
    stream.timeout = 0
    stream.write_timeout = 0.05
    framing = LineBuffer()
    microcontroller.watchdog.timeout = 2
    microcontroller.watchdog.mode = WatchDogMode.RESET
    connected = False
    while True:
        microcontroller.watchdog.feed()
        controller.tick()
        if not stream.connected:
            controller.release()
            framing.reset()
            connected = False
            stream.reset_input_buffer()
        else:
            if not connected:
                controller.release()
                framing.reset()
                connected = True
            if stream.in_waiting:
                for line in framing.feed(stream.read(min(stream.in_waiting, 64))):
                    try:
                        if line is None:
                            raise ValueError("line exceeds 128 bytes")
                        response = controller.command(json.loads(line.decode("utf-8")))
                    except (ValueError, UnicodeError) as error:
                        controller.release()
                        response = {"ok": False, "error": str(error)}
                    packet = (json.dumps(response) + "\n").encode("utf-8")
                    if stream.write(packet) != len(packet):
                        controller.release()
        time.sleep(0.001)
finally:
    try:
        if controller is not None:
            controller.release()
    finally:
        # Also covers failure partway through configuring the GPIOs.
        for output in outputs:
            output.deinit()
