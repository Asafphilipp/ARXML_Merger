#!/usr/bin/env python3
"""
Einfacher Starter für das ARXML-Merger Web-Interface.

Dieses Skript startet das Web-Interface mit optimierten Einstellungen
und bietet eine einfache Möglichkeit, den Server zu starten.
"""

import sys
import os
import logging
from pathlib import Path

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

try:
    from web_interface import ARXMLWebServer
    from config import get_config_manager
    from utils import setup_logging
except ImportError as e:
    print(f"❌ Fehler beim Importieren der Module: {e}")
    print("💡 Stellen Sie sicher, dass alle Dependencies installiert sind:")
    print("   pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Startet das Web-Interface mit optimierten Einstellungen."""
    
    # Setup Logging
    setup_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Lade Konfiguration
        config_manager = get_config_manager()
        web_config = config_manager.get_web_config()
        
        # Erstelle Server
        server = ARXMLWebServer(
            port=web_config.port,
            host=web_config.host
        )
        
        # Zeige Startup-Information
        print("🚀 ARXML-Merger wird gestartet...")
        print(f"📁 Arbeitsverzeichnis: {Path.cwd()}")
        print(f"🐍 Python-Version: {sys.version}")
        print(f"⚙️  Konfiguration geladen")
        print()
        
        # Starte Server
        server.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Server durch Benutzer beendet")
        return 0
    except Exception as e:
        logger.error(f"❌ Fehler beim Starten des Servers: {e}")
        print(f"\n❌ Fehler: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Prüfen Sie, ob der Port bereits verwendet wird")
        print("   2. Stellen Sie sicher, dass alle Dependencies installiert sind")
        print("   3. Prüfen Sie die Berechtigungen")
        return 1


if __name__ == '__main__':
    sys.exit(main())
