@echo off
REM Choi Sango II ban dich tieng Viet (SAN2-VN.EXE)
cd /d "%~dp0"
set "GAME=D:\Game\SAN\SANGO2"
if not exist "%GAME%\SAN2-VN.EXE" set "GAME=D:\Game\SAN\sango2"
if not exist "%GAME%\SAN2-VN.EXE" (
    echo Chua co ban dich!
    echo Chay: D:\Game\SAN\repo\scripts\build_vn_release.bat
    pause
    exit /b 1
)
set SDL_AUDIODRIVER=winmm
"C:\DOSBox-X\dosbox-x.exe" -conf "%~dp0play_vn.conf"
