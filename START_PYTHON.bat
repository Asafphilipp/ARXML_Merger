@echo off
echo.
echo ========================================
echo 🚀 ARXML MERGER - PYTHON VERSION
echo ========================================
echo.
echo ✅ KEINE Windows-Schutzwarnung!
echo ✅ Direkte Python-Ausführung
echo ✅ FUNKTIONIERT SOFORT!
echo.

REM Python-Version prüfen
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nicht gefunden!
    echo 📥 Bitte Python von https://python.org installieren
    echo    Download: https://python.org/downloads/
    echo.
    echo 💡 ALTERNATIVE: Verwenden Sie die .exe Version
    echo    und klicken Sie bei der Warnung auf "Trotzdem ausführen"
    echo.
    pause
    exit /b 1
)

echo ✅ Python gefunden
echo.

REM Abhängigkeiten prüfen
echo 🔍 Prüfe Abhängigkeiten...
python -c "import xml.etree.ElementTree" >nul 2>&1
if errorlevel 1 (
    echo ❌ XML-Bibliothek nicht verfügbar
    pause
    exit /b 1
)

echo ✅ Alle Abhängigkeiten verfügbar
echo.

REM Programm starten
echo 🚀 Starte ARXML Merger...
echo.
python arxml_merger_console.py

echo.
echo 👋 Programm beendet
pause
