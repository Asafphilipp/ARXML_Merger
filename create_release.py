#!/usr/bin/env python3
"""
ARXML Merger - Release Creator
Erstellt automatisch Release-Pakete für verschiedene Zielgruppen.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_release_packages():
    """Erstellt verschiedene Release-Pakete."""
    
    # Basis-Verzeichnis
    base_dir = Path(__file__).parent
    release_dir = base_dir / "releases"
    
    # Release-Verzeichnis erstellen
    release_dir.mkdir(exist_ok=True)
    
    # Aktuelle Version
    version = "v2.0.0"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"🚀 Erstelle Release-Pakete für {version}")
    
    # 1. Komplettes Paket (für Entwickler)
    create_complete_package(base_dir, release_dir, version)
    
    # 2. HTML-Only Paket (für Endbenutzer)
    create_html_package(base_dir, release_dir, version)
    
    # 3. Standalone HTML-Dateien (einzeln)
    create_standalone_files(base_dir, release_dir, version)
    
    print(f"✅ Alle Release-Pakete erstellt in: {release_dir}")

def create_complete_package(base_dir, release_dir, version):
    """Erstellt das komplette Paket mit allen Funktionen."""
    
    package_name = f"ARXML_Merger_Complete_{version}"
    package_dir = release_dir / package_name
    
    # Verzeichnis erstellen
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Dateien kopieren
    files_to_copy = [
        # Python-Module
        "main.py",
        "arxml_merger_engine.py",
        "arxml_validator.py",
        "conflict_resolver.py",
        "arxml_reporter.py",
        "web_interface.py",
        "config.py",
        "utils.py",
        "requirements.txt",
        
        # HTML-Versionen
        "arxml_merger_working.html",
        "arxml_merger_standalone.html",
        "arxml_merger_simple.html",
        "download.html",
        
        # Setup-Dateien
        "START.bat",
        "INSTALL.bat",
        "run_web_server.py",
        "install.py",
        "build_exe.py",
        "create_download_package.py",
        
        # Konfiguration
        "arxml_merger_config.json",
        
        # Dokumentation
        "README.md",
        "BENUTZERANLEITUNG.md",
        "TROUBLESHOOTING.md",
        "ANLEITUNG.txt",
        "RELEASE_NOTES.md",
        "VERSION.md",
    ]
    
    for file_name in files_to_copy:
        src = base_dir / file_name
        if src.exists():
            shutil.copy2(src, package_dir / file_name)
    
    # Examples-Verzeichnis kopieren
    examples_src = base_dir / "examples"
    if examples_src.exists():
        shutil.copytree(examples_src, package_dir / "examples")
    
    # ZIP erstellen
    zip_path = release_dir / f"{package_name}.zip"
    create_zip(package_dir, zip_path)
    
    print(f"✅ Komplettes Paket: {zip_path}")

def create_html_package(base_dir, release_dir, version):
    """Erstellt ein Paket nur mit HTML-Versionen."""
    
    package_name = f"ARXML_Merger_HTML_Only_{version}"
    package_dir = release_dir / package_name
    
    # Verzeichnis erstellen
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # HTML-Dateien kopieren
    html_files = [
        "arxml_merger_working.html",
        "arxml_merger_standalone.html",
        "arxml_merger_simple.html",
        "download.html"
    ]
    
    for file_name in html_files:
        src = base_dir / file_name
        if src.exists():
            shutil.copy2(src, package_dir / file_name)
    
    # Dokumentation kopieren
    doc_files = [
        "BENUTZERANLEITUNG.md",
        "TROUBLESHOOTING.md",
        "ANLEITUNG.txt"
    ]
    
    for file_name in doc_files:
        src = base_dir / file_name
        if src.exists():
            shutil.copy2(src, package_dir / file_name)
    
    # README für HTML-Paket erstellen
    html_readme = package_dir / "README_HTML.txt"
    with open(html_readme, 'w', encoding='utf-8') as f:
        f.write(f"""
🚀 ARXML Merger - HTML-Only Paket {version}

📁 Enthaltene Dateien:
- arxml_merger_working.html     ✅ Funktioniert garantiert
- arxml_merger_standalone.html  ✅ Erweiterte Version  
- arxml_merger_simple.html      ✅ Einfache Version
- download.html                 📥 Download-Seite

🎯 Verwendung:
1. Doppelklick auf eine HTML-Datei
2. ARXML-Dateien per Drag & Drop hochladen
3. "Zusammenführen" klicken
4. Ergebnis herunterladen

⚠️ WICHTIG:
- Dateien müssen LOKAL gespeichert werden
- Nicht direkt von GitHub öffnen
- Funktioniert komplett offline

📖 Hilfe:
- BENUTZERANLEITUNG.md - Einfache Anleitung für alle
- TROUBLESHOOTING.md - Problemlösungen
""")
    
    # ZIP erstellen
    zip_path = release_dir / f"{package_name}.zip"
    create_zip(package_dir, zip_path)
    
    print(f"✅ HTML-Paket: {zip_path}")

def create_standalone_files(base_dir, release_dir, version):
    """Kopiert einzelne HTML-Dateien für direkten Download."""
    
    standalone_dir = release_dir / "standalone"
    standalone_dir.mkdir(exist_ok=True)
    
    html_files = [
        ("arxml_merger_working.html", "ARXML_Merger_Working.html"),
        ("arxml_merger_standalone.html", "ARXML_Merger_Standalone.html"),
        ("arxml_merger_simple.html", "ARXML_Merger_Simple.html")
    ]
    
    for src_name, dst_name in html_files:
        src = base_dir / src_name
        dst = standalone_dir / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"✅ Standalone-Datei: {dst}")

def create_zip(source_dir, zip_path):
    """Erstellt eine ZIP-Datei aus einem Verzeichnis."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(source_dir)
                zipf.write(file_path, arc_name)

if __name__ == "__main__":
    create_release_packages()
