@echo off

cd /d "%~dp0"
set "VENV=venv"
set "PY=%VENV%\Scripts\python.exe"

if not exist "%PY%" (
    echo Creating virtual environment...
    python -m venv "%VENV%" || goto :error
)

echo Installing dependencies...
"%PY%" -m pip install --upgrade pip || goto :error
"%PY%" -m pip install -r requirements.txt || goto :error

echo Building...
"%PY%" -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name TaskEcho ^
    --icon "img\favicon.ico" ^
    --add-data "ui;ui" ^
    --add-data "img;img" ^
    "src\main.py" || goto :error

echo.
echo Build complete: dist\TaskEcho.exe
pause
exit /b 0

:error
echo.
echo Build failed.
pause
