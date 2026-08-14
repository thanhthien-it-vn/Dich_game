@echo off
cls
echo Now copy all crack file to HardDisk ....
pause
if exist C:\sango2\*.* goto C
if exist D:\sango2\*.* goto D
if exist E:\sango2\*.* goto E
if exist F:\sango2\*.* goto F
GOTO NOT

:C
echo Copy file to c:\sango2 .............
copy  SAN2.VMC        C:\SANGO2  /Y
copy  NEWHERO.DAT     C:\SANGO2  /Y
copy  GO8MB.BAT       C:\SANGO2  /Y
copy  SAN2.EXE        C:\SANGO2  /Y
c:
cd \sango2
GOTO DONE

:D
echo Copy file to c:\sango2 .............
copy  SAN2.VMC        D:\SANGO2  /Y
copy  NEWHERO.DAT     D:\SANGO2  /Y
copy  GO8MB.BAT       D:\SANGO2  /Y
copy  SAN2.EXE        D:\SANGO2  /Y
d:
cd \sango2
GOTO DONE

:E
echo Copy file to c:\sango2 .............
copy  SAN2.VMC        E:\SANGO2  /Y
copy  NEWHERO.DAT     E:\SANGO2  /Y
copy  GO8MB.BAT       E:\SANGO2  /Y
copy  SAN2.EXE        E:\SANGO2  /Y
e:
cd \sango2
GOTO DONE

:F
echo Copy file to c:\sango2 .............
copy  SAN2.VMC        F:\SANGO2  /Y
copy  NEWHERO.DAT     F:\SANGO2  /Y
copy  GO8MB.BAT       F:\SANGO2  /Y
copy  SAN2.EXE        F:\SANGO2  /Y
f:
cd \sango2
GOTO DONE



:DONE
cls
ECHO Complete !!
echo Run go8mb.bat or go4mb.bat to play.
goto end

:not
cls
echo Can't found sango2 in harddisk, please run install.bat from cd-rom !!
goto end


:end
