@echo off
REM Deploy ban syllable CO DAU vao thu muc SANGO2 (chay tu game\)
setlocal
cd /d "%~dp0"
set "GAME=%~dp0.."
set "SANGO=%~dp0SANGO2"

echo === Deploy Sango II Syllable (co dau) ===
echo SANGO2: %SANGO%
echo.

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python "%GAME%\..\..\tools\adapters\sango2\deploy_syllable.py" --game "%GAME%"
  if %ERRORLEVEL% neq 0 exit /b 1
  echo.
  echo Chay: Play Sango2 Syllable.bat
  exit /b 0
)

if not exist "%GAME%\patch\SAN2-SYLLABLE.EXE" (
  echo LOI: Chua co patch\SAN2-SYLLABLE.EXE
  echo Chay: python dich.py sango2 --game ... --patch-font --patch-exe
  exit /b 1
)

copy /Y "%GAME%\patch\SAN2-SYLLABLE.EXE" "%SANGO%\SAN2-VN.EXE"
copy /Y "%SANGO%\FONT16-SYLLABLE.PAT" "%SANGO%\FONT16.PAT"
copy /Y "%SANGO%\FONT16-SYLLABLE.PAT" "%SANGO%\FONT16-VN.PAT"
copy /Y "%SANGO%\FONT24-SYLLABLE.PAT" "%SANGO%\FONT24.PAT"
copy /Y "%SANGO%\FONT24-SYLLABLE.PAT" "%SANGO%\FONT24-VN.PAT"

echo.
echo OK da copy:
echo   SAN2-VN.EXE      ^<= patch syllable co dau
echo   FONT16.PAT        ^<= FONT16-SYLLABLE.PAT
echo   FONT24.PAT        ^<= FONT24-SYLLABLE.PAT
echo.
echo Chay: Play Sango2 Syllable.bat
endlocal
