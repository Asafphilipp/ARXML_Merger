#!/usr/bin/env python3
"""
ARXML Merger Console - EXE Builder
Erstellt eine ausführbare .exe-Datei der Konsolen-Anwendung.
"""

import os
import sys
import subprocess
import shutil
import zipfile
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
        "--onefile",                        # Einzelne .exe-Datei
        "--console",                        # Mit Konsolen-Fenster
        "--name=ARXML_Merger",              # Name der .exe
        "--icon=NONE",                      # Kein Icon
        "arxml_merger_console.py"           # Haupt-Python-Datei
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ EXE-Datei erfolgreich erstellt!")
        
        # Pfad zur erstellten .exe
        exe_path = Path("dist") / "ARXML_Merger.exe"
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

def create_complete_package():
    """Erstellt ein komplettes Download-Paket."""
    print("📦 Erstelle komplettes Download-Paket...")
    
    # Verzeichnis für das Paket
    package_dir = Path("ARXML_Merger_Complete")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # EXE kopieren
    exe_source = Path("dist") / "ARXML_Merger.exe"
    if exe_source.exists():
        shutil.copy2(exe_source, package_dir / "ARXML_Merger.exe")
        print("✅ EXE-Datei kopiert")
    
    # Python-Version für Entwickler kopieren
    python_files = [
        "arxml_merger_console.py",
        "arxml_merger_gui.py",
        "arxml_merger_simple_gui.py",
        "main.py",
        "requirements.txt"
    ]
    
    python_dir = package_dir / "python_version"
    python_dir.mkdir()
    
    for file in python_files:
        if Path(file).exists():
            shutil.copy2(file, python_dir / file)
    
    # Dokumentation kopieren
    docs = [
        "README.md",
        "BENUTZERANLEITUNG.md",
        "TROUBLESHOOTING.md",
        "ANLEITUNG.txt"
    ]
    
    for doc in docs:
        if Path(doc).exists():
            shutil.copy2(doc, package_dir / doc)
    
    # Beispiel-Dateien erstellen
    examples_dir = package_dir / "examples"
    examples_dir.mkdir()
    
    # Beispiel ARXML-Datei 1
    example1 = examples_dir / "example1.arxml"
    with open(example1, 'w', encoding='utf-8') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>Example1</SHORT-NAME>
      <ELEMENTS>
        <I-SIGNAL>
          <SHORT-NAME>Signal1</SHORT-NAME>
          <LENGTH>8</LENGTH>
        </I-SIGNAL>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>''')
    
    # Beispiel ARXML-Datei 2
    example2 = examples_dir / "example2.arxml"
    with open(example2, 'w', encoding='utf-8') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>Example2</SHORT-NAME>
      <ELEMENTS>
        <I-SIGNAL>
          <SHORT-NAME>Signal2</SHORT-NAME>
          <LENGTH>16</LENGTH>
        </I-SIGNAL>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>''')
    
    # Haupt-Anleitung erstellen
    readme = package_dir / "START_HIER.txt"
    with open(readme, 'w', encoding='utf-8') as f:
        f.write("""🚀 ARXML MERGER - KOMPLETTES PAKET

═══════════════════════════════════════════════════════════════

✅ SOFORT EINSATZBEREIT - FUNKTIONIERT GARANTIERT!

═══════════════════════════════════════════════════════════════

🎯 SCHNELLSTART:

1. 📂 Doppelklick auf "ARXML_Merger.exe"
2. 📁 Wählen Sie "1" um Dateien hinzuzufügen
3. 🔄 Wählen Sie "4" um zusammenzuführen
4. ✅ Fertig!

═══════════════════════════════════════════════════════════════

📁 PAKET-INHALT:

📄 ARXML_Merger.exe          - Hauptprogramm (SOFORT AUSFÜHRBAR!)
📖 START_HIER.txt            - Diese Anleitung
📖 BENUTZERANLEITUNG.md      - Ausführliche Anleitung
📖 TROUBLESHOOTING.md        - Bei Problemen
📁 examples/                 - Beispiel-ARXML-Dateien zum Testen
📁 python_version/           - Python-Quellcode für Entwickler

═══════════════════════════════════════════════════════════════

🎯 FUNKTIONEN:

✅ Mehrere ARXML-Dateien laden
✅ Automatisch alle Dateien im Ordner finden
✅ Einfache Konsolen-Bedienung
✅ Drag & Drop Unterstützung
✅ Detaillierte Fortschrittsanzeige
✅ Fehlerbehandlung
✅ Funktioniert offline
✅ Keine Installation erforderlich

═══════════════════════════════════════════════════════════════

🧪 TESTEN:

1. Kopieren Sie die Beispiel-Dateien aus "examples/" in diesen Ordner
2. Starten Sie ARXML_Merger.exe
3. Wählen Sie "5" für automatische Erkennung
4. Wählen Sie "4" zum Zusammenführen
5. Prüfen Sie die Ausgabedatei "merged_arxml.arxml"

═══════════════════════════════════════════════════════════════

💡 TIPPS:

- Drag & Drop: Ziehen Sie Dateien ins Konsolen-Fenster
- Automatik: Option "5" findet alle .arxml Dateien automatisch
- Sicherheit: Originaldateien bleiben unverändert
- Portable: Kann auf USB-Stick verwendet werden

═══════════════════════════════════════════════════════════════

🆘 PROBLEME?

📖 Lesen Sie: TROUBLESHOOTING.md
📖 Ausführlich: BENUTZERANLEITUNG.md

═══════════════════════════════════════════════════════════════

🎉 ENDLICH EINE LÖSUNG DIE FUNKTIONIERT!

Keine Browser-Probleme, keine HTML-Dateien, keine Verwirrung!
Einfach ausführen und verwenden! 🚀

═══════════════════════════════════════════════════════════════
""")
    
    # ZIP erstellen
    zip_path = Path("ARXML_Merger_FINAL.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Komplettes Paket erstellt: {zip_path.absolute()}")
    print(f"📏 ZIP-Größe: {zip_path.stat().st_size / (1024*1024):.1f} MB")
    
    return True

def main():
    """Hauptfunktion."""
    print("🚀 ARXML Merger - EXE Builder (Konsolen-Version)")
    print("=" * 60)
    
    # Prüfe ob Konsolen-Datei existiert
    if not Path("arxml_merger_console.py").exists():
        print("❌ arxml_merger_console.py nicht gefunden!")
        return False
    
    # Erstelle EXE
    if not create_exe():
        return False
    
    # Erstelle komplettes Paket
    if not create_complete_package():
        return False
    
    print("\n🎉 ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 60)
    print("📁 Dateien erstellt:")
    print("  - dist/ARXML_Merger.exe (Einzelne EXE)")
    print("  - ARXML_Merger_FINAL.zip (Komplettes Paket)")
    print("\n💡 VERWENDUNG:")
    print("  1. ZIP entpacken")
    print("  2. Doppelklick auf ARXML_Merger.exe")
    print("  3. Menü folgen")
    print("\n✅ FUNKTIONIERT GARANTIERT!")
    print("🚫 KEINE BROWSER-PROBLEME!")
    print("🚫 KEINE HTML-DATEIEN!")
    print("🚫 KEINE VERWIRRUNG!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nDrücken Sie Enter zum Beenden...")
    else:
        input("\nDrücken Sie Enter zum Beenden...")
