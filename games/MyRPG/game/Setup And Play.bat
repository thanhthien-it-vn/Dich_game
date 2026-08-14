@echo off
REM Setup lan dau + choi Sango II (co dau + nhac CD)
setlocal
cd /d "%~dp0"
set "ROOT=%~dp0..\.."
set "GAME=%~dp0"

title Sango II — Setup + Play

echo.
echo ============================================
echo   SANGO II — Setup lan dau + Play
echo ============================================
echo.

REM --- Kiem tra CD image ---
if not exist "%GAME%CD-ROM\Sango2.img" (
  echo [LOI] Thieu CD-ROM\Sango2.img
  echo       Chay: git lfs pull
  pause
  exit /b 1
)

REM --- Hoan nguyen dia neu chua co ---
if not exist "%GAME%CD-ROM\restored\Sango2_disc.bin" (
  echo [1/3] Hoan nguyen dia CD PIONEERV01...
  if exist "%GAME%CD-ROM\Restore Disc.bat" (
    call "%GAME%CD-ROM\Restore Disc.bat"
  ) else (
    cd /d "%ROOT%"
    python dich.py sango2-cd --game "%ROOT%" restore --copy
    cd /d "%GAME%"
  )
) else (
  echo [1/3] Dia CD restored OK
)

REM --- Deploy syllable ---
echo [2/3] Deploy font + EXE co dau...
call "%GAME%Deploy Syllable.bat"
if %ERRORLEVEL% neq 0 pause & exit /b 1

REM --- Choi ---
echo [3/3] Mo DOSBox (auto mount CD + nhac)...
call "%GAME%Play Sango2 Syllable.bat"
