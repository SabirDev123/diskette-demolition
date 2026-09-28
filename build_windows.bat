@echo off
setlocal

cd /d "%~dp0"

python -m pip install -r requirements.txt

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "Diskette Demolition" ^
    src\main.py

echo.
echo ========================================
echo  Windows build complete!
echo ========================================
echo.
echo EXE:
echo dist\Diskette Demolition\Diskette Demolition.exe

pause
