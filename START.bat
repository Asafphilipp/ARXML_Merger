@echo off
title ARXML Merger - Portable Version
echo 🚀 ARXML Merger - Portable Version
echo ==================================
echo.

REM Prüfe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert!
    echo.
    echo 💡 Zwei Optionen:
    echo   1. Python installieren von: https://python.org
    echo   2. Standalone-HTML-Version verwenden
    echo.
    echo 🌐 Öffne Standalone-Version...
    start arxml_merger_standalone.html
    pause
    exit /b 0
)

echo ✅ Python gefunden
echo 📦 Prüfe Dependencies...

REM Versuche Dependencies zu installieren
pip install chardet psutil >nul 2>&1

echo 🚀 Starte ARXML Merger...
echo 📡 Web-Interface wird unter http://localhost:8000 geöffnet
echo ⏹️  Drücken Sie Ctrl+C zum Beenden
echo.

python run_web_server.py

echo.
echo 👋 ARXML Merger beendet
pause
