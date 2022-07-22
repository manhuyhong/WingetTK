@echo off
winget upgrade
CHOICE /C YN /M "Do you want to update all"
IF %ERRORLEVEL% EQU 1 winget upgrade --all
IF %ERRORLEVEL% EQU 2 echo Cancelled
echo You can close the terminal now.
pause > nul