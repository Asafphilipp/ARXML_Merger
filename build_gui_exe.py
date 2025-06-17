#!/usr/bin/env python3
"""
ARXML Merger GUI - EXE Builder
Erstellt eine ausführbare .exe-Datei der GUI-Anwendung.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Installiert PyInstaller falls nicht vorhanden."""
    try:
        import PyInstaller
        print("✅ PyInstaller bereits installiert")
        return True
    except ImportError:
        print("📦 Installiere PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller erfolgreich installiert")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Fehler beim Installieren von PyInstaller: {e}")
            return False

def create_exe():
    """Erstellt die .exe-Datei."""
    if not install_pyinstaller():
        return False
        
    print("🔨 Erstelle ausführbare Datei...")
    
    # PyInstaller-Befehl
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Einzelne .exe-Datei
        "--windowed",                   # Kein Konsolen-Fenster
        "--name=ARXML_Merger_GUI",      # Name der .exe
        "--icon=NONE",                  # Kein Icon (kann später hinzugefügt werden)
        "--add-data=README.md;.",       # README mit einpacken
        "arxml_merger_gui.py"           # Haupt-Python-Datei
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ EXE-Datei erfolgreich erstellt!")
        
        # Pfad zur erstellten .exe
        exe_path = Path("dist") / "ARXML_Merger_GUI.exe"
        if exe_path.exists():
            print(f"📁 EXE-Datei: {exe_path.absolute()}")
            print(f"📏 Dateigröße: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            return True
        else:
            print("❌ EXE-Datei nicht gefunden")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Erstellen der EXE: {e}")
        return False

def create_portable_package():
    """Erstellt ein portables Paket."""
    print("📦 Erstelle portables Paket...")
    
    import shutil
    import zipfile
    
    # Verzeichnis für portables Paket
    package_dir = Path("ARXML_Merger_Portable")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # EXE kopieren
    exe_source = Path("dist") / "ARXML_Merger_GUI.exe"
    if exe_source.exists():
        shutil.copy2(exe_source, package_dir / "ARXML_Merger_GUI.exe")
    
    # Dokumentation kopieren
    docs_to_copy = [
        "README.md",
        "BENUTZERANLEITUNG.md",
        "TROUBLESHOOTING.md",
        "ANLEITUNG.txt"
    ]
    
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy2(doc, package_dir / doc)
    
    # Start-Anleitung erstellen
    start_guide = package_dir / "START_HIER.txt"
    with open(start_guide, 'w', encoding='utf-8') as f:
        f.write("""🚀 ARXML Merger - Desktop GUI

📁 VERWENDUNG:
1. Doppelklick auf "ARXML_Merger_GUI.exe"
2. "Dateien hinzufügen" klicken
3. Mindestens 2 ARXML-Dateien auswählen
4. "Zusammenführen" klicken
5. Fertig!

✅ FUNKTIONIERT GARANTIERT:
- Keine Browser-Probleme
- Keine HTML-Dateien
- Echte Desktop-Anwendung
- Drag & Drop für Dateien
- Sofortiges Feedback

📖 HILFE:
- BENUTZERANLEITUNG.md - Ausführliche Anleitung
- TROUBLESHOOTING.md - Bei Problemen
- README.md - Vollständige Dokumentation

🎯 VORTEILE:
- Funktioniert offline
- Keine Installation erforderlich
- Portable - kann auf USB-Stick
- Einfache Bedienung
- Professionelle GUI

💡 TIPP:
Die .exe-Datei kann direkt ausgeführt werden.
Keine Python-Installation erforderlich!
""")
    
    # ZIP erstellen
    zip_path = Path("ARXML_Merger_GUI_Portable.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Portables Paket erstellt: {zip_path.absolute()}")
    print(f"📏 ZIP-Größe: {zip_path.stat().st_size / (1024*1024):.1f} MB")
    
    return True

def main():
    """Hauptfunktion."""
    print("🚀 ARXML Merger GUI - EXE Builder")
    print("=" * 50)
    
    # Prüfe ob GUI-Datei existiert
    if not Path("arxml_merger_gui.py").exists():
        print("❌ arxml_merger_gui.py nicht gefunden!")
        return False
    
    # Erstelle EXE
    if not create_exe():
        return False
    
    # Erstelle portables Paket
    if not create_portable_package():
        return False
    
    print("\n🎉 ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 50)
    print("📁 Dateien erstellt:")
    print("  - dist/ARXML_Merger_GUI.exe (Einzelne EXE)")
    print("  - ARXML_Merger_GUI_Portable.zip (Komplettes Paket)")
    print("\n💡 VERWENDUNG:")
    print("  1. ZIP entpacken")
    print("  2. Doppelklick auf ARXML_Merger_GUI.exe")
    print("  3. Dateien auswählen und zusammenführen")
    print("\n✅ FUNKTIONIERT GARANTIERT - KEINE BROWSER-PROBLEME!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nDrücken Sie Enter zum Beenden...")
    else:
        input("\nDrücken Sie Enter zum Beenden...")
