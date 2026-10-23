@echo off
chcp 65001 > nul
title Kutubxonalarni o'rnatish
echo ===================================================
echo   Kerakli Python kutubxonalari o'rnatilmoqda...
echo ===================================================
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ===================================================
echo   O'rnatish yakunlandi! Endi "run.bat" ni bosing.
echo ===================================================
pause
