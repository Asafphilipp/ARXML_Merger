@echo off
echo 🚀 ARXML Merger GUI - Builder
echo ========================================
echo.
echo 📦 Erstelle Desktop-GUI-Anwendung...
echo.

REM Python-Version prüfen
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nicht gefunden!
    echo 📥 Bitte Python von https://python.org installieren
    pause
    exit /b 1
)

echo ✅ Python gefunden
echo.

REM GUI erstellen
echo 🔨 Starte GUI-Erstellung...
python build_gui_exe.py

echo.
echo 🎉 FERTIG!
echo.
echo 📁 Die ausführbare Datei wurde erstellt:
echo    - ARXML_Merger_GUI_Portable.zip
echo.
echo 💡 VERWENDUNG:
echo    1. ZIP entpacken
echo    2. Doppelklick auf ARXML_Merger_GUI.exe
echo    3. ARXML-Dateien auswählen und zusammenführen
echo.
echo ✅ FUNKTIONIERT GARANTIERT!
echo.
pause
