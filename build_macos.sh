#!/bin/bash
set -e

cd "$(dirname "$0")"

python3 -m pip install -r requirements.txt

rm -rf build dist

python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "Diskette Demolition" \
    src/main.py

echo
echo "========================================"
echo " macOS build complete!"
echo "========================================"
echo
echo "App:"
echo "dist/Diskette Demolition.app"
