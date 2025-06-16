# 🚀 ARXML Merger - Professional AUTOSAR Tool

Ein robuster, professioneller ARXML-Merger für AUTOSAR-Dateien mit vollständiger Signal-Preservation, intelligenter Konfliktauflösung und modernem Web-Interface.

## ✨ Hauptfunktionen

### 🔧 Kernfunktionalitäten
- **Vollständige Signal-Preservation**: Garantiert, dass ALLE Signale aus allen Quelldateien erhalten bleiben
- **Intelligente Konfliktauflösung**: Erweiterte Strategien für verschiedene Konflikttypen
- **Referenz-Integrität**: Automatische Auflösung und Erhaltung aller internen/externen Referenzen
- **Multi-Format-Support**: Unterstützt verschiedene AUTOSAR-Versionen (4.0.x - 4.5.x)
- **Schema-Validierung**: Vollständige Validierung gegen AUTOSAR-Schemas

### 📊 Erweiterte Features
- **Performance-Optimierung**: Effiziente Verarbeitung großer Dateien (>100MB)
- **Detaillierte Berichte**: HTML, JSON und CSV-Berichte mit Signal-Inventar
- **Moderne Web-UI**: Drag & Drop Interface mit Live-Feedback
- **Konfigurierbare Strategien**: Conservative, Latest-Wins, Interactive, Rule-Based
- **Backup-System**: Automatische Sicherung der Originaldateien

## 🚀 Schnellstart

### Installation
```bash
# Repository klonen
git clone https://github.com/Asafphilipp/ARXML_Merger.git
cd ARXML_Merger

# Dependencies installieren
pip install -r requirements.txt
```

### Command-Line-Interface
```bash
# Einfacher Merge
python main.py merge output.arxml input1.arxml input2.arxml

# Mit erweiterten Optionen
python main.py merge --strategy latest_wins --validation schema --reports \
    output.arxml input1.arxml input2.arxml input3.arxml

# Nur Validierung
python main.py validate --level schema input1.arxml input2.arxml
```

### Web-Interface
```bash
# Web-Server starten
python main.py web --port 8000

# Oder direkt
python web_interface.py --port 8000
```
Dann öffnen Sie `http://localhost:8000` in Ihrem Browser.

## 📖 Detaillierte Verwendung

### Command-Line-Optionen

#### Merge-Kommando
```bash
python main.py merge [OPTIONS] OUTPUT INPUT1 INPUT2 [INPUT3...]

Optionen:
  --strategy {conservative,latest_wins,interactive,rule_based}
                        Merge-Strategie (Standard: conservative)
  --validation {basic,structure,schema,semantic}
                        Validierungsstufe (Standard: structure)
  --rules RULES         Pfad zur JSON-Datei mit Konfliktauflösungsregeln
  --reports             Generiert detaillierte Berichte
  --backup              Erstellt Backups der Eingabedateien
  --output-dir DIR      Verzeichnis für Ausgabedateien und Berichte
```

#### Validierungs-Kommando
```bash
python main.py validate [OPTIONS] INPUT1 [INPUT2...]

Optionen:
  --level {basic,structure,schema,semantic}
                        Validierungsstufe (Standard: structure)
  --report REPORT       Pfad für Validierungsbericht
```

#### Web-Interface-Kommando
```bash
python main.py web [OPTIONS]

Optionen:
  --host HOST           Host-Adresse (Standard: localhost)
  --port PORT           Port-Nummer (Standard: 8000)
  --debug               Debug-Modus aktivieren
```

### Merge-Strategien

#### 1. Conservative (Standard)
- Erste Datei hat Priorität bei Konflikten
- Sicherste Option für kritische Systeme
- Bewahrt ursprüngliche Struktur

#### 2. Latest-Wins
- Letzte Datei überschreibt bei Konflikten
- Gut für Updates und Patches
- Automatische Konfliktauflösung

