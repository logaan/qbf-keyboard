#!/bin/sh
set -eu

if [ -n "${KICAD_PYTHON:-}" ]; then
    exec "$KICAD_PYTHON" scripts/route_board.py
fi

KICAD_MAC_PYTHON=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
if [ -x "$KICAD_MAC_PYTHON" ]; then
    exec "$KICAD_MAC_PYTHON" scripts/route_board.py
fi

exec python3 scripts/route_board.py
