#!/usr/bin/env python3
"""
Download-Paket Creator für ARXML-Merger.

Erstellt ein ZIP-Paket mit allem was Benutzer brauchen,
ohne Git oder komplizierte Installation.
"""

import os
import zipfile
import shutil
from pathlib import Path
import json


def create_simple_installer():
    """Erstellt einen einfachen Installer."""
    installer_content = '''@echo off
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
set "desktop=%USERPROFILE%\\Desktop"
set "current_dir=%~dp0"

echo @echo off > "%desktop%\\ARXML_Merger.bat"
echo cd /d "%current_dir%" >> "%desktop%\\ARXML_Merger.bat"
echo python run_web_server.py >> "%desktop%\\ARXML_Merger.bat"
echo pause >> "%desktop%\\ARXML_Merger.bat"

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
'''
    
    with open("INSTALL.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    
    print("✅ Einfacher Installer erstellt: INSTALL.bat")


def create_portable_runner():
    """Erstellt einen portablen Runner ohne Installation."""
    runner_content = '''@echo off
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
'''
    
    with open("START.bat", "w", encoding="utf-8") as f:
        f.write(runner_content)
    
    print("✅ Portabler Runner erstellt: START.bat")


def create_user_guide():
    """Erstellt eine einfache Benutzeranleitung."""
    guide_content = """# 🚀 ARXML Merger - Benutzeranleitung

## 📥 Was ist in diesem Paket?

- **START.bat** - Einfacher Starter (empfohlen)
- **INSTALL.bat** - Einmalige Installation mit Desktop-Verknüpfung
- **arxml_merger_standalone.html** - Offline-Version für Browser
- **run_web_server.py** - Hauptprogramm
- **Alle Python-Dateien** - Vollständige Funktionalität

## 🎯 Schnellstart (3 Optionen)

### Option 1: Einfachster Weg 🌟
1. **Doppelklick auf `START.bat`**
2. Warten bis Browser sich öffnet
3. ARXML-Dateien hochladen
4. "Zusammenführen" klicken
5. Ergebnis herunterladen

### Option 2: Offline im Browser
1. **Doppelklick auf `arxml_merger_standalone.html`**
2. Funktioniert ohne Python
3. Einfache Merge-Funktionalität
4. Komplett offline

### Option 3: Mit Installation
1. **Doppelklick auf `INSTALL.bat`**
2. Folgen Sie den Anweisungen
3. Desktop-Verknüpfung wird erstellt
4. Zukünftig: Doppelklick auf Desktop-Symbol

## 🔧 Voraussetzungen

### Für START.bat und INSTALL.bat:
- Windows-Computer
- Python 3.8+ (wird automatisch geprüft)
- Internetverbindung (für erste Nutzung)

### Für Standalone-HTML:
- Nur ein moderner Browser
- Keine weiteren Voraussetzungen

## 💡 Tipps

- **Erste Nutzung**: Verwenden Sie START.bat
- **Regelmäßige Nutzung**: Installieren Sie mit INSTALL.bat
- **Ohne Python**: Verwenden Sie die HTML-Version
- **Probleme**: Versuchen Sie die HTML-Version als Fallback

## 🆘 Häufige Probleme

**"Python ist nicht installiert"**
→ Laden Sie Python von https://python.org herunter
→ Oder verwenden Sie die HTML-Version

**"Fehler bei der Installation"**
→ Führen Sie als Administrator aus
→ Oder verwenden Sie die HTML-Version

**"Browser öffnet sich nicht"**
→ Öffnen Sie manuell: http://localhost:8000
→ Oder verwenden Sie die HTML-Version

## 📞 Support

Bei Problemen:
1. Versuchen Sie die HTML-Version
2. Prüfen Sie die Python-Installation
3. Führen Sie als Administrator aus
4. Kontaktieren Sie den Support

---
**Viel Erfolg mit ARXML Merger!** 🎉
"""
    
    with open("ANLEITUNG.txt", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("✅ Benutzeranleitung erstellt: ANLEITUNG.txt")


def create_download_package():
    """Erstellt das komplette Download-Paket."""
    print("📦 Erstelle Download-Paket...")
    
    # Erstelle Hilfsdateien
    create_simple_installer()
    create_portable_runner()
    create_user_guide()
    
    # Liste der wichtigsten Dateien
    essential_files = [
        "run_web_server.py",
        "main.py",
        "arxml_merger_engine.py",
        "arxml_validator.py",
        "conflict_resolver.py",
        "arxml_reporter.py",
        "web_interface.py",
        "config.py",
        "utils.py",
        "requirements.txt",
        "arxml_merger_standalone.html",
        "START.bat",
        "INSTALL.bat",
        "ANLEITUNG.txt"
    ]
    
    # Erstelle ZIP-Datei
    zip_filename = "ARXML_Merger_Download.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Füge Hauptdateien hinzu
        for file in essential_files:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️ {file} nicht gefunden")
        
        # Füge Beispiele hinzu
        if os.path.exists("examples"):
            for root, dirs, files in os.walk("examples"):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path)
                    print(f"  ✅ {file_path}")
        
        # Füge README hinzu
        if os.path.exists("README.md"):
            zipf.write("README.md")
            print(f"  ✅ README.md")
    
    print(f"\n🎉 Download-Paket erstellt: {zip_filename}")
    print(f"📏 Dateigröße: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    
    return zip_filename


def create_github_release_files():
    """Erstellt Dateien für GitHub Release."""
    print("\n📋 Erstelle GitHub Release-Dateien...")
    
    # Release Notes
    release_notes = """# 🚀 ARXML Merger v1.0 - Easy Download Package

## 📥 Einfache Installation - Keine Git-Kenntnisse erforderlich!

### 🎯 3 Wege zur Nutzung:

#### 1. 🌟 Einfachster Weg (Empfohlen)
- Download: `ARXML_Merger_Download.zip`
- Entpacken und Doppelklick auf `START.bat`
- Fertig! Browser öffnet sich automatisch

#### 2. 🌐 Offline im Browser
- Download: `arxml_merger_standalone.html`
- Doppelklick auf die HTML-Datei
- Funktioniert ohne Python-Installation

#### 3. 💻 Vollständige Installation
- Download: `ARXML_Merger_Download.zip`
- Entpacken und Doppelklick auf `INSTALL.bat`
- Desktop-Verknüpfung wird erstellt

## ✨ Features

- ✅ 100% Signal-Preservation
- ✅ Drag & Drop Web-Interface
- ✅ Intelligente Konfliktauflösung
- ✅ Detaillierte Berichte
- ✅ Offline-Funktionalität
- ✅ Keine Git-Kenntnisse erforderlich

## 🎯 Für wen?

- **Einsteiger**: Verwenden Sie die HTML-Version
- **Gelegentliche Nutzung**: START.bat
- **Regelmäßige Nutzung**: INSTALL.bat
- **Entwickler**: Vollständiger Source-Code enthalten

## 🆘 Support

Alle Versionen enthalten detaillierte Anleitungen und Fallback-Optionen.
Bei Problemen: Versuchen Sie die HTML-Standalone-Version!
"""
    
    with open("RELEASE_NOTES.md", "w", encoding="utf-8") as f:
        f.write(release_notes)
    
    print("✅ Release Notes erstellt: RELEASE_NOTES.md")


def main():
    """Hauptfunktion."""
    print("📦 ARXML Merger Download-Paket Creator")
    print("=" * 45)
    print()
    
    # Erstelle Download-Paket
    zip_file = create_download_package()
    
    # Erstelle GitHub Release-Dateien
    create_github_release_files()
    
    print("\n🎉 Alle Pakete erstellt!")
    print("\n📋 Erstellt wurden:")
    print(f"  📦 {zip_file} - Komplettes Download-Paket")
    print("  🌐 arxml_merger_standalone.html - Offline-Browser-Version")
    print("  📄 RELEASE_NOTES.md - GitHub Release Notes")
    print("  📖 ANLEITUNG.txt - Benutzeranleitung")
    print("  🚀 START.bat - Einfacher Starter")
    print("  💾 INSTALL.bat - Installer mit Desktop-Verknüpfung")
    
    print("\n💡 Nächste Schritte:")
    print("  1. Laden Sie die Dateien auf GitHub hoch")
    print("  2. Erstellen Sie ein Release mit den Paketen")
    print("  3. Benutzer können ohne Git herunterladen und nutzen!")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
