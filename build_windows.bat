@echo off
setlocal
cd /d "%~dp0"
echo [Clawd] Installing build dependencies...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto fail
echo [Clawd] Building portable Windows executable...
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Clawd clawd.py
if errorlevel 1 goto fail
echo.
echo Build finished: dist\Clawd.exe
pause
exit /b 0
:fail
echo Build failed. Check the error above.
pause
exit /b 1
