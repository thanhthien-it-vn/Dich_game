@echo off
REM VigameV1.0 — pull/update ve may Windows
REM Chay file nay trong PowerShell hoac double-click

set TOOLKIT=D:\Game\VigameV1.0

if not exist "%TOOLKIT%" (
    echo Tao moi...
    git clone https://github.com/thanhthien-it-vn/Dich_game.git "%TOOLKIT%"
    cd /d "%TOOLKIT%"
) else (
    cd /d "%TOOLKIT%"
    git pull origin main
)

pip install -r requirements.txt
echo.
echo ✓ VigameV1.0 san sang tai %TOOLKIT%
echo   Doc: INSTALL_WINDOWS.md
python dich.py --help
