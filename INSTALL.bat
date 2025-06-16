@echo off
echo 🚀 ARXML Merger - Einfache Installation
echo =====================================
echo.

REM Prüfe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert!
    echo 💡 Bitte installieren Sie Python von: https://python.org
    echo    Stellen Sie sicher, dass "Add to PATH" aktiviert ist
    pause
    exit /b 1
)

echo ✅ Python gefunden
echo.

REM Installiere Dependencies
echo 📦 Installiere benötigte Pakete...
pip install chardet psutil

if errorlevel 1 (
    echo ❌ Fehler bei der Installation
    pause
    exit /b 1
)

echo ✅ Installation erfolgreich!
echo.

REM Erstelle Desktop-Verknüpfung
echo 🖥️ Erstelle Desktop-Verknüpfung...
set "desktop=%USERPROFILE%\Desktop"
set "current_dir=%~dp0"

echo @echo off > "%desktop%\ARXML_Merger.bat"
echo cd /d "%current_dir%" >> "%desktop%\ARXML_Merger.bat"
echo python run_web_server.py >> "%desktop%\ARXML_Merger.bat"
echo pause >> "%desktop%\ARXML_Merger.bat"

echo ✅ Desktop-Verknüpfung erstellt
echo.

echo 🎉 Installation abgeschlossen!
echo.
echo 📋 So verwenden Sie ARXML Merger:
echo   1. Doppelklick auf Desktop-Verknüpfung "ARXML_Merger.bat"
echo   2. Browser öffnet automatisch http://localhost:8000
echo   3. ARXML-Dateien hochladen und zusammenführen
echo.
echo 💡 Alternativ: Doppelklick auf "run_web_server.py"
echo.
pause
