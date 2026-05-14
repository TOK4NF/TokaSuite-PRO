@echo off
setlocal
title Toka Suite Pro - Windows
echo.
echo        T O K A   S U I T E   P R O
echo.

py -m venv .venv || goto error
call .venv\Scripts\activate || goto error
python -m pip install --upgrade pip setuptools wheel || goto error
python -m pip install --no-cache-dir -r requirements.txt || goto error
python app.py || goto error
goto end

:error
echo.
echo Une erreur est arrivee. Copie le message d'erreur et envoie-le.
pause
exit /b 1

:end
pause
