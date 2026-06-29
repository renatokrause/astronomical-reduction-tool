#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$SCRIPT_DIR/AIRT.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Astronomical Image Reduction Tool
Comment=Calibrate, align, stack and generate RGB images from FITS files
Exec=$SCRIPT_DIR/AIRT.sh
Icon=$SCRIPT_DIR/assets/airt-icon.png
Terminal=false
Categories=Science;Astronomy;Education;
EOF

chmod +x "$DESKTOP_FILE"
echo "Desktop entry created: $DESKTOP_FILE"
echo "If your desktop environment requires it, right-click the file and allow launching."