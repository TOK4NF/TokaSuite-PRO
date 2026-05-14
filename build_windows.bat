@echo off
setlocal
title Build Toka Suite Pro - Windows
echo.
echo Build Windows de Toka Suite Pro
echo.

py -m venv .venv || goto error
call .venv\Scripts\activate || goto error
python -m pip install --upgrade pip setuptools wheel || goto error
python -m pip install --no-cache-dir -r requirements.txt || goto error
python -m PyInstaller --noconfirm --onefile --windowed --name "TokaSuitePro" app.py || goto error

echo.
echo Termine !
echo Ton .exe est ici : dist\TokaSuitePro.exe
pause
goto end

:error
echo.
echo Une erreur est arrivee. Copie le message d'erreur et envoie-le.
pause
exit /b 1

:end
