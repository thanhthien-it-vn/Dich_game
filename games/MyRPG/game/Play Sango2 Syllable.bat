@echo off
REM Choi Sango II — syllable co dau (VigameV1.0)
cd /d "%~dp0"

if not exist "SANGO2\SAN2-VN.EXE" (
  echo Chua deploy! Chay: Deploy Syllable.bat
  pause
  exit /b 1
)

if not exist "SANGO2\FONT16-SYLLABLE.PAT" (
  echo Thieu FONT16-SYLLABLE.PAT — build lai pipeline
  pause
  exit /b 1
)

REM Tu dong deploy font + exe moi nhat
call "%~dp0Deploy Syllable.bat"

set SDL_AUDIODRIVER=winmm
if exist "C:\DOSBox-X\dosbox-x.exe" (
  "C:\DOSBox-X\dosbox-x.exe" -conf "%~dp0play_syllable.conf"
) else (
  echo Cai DOSBox-X hoac chinh duong dan trong play_syllable.conf
  pause
)
