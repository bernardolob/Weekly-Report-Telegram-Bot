@echo off


cd C:\Users\berna\Documents\telegram-bot

echo ------------- >> .\logs\weekend.log

echo Task started at %DATE% %TIME% >> .\logs\weekend.log


echo Running weekend task >> C:\Users\berna\Documents\telegram-bot\logs\weekend.log


echo Working dir: %CD% >> .\logs\weekend.log

REM --- Start python in background ---
start "TelegramBot" /B /D C:\Users\berna\Documents\telegram-bot cmd /c "python .\main.py"


echo Starting timer >> .\logs\weekend.log

REM --- Wait 5 minutes (300 seconds) ---
timeout /t 40 /nobreak

REM --- Kill python process ---
taskkill /IM python.exe
echo Killed Python >> .\logs\weekend.log

REM --- Suspend ---
echo Shutting Down >> .\logs\weekend.log

