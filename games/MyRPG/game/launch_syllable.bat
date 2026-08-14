@echo off
REM Chay trong DOSBox — mount CD + khoi dong Sango II syllable
setlocal

cd /d C:\

REM --- Mount CD-ROM (can MSCDEX + nhac SANGO.WAV) ---
if exist C:\CD-ROM\Sango2.cue (
  imgmount d C:\CD-ROM\Sango2.cue -t cdrom
  goto :cd_ok
)
if exist C:\CD-ROM\Sango2.ccd (
  imgmount d C:\CD-ROM\Sango2.ccd -t cdrom
  goto :cd_ok
)
if exist C:\CD-ROM\SANGO2.CUE (
  imgmount d C:\CD-ROM\SANGO2.CUE -t cdrom
  goto :cd_ok
)
if exist C:\Sango2\Sango2.ccd (
  imgmount d C:\Sango2\Sango2.ccd -t cdrom
  goto :cd_ok
)
if exist C:\CD-ROM\ (
  mount d C:\CD-ROM -t cdrom -label PIONEERV.01
  goto :cd_ok
)

echo.
echo CANH BAO: Khong tim thay CD image!
echo Dat vao C:\CD-ROM\ :
echo   Sango2.cue + Sango2.bin   (co nhac CD day du)
echo   hoac Sango2.ccd + .img
echo   hoac copy noi dung dia CD vao thu muc CD-ROM
echo.
goto :play

:cd_ok
echo CD-ROM mounted as D:

:play
cd SANGO2
if not exist SAN2-VN.EXE (
  echo LOI: Chua co SAN2-VN.EXE — chay Deploy Syllable.bat tren Windows
  pause
  exit /b 1
)
if not exist FONT16.PAT (
  echo LOI: Chua co FONT16.PAT — chay Deploy Syllable.bat tren Windows
  pause
  exit /b 1
)
C:\UNIVBE
SAN2-VN
