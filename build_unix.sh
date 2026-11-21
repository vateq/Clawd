#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt pyinstaller
python3 -m PyInstaller --noconfirm --clean --onefile --windowed --name Clawd clawd.py
echo "Build finished: dist/Clawd"