#### 3. Interactive
- Benutzer entscheidet bei jedem Konflikt
- Maximale Kontrolle
- Ideal für komplexe Merge-Szenarien

#### 4. Rule-Based
- Verwendet vordefinierte Regeln
- Konfigurierbar über JSON-Dateien
- Automatisierbar für wiederkehrende Aufgaben

### Validierungsstufen

#### Basic
- XML-Wohlgeformtheit
- Grundlegende Struktur-Checks

#### Structure (Standard)
- AUTOSAR-Struktur-Validierung
- Package-Hierarchie-Prüfung
- Short-Name-Eindeutigkeit

#### Schema
- Vollständige XSD-Schema-Validierung
- AUTOSAR-Versions-Compliance
- Datentyp-Validierung

#### Semantic
- Semantische Konsistenz-Checks
- Referenz-Integrität
- Signal-Mapping-Validierung

## 🔧 Konfiguration

### Konfigurationsdatei erstellen
```bash
python main.py config --create
```

### Beispiel-Konfiguration (arxml_merger_config.json)
```json
{
  "merge": {
    "strategy": "conservative",
    "validation_level": "structure",
    "generate_reports": true,
    "pretty_print": true,
    "backup_originals": true
  },
  "validation": {
    "check_schema": true,
    "check_references": true,
    "autosar_versions": ["4.2.1", "4.3.0", "4.4.0"]
  },
  "reporting": {
    "generate_html": true,
    "generate_json": true,
    "generate_csv": true,
    "include_signal_inventory": true
  },
  "web": {
    "host": "localhost",
    "port": 8000,
    "max_upload_size_mb": 50
  }
}
```

## 📊 Berichte und Ausgaben

### Generierte Berichte
- **HTML-Bericht**: Interaktive Übersicht mit Metriken
- **JSON-Bericht**: Maschinenlesbare Daten für Automation
- **Signal-Inventar (CSV)**: Vollständige Liste aller Signale
- **Konflikt-Bericht (CSV)**: Detaillierte Konfliktauflösung

### Beispiel-Ausgabe
```
🚀 ARXML Merger Web-Interface gestartet!
📡 Server läuft auf: http://localhost:8000
🌐 Öffnen Sie die URL in Ihrem Browser
⏹️  Drücken Sie Ctrl+C zum Beenden

✅ Merge erfolgreich abgeschlossen: merged_output.arxml
⚡ Verarbeitungszeit: 2.34s
📡 Erhaltene Signale: 1,247
🔧 Aufgelöste Konflikte: 23
📊 Berichte generiert in: reports/
```

## 🌐 Web-Interface Features

### Moderne Benutzeroberfläche
- **Drag & Drop**: Einfaches Hochladen von ARXML-Dateien
- **Live-Feedback**: Echtzeit-Fortschrittsanzeige
- **Responsive Design**: Funktioniert auf Desktop und Mobile
- **Konfigurierbare Optionen**: Alle Merge-Parameter einstellbar

### Unterstützte Browser
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🔍 Erweiterte Funktionen

### Konfliktauflösungsregeln (JSON)
```json
{
  "rules": [
    {
      "element_type": "I-SIGNAL",
      "conflict_type": "duplicate_element",
      "resolution_strategy": "keep_first",
      "priority": 10
    },
    {
      "element_type": "SENDER-RECEIVER-INTERFACE",
      "conflict_type": "different_attributes",
      "resolution_strategy": "merge_attributes",
      "priority": 8
    }
  ]
}
```

### Performance-Optimierung
- **Streaming-Parser**: Effiziente Verarbeitung großer Dateien
- **Memory-Management**: Optimiert für begrenzte Ressourcen
- **Parallel-Processing**: Nutzt mehrere CPU-Kerne
- **Caching**: Intelligente Zwischenspeicherung

### Signal-Preservation-Garantie
```
✅ Alle I-Signale werden erhalten
✅ Signal-Gruppen bleiben intakt
✅ Interface-Definitionen vollständig
✅ Datentyp-Referenzen aufgelöst
✅ Port-Prototypen korrekt zugeordnet
```

