#!/bin/sh
set -eu
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
exec python3 "$root/scripts/setup.py" "$@"
