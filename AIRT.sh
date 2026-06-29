#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_EXE="$SCRIPT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_EXE" ]]; then
  echo "Python virtual environment was not found."
  echo "Run ./setup_environment.sh first."
  exit 1
fi

"$PYTHON_EXE" app.py