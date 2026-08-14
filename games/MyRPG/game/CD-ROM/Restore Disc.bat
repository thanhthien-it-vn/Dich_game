@echo off
REM Hoan nguyen dia CD CloneCD (3 file) -> 1 dia ao CUE+BIN
setlocal
cd /d "%~dp0..\.."
set "GAME=%CD%"

echo === Hoan nguyen dia Sango II ===
echo.

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo Can Python. Hoac copy thu cong:
  echo   copy CD-ROM\Sango2.img CD-ROM\restored\Sango2_disc.bin
  echo   chay: python dich.py sango2-cd --game . restore --copy
  pause
  exit /b 1
)

python dich.py sango2-cd --game "%GAME%" restore --copy
if %ERRORLEVEL% neq 0 exit /b 1

echo.
echo Xong! Dia da phuc hoi tai:
echo   %GAME%\game\CD-ROM\restored\
echo      Sango2_disc.cue
echo      Sango2_disc.bin
echo.
echo Choi: Play Sango2 Syllable.bat
echo Ghi CD that: ImgBurn - Write image - chon Sango2_disc.cue
pause
