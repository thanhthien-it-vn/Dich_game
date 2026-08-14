@echo off
cd /d "%~dp0"
echo ============================================
echo   SANGO II - COPY CRACK
echo ============================================
if not exist "D:\Game\SAN\SANGO2\SAN2.EXE" (
    if not exist "D:\Game\SAN\sango2\SAN2.EXE" (
        echo Chua cai dat! Hay chay "Install Sango2.bat" truoc.
        pause
        exit /b 1
    )
)
if not exist "_crack\crack_out" mkdir "_crack\crack_out"
del /q "_crack\crack_out\*.*" 2>nul
echo Dang trich xuat thu muc CRACK tu dia CD...
set SDL_AUDIODRIVER=winmm
"C:\DOSBox-X\dosbox-x.exe" -conf "%~dp0_crack\extract_crack.conf"
if not exist "_crack\crack_out\SAN2.EXE" (
    echo Loi: Khong trich xuat duoc crack tu dia CD!
    echo Kiem tra CD: D:\Game\VigameV1.0\games\MyRPG\game\Sango2\
    pause
    exit /b 1
)
set "DEST=D:\Game\SAN\SANGO2"
if not exist "%DEST%" set "DEST=D:\Game\SAN\sango2"
echo Dang copy crack vao %DEST%...
copy /Y "_crack\crack_out\*.*" "%DEST%\" >nul
echo.
echo Crack thanh cong!
echo   Chay "Play Sango2 VN.bat" de choi.
echo.
pause
