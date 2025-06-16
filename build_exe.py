#!/usr/bin/env python3
"""
EXE-Builder für ARXML-Merger.

Dieses Skript erstellt eine portable .exe-Datei des ARXML-Mergers,
die ohne Python-Installation ausgeführt werden kann.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Prüft ob PyInstaller installiert ist."""
    try:
        import PyInstaller
        print("✅ PyInstaller ist verfügbar")
        return True
    except ImportError:
        print("❌ PyInstaller ist nicht installiert")
        print("💡 Installiere PyInstaller mit: pip install pyinstaller")
        return False


def install_pyinstaller():
    """Installiert PyInstaller."""
    print("📦 Installiere PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller erfolgreich installiert")
        return True
    except subprocess.CalledProcessError:
        print("❌ Fehler bei der PyInstaller-Installation")
        return False


def create_exe():
    """Erstellt die EXE-Datei."""
    print("🔨 Erstelle portable EXE-Datei...")
    
    # PyInstaller-Kommando
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Einzelne EXE-Datei
        "--windowed",                   # Kein Konsolen-Fenster (für GUI)
        "--name", "ARXML_Merger",       # Name der EXE
        "--icon", "icon.ico",           # Icon (falls vorhanden)
        "--add-data", "examples;examples",  # Beispiel-Dateien einbetten
        "--hidden-import", "chardet",
        "--hidden-import", "psutil",
        "--hidden-import", "xml.etree.ElementTree",
        "run_web_server.py"             # Haupt-Skript
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ EXE-Datei erfolgreich erstellt")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Erstellen der EXE: {e}")
        return False


def create_simple_exe():
    """Erstellt eine einfache EXE ohne GUI."""
    print("🔨 Erstelle einfache CLI-EXE...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "ARXML_Merger_CLI",
        "--hidden-import", "chardet",
        "--hidden-import", "psutil",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ CLI-EXE erfolgreich erstellt")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Erstellen der CLI-EXE: {e}")
        return False


def create_batch_launcher():
    """Erstellt eine Batch-Datei zum einfachen Starten."""
    batch_content = '''@echo off
echo 🚀 ARXML Merger wird gestartet...
echo.
echo 📡 Web-Interface wird unter http://localhost:8000 geöffnet
echo ⏹️  Drücken Sie Ctrl+C zum Beenden
echo.
ARXML_Merger.exe
pause
'''
    
    with open("Start_ARXML_Merger.bat", "w") as f:
        f.write(batch_content)
    
    print("✅ Batch-Launcher erstellt: Start_ARXML_Merger.bat")


def create_readme_exe():
    """Erstellt eine README für die EXE-Version."""
    readme_content = """# ARXML Merger - Portable Version

## 🚀 Schnellstart

### Option 1: Doppelklick
1. Doppelklick auf `ARXML_Merger.exe`
2. Browser öffnet automatisch http://localhost:8000
3. ARXML-Dateien hochladen und mergen

### Option 2: Batch-Datei
1. Doppelklick auf `Start_ARXML_Merger.bat`
2. Folgen Sie den Anweisungen

### Option 3: Command Line
1. Öffnen Sie Eingabeaufforderung (cmd)
2. Navigieren Sie zum Ordner mit der EXE
3. Führen Sie aus: `ARXML_Merger_CLI.exe merge output.arxml input1.arxml input2.arxml`

## 📁 Dateien in diesem Paket

- `ARXML_Merger.exe` - Hauptprogramm mit Web-Interface
- `ARXML_Merger_CLI.exe` - Command-Line-Version
- `Start_ARXML_Merger.bat` - Einfacher Starter
- `arxml_merger_standalone.html` - Offline-Browser-Version
- `README_EXE.txt` - Diese Anleitung

## 💡 Tipps

- Keine Python-Installation erforderlich
- Funktioniert auf jedem Windows-Computer
- Alle Dateien bleiben lokal auf Ihrem Computer
- Für erweiterte Features verwenden Sie die CLI-Version

## 🆘 Probleme?

Falls die EXE nicht startet:
1. Prüfen Sie, ob Windows Defender die Datei blockiert
2. Führen Sie als Administrator aus
3. Verwenden Sie die Standalone-HTML-Version als Alternative
"""
    
    with open("README_EXE.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README für EXE-Version erstellt")


def main():
    """Hauptfunktion."""
    print("🏗️  ARXML Merger EXE Builder")
    print("=" * 40)
    print()
    
    # Prüfe PyInstaller
    if not check_pyinstaller():
        if input("PyInstaller installieren? (j/n): ").lower() == 'j':
            if not install_pyinstaller():
                return 1
        else:
            print("❌ PyInstaller erforderlich für EXE-Erstellung")
            return 1
    
    print()
    
    # Erstelle EXE-Dateien
    success = True
    
    print("1️⃣ Erstelle Web-Interface EXE...")
    if not create_exe():
        success = False
    
    print("\n2️⃣ Erstelle CLI EXE...")
    if not create_simple_exe():
        success = False
    
    print("\n3️⃣ Erstelle Hilfsdateien...")
    create_batch_launcher()
    create_readme_exe()
    
    if success:
        print("\n🎉 EXE-Erstellung erfolgreich!")
        print("📁 Dateien befinden sich im 'dist/' Ordner")
        print("\n📋 Erstellt wurden:")
        print("  - ARXML_Merger.exe (Web-Interface)")
        print("  - ARXML_Merger_CLI.exe (Command-Line)")
        print("  - Start_ARXML_Merger.bat (Einfacher Starter)")
        print("  - README_EXE.txt (Anleitung)")
        
        # Kopiere zusätzliche Dateien
        dist_dir = Path("dist")
        if dist_dir.exists():
            try:
                shutil.copy("arxml_merger_standalone.html", dist_dir)
                shutil.copy("Start_ARXML_Merger.bat", dist_dir)
                shutil.copy("README_EXE.txt", dist_dir)
                print("  - arxml_merger_standalone.html (Offline-Version)")
                print("\n✅ Alle Dateien in 'dist/' kopiert")
            except Exception as e:
                print(f"⚠️ Warnung beim Kopieren: {e}")
        
        print("\n🚀 Bereit für Verteilung!")
        return 0
    else:
        print("\n❌ Fehler bei der EXE-Erstellung")
        return 1


if __name__ == '__main__':
    sys.exit(main())