## 🧪 Testing und Qualitätssicherung

### Automatische Tests
```bash
# Unit-Tests ausführen (falls pytest installiert)
pytest tests/

# Validierung mit Beispieldateien
python main.py validate examples/*.arxml

# Performance-Test
python main.py merge --reports large_output.arxml large_input*.arxml
```

### Qualitätskriterien
- ✅ 100% Signal-Preservation
- ✅ Schema-Compliance der Ausgabe
- ✅ Performance: <10s für typische Projekte (<50MB)
- ✅ Memory-Effizienz: <2x der größten Eingabedatei

## 🔧 Entwicklung und Erweiterung

### Architektur-Übersicht
```
arxml_merger_engine.py    # Kern-Merge-Engine
arxml_validator.py        # Validierung und Schema-Checks
conflict_resolver.py      # Intelligente Konfliktauflösung
arxml_reporter.py         # Berichtserstellung
web_interface.py          # Moderne Web-UI
config.py                 # Konfigurationsmanagement
utils.py                  # Utility-Funktionen
main.py                   # CLI-Interface
```

### Eigene Merge-Strategien hinzufügen
```python
from conflict_resolver import ConflictResolver, ResolutionStrategy

def custom_strategy(context):
    # Ihre benutzerdefinierte Logik
    return resolution

resolver = ConflictResolver()
resolver.rule_engine.register_custom_handler("my_strategy", custom_strategy)
```

## 📋 Systemanforderungen

### Minimum
- Python 3.8+
- 512 MB RAM
- 100 MB freier Speicherplatz

### Empfohlen
- Python 3.10+
- 2 GB RAM
- 1 GB freier Speicherplatz
- Multi-Core-CPU für bessere Performance

### Dependencies
```
lxml>=4.9.0              # XML-Verarbeitung
xmlschema>=2.0.0         # Schema-Validierung
chardet>=5.0.0           # Encoding-Erkennung
psutil>=5.9.0            # System-Monitoring
```

## 🐛 Troubleshooting

### Häufige Probleme

#### "Memory Error" bei großen Dateien
```bash
# Reduzieren Sie die Chunk-Größe
python main.py merge --config config_low_memory.json output.arxml input*.arxml
```

#### "Schema Validation Failed"
```bash
# Verwenden Sie niedrigere Validierungsstufe
python main.py merge --validation basic output.arxml input*.arxml
```

#### "Permission Denied" beim Web-Interface
```bash
# Verwenden Sie einen anderen Port
python main.py web --port 8080
```

### Debug-Modus
```bash
# Detaillierte Logs aktivieren
python main.py merge -vv --log-file debug.log output.arxml input*.arxml
```

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe LICENSE-Datei für Details.

## 🤝 Beitragen

Beiträge sind willkommen! Bitte lesen Sie CONTRIBUTING.md für Details zum Entwicklungsprozess.

### Entwicklung
```bash
# Development-Setup
git clone https://github.com/Asafphilipp/ARXML_Merger.git
cd ARXML_Merger
pip install -r requirements.txt

# Tests ausführen
python -m pytest tests/

# Code-Qualität prüfen
flake8 *.py
black *.py
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Asafphilipp/ARXML_Merger/issues)
- **Dokumentation**: Siehe `docs/` Verzeichnis
- **Beispiele**: Siehe `examples/` Verzeichnis

## 🏆 Erfolgs-Metriken

- ✅ **Null Signal-Verlust**: Jedes Signal wird erhalten
- ✅ **100% Schema-Validität**: AUTOSAR-konforme Ausgabe
- ✅ **Referenz-Integrität**: Alle Referenzen bleiben auflösbar
- ✅ **Linear Performance**: Skaliert mit Dateigröße
- ✅ **Benutzerfreundlich**: Klare Berichte und Fehlermeldungen

---

**Entwickelt für professionelle AUTOSAR-Entwicklung** 🚗⚡
