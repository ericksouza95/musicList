@echo off
echo.
echo 🎵================================🎵
echo      MUSIC LIST SYSTEM LAUNCHER
echo 🎵================================🎵
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não está instalado!
    echo Baixe em: https://python.org
    pause
    exit /b 1
)

REM Executar o launcher Python
python start_app.py

pause 