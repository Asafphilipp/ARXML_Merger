#!/usr/bin/env python3
"""
Installations-Skript für ARXML-Merger.

Dieses Skript prüft die Systemvoraussetzungen und installiert
alle notwendigen Dependencies für den ARXML-Merger.
"""

import sys
import subprocess
import os
from pathlib import Path
import platform


def check_python_version():
    """Prüft die Python-Version."""
    print("🐍 Prüfe Python-Version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} ist zu alt")
        print("💡 Mindestens Python 3.8 erforderlich")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} ist kompatibel")
    return True


def check_pip():
    """Prüft ob pip verfügbar ist."""
    print("📦 Prüfe pip-Installation...")
    
    try:
        import pip
        print("✅ pip ist verfügbar")
        return True
    except ImportError:
        print("❌ pip ist nicht installiert")
        print("💡 Installieren Sie pip: https://pip.pypa.io/en/stable/installation/")
        return False


def install_requirements():
    """Installiert die Requirements."""
    print("📥 Installiere Dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt nicht gefunden")
        return False
    
    try:
        # Installiere Requirements
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies erfolgreich installiert")
            return True
        else:
            print("❌ Fehler bei der Installation:")
            print(result.stderr)
            return False
    
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False


def test_imports():
    """Testet ob alle Module importiert werden können."""
    print("🧪 Teste Module-Imports...")
    
    modules_to_test = [
        "xml.etree.ElementTree",
        "chardet",
        "psutil"
    ]
    
    optional_modules = [
        "lxml",
        "xmlschema"
    ]
    
    # Teste erforderliche Module
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} nicht verfügbar")
            return False
    
    # Teste optionale Module
    for module in optional_modules:
        try:
            __import__(module)
            print(f"  ✅ {module} (optional)")
        except ImportError:
            print(f"  ⚠️  {module} nicht verfügbar (optional)")
    
    return True


def test_arxml_merger():
    """Testet die ARXML-Merger-Module."""
    print("🔧 Teste ARXML-Merger-Module...")
    
    try:
        # Teste Haupt-Module
        from arxml_merger_engine import ARXMLMergerEngine
        from arxml_validator import ARXMLValidator
        from conflict_resolver import ConflictResolver
        from arxml_reporter import ReportGenerator
        from config import get_config_manager
        from utils import TempFileManager
        
        print("  ✅ Alle ARXML-Merger-Module verfügbar")
        return True
    
    except ImportError as e:
        print(f"  ❌ Fehler beim Import: {e}")
        return False


def create_desktop_shortcut():
    """Erstellt Desktop-Verknüpfung (nur Windows/Linux)."""
    print("🖥️  Erstelle Desktop-Verknüpfung...")
    
    system = platform.system()
    script_dir = Path(__file__).parent
    
    if system == "Windows":
        # Windows .bat Datei
        bat_content = f'''@echo off
cd /d "{script_dir}"
python run_web_server.py
pause
'''
        bat_file = Path.home() / "Desktop" / "ARXML_Merger.bat"
        try:
            with open(bat_file, 'w') as f:
                f.write(bat_content)
            print(f"  ✅ Windows-Verknüpfung erstellt: {bat_file}")
        except Exception as e:
            print(f"  ⚠️  Konnte Windows-Verknüpfung nicht erstellen: {e}")
    
    elif system == "Linux":
        # Linux .desktop Datei
        desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=ARXML Merger
Comment=Professional AUTOSAR ARXML Merger
Exec=python3 "{script_dir}/run_web_server.py"
Icon=applications-development
Terminal=true
Categories=Development;
'''
        desktop_file = Path.home() / "Desktop" / "ARXML_Merger.desktop"
        try:
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            os.chmod(desktop_file, 0o755)
            print(f"  ✅ Linux-Verknüpfung erstellt: {desktop_file}")
        except Exception as e:
            print(f"  ⚠️  Konnte Linux-Verknüpfung nicht erstellen: {e}")
    
    else:
        print(f"  ⚠️  Desktop-Verknüpfung für {system} nicht unterstützt")


def create_config_file():
    """Erstellt Standard-Konfigurationsdatei."""
    print("⚙️  Erstelle Standard-Konfiguration...")
    
    try:
        from config import get_config_manager
        
        config_manager = get_config_manager()
        config_manager.create_default_config_file()
        print("  ✅ Konfigurationsdatei erstellt")
        return True
    
    except Exception as e:
        print(f"  ❌ Fehler beim Erstellen der Konfiguration: {e}")
        return False


def show_usage_info():
    """Zeigt Nutzungsinformationen."""
    print("\n" + "=" * 60)
    print("🎉 Installation erfolgreich abgeschlossen!")
    print("=" * 60)
    print()
    print("📖 Verwendung:")
    print()
    print("1️⃣  Web-Interface starten:")
    print("   python run_web_server.py")
    print("   oder: python main.py web")
    print()
    print("2️⃣  Command-Line-Interface:")
    print("   python main.py merge output.arxml input1.arxml input2.arxml")
    print()
    print("3️⃣  Validierung:")
    print("   python main.py validate input.arxml")
    print()
    print("4️⃣  Tests ausführen:")
    print("   python test_merger.py")
    print()
    print("📚 Weitere Informationen:")
    print("   - README.md für detaillierte Dokumentation")
    print("   - examples/ für Beispiel-Konfigurationen")
    print("   - python main.py --help für alle Optionen")
    print()
    print("🌐 Web-Interface: http://localhost:8000")
    print()


def main():
    """Hauptfunktion der Installation."""
    print("🚀 ARXML-Merger Installation")
    print("=" * 40)
    print()
    
    # Prüfe Systemvoraussetzungen
    checks = [
        ("Python-Version", check_python_version),
        ("pip-Installation", check_pip)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ Installation abgebrochen: {check_name} fehlgeschlagen")
            return 1
        print()
    
    # Installiere Dependencies
    if not install_requirements():
        print("\n❌ Installation abgebrochen: Dependencies konnten nicht installiert werden")
        return 1
    print()
    
    # Teste Installation
    test_checks = [
        ("Module-Imports", test_imports),
        ("ARXML-Merger-Module", test_arxml_merger)
    ]
    
    for check_name, check_func in test_checks:
        if not check_func():
            print(f"\n❌ Installation unvollständig: {check_name} fehlgeschlagen")
            return 1
        print()
    
    # Erstelle Konfiguration
    create_config_file()
    print()
    
    # Erstelle Desktop-Verknüpfung
    create_desktop_shortcut()
    print()
    
    # Zeige Nutzungsinformationen
    show_usage_info()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
