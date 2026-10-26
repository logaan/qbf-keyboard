#!/bin/sh
set -eu
root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
"$root/scripts/setup.sh" --dependencies-only
exec "$root/.tools/venv/bin/python" "$root/scripts/export_boards.py" "$@"
