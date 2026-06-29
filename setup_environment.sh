#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_EXE="${PYTHON_EXE:-python3}"

if ! command -v "$PYTHON_EXE" >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3.11 or newer and try again."
  exit 1
fi

"$PYTHON_EXE" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")
try:
    import tkinter
except Exception:
    raise SystemExit("Tkinter is not available. On Debian/Ubuntu, install it with: sudo apt install python3-tk")
PY

"$PYTHON_EXE" -m venv .venv
"$SCRIPT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$SCRIPT_DIR/.venv/bin/python" -m pip install -r requirements.txt

echo
echo "Environment setup complete."
echo "Run ./AIRT.sh to start the application."