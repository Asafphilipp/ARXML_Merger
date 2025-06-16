
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

## 🎯 Schritt-für-Schritt Anleitung für Einsteiger

### 📥 **Schritt 1: Installation (Einmalig)**

#### **Option A: Automatische Installation (Empfohlen)**
```bash
# 1. Repository herunterladen
git clone https://github.com/Asafphilipp/ARXML_Merger.git
cd ARXML_Merger

# 2. Automatische Installation starten
python install.py
```
Das Installations-Skript prüft automatisch alle Voraussetzungen und installiert alles Notwendige.

#### **Option B: Manuelle Installation**
```bash
# 1. Repository herunterladen
git clone https://github.com/Asafphilipp/ARXML_Merger.git
cd ARXML_Merger

# 2. Python-Pakete installieren
pip install -r requirements.txt

# 3. Konfiguration erstellen
python main.py config --create

# 4. Installation testen
python test_merger.py
```

### 🚀 **Schritt 2: Erste Verwendung**

#### **🌐 Web-Interface (Einfachste Methode)**
```bash
# 1. Web-Server starten
python run_web_server.py

# 2. Browser öffnen und zu folgender Adresse gehen:
#    http://localhost:8000

# 3. ARXML-Dateien per Drag & Drop hochladen
# 4. Einstellungen wählen (oder Standard beibehalten)
# 5. "Zusammenführen" klicken
# 6. Ergebnis herunterladen
```

#### **💻 Command-Line (Für Fortgeschrittene)**
```bash
# Einfachster Befehl - 2 Dateien zusammenführen:
python main.py merge meine_ausgabe.arxml datei1.arxml datei2.arxml

# Mit mehr Optionen:
python main.py merge --strategy latest_wins --reports \
    ausgabe.arxml eingabe1.arxml eingabe2.arxml eingabe3.arxml
```

### 📁 **Schritt 3: Ihre ARXML-Dateien vorbereiten**

1. **Sammeln Sie alle ARXML-Dateien**, die Sie zusammenführen möchten
2. **Legen Sie sie in einen Ordner** (z.B. `meine_arxml_dateien/`)
3. **Stellen Sie sicher**, dass die Dateien gültige ARXML-Dateien sind

### 🎮 **Schritt 4: Praktische Beispiele**

#### **Beispiel 1: Zwei Dateien zusammenführen (Web-Interface)**
```
1. python run_web_server.py
2. Browser öffnen: http://localhost:8000
3. Dateien hochladen: ECU1.arxml und ECU2.arxml
4. "Zusammenführen" klicken
5. merged.arxml herunterladen
```

#### **Beispiel 2: Mehrere Dateien mit Berichten (Command-Line)**
```bash
python main.py merge --reports --backup \
    projekt_merged.arxml \
    ecu1.arxml ecu2.arxml ecu3.arxml signals.arxml
```
**Was passiert:**
- Alle 4 Dateien werden zusammengeführt
- Backups der Originaldateien werden erstellt
- Detaillierte Berichte werden im `reports/` Ordner erstellt
- Ergebnis wird als `projekt_merged.arxml` gespeichert

#### **Beispiel 3: Nur Validierung (ohne Merge)**
```bash
python main.py validate meine_datei.arxml
```

### 🔧 **Schritt 5: Einstellungen anpassen (Optional)**

#### **Konfigurationsdatei bearbeiten:**
```bash
# Konfiguration erstellen (falls noch nicht vorhanden)
python main.py config --create

# Datei bearbeiten mit einem Text-Editor
notepad arxml_merger_config.json    # Windows
nano arxml_merger_config.json       # Linux/Mac
```

#### **Wichtige Einstellungen:**
- `"strategy": "conservative"` - Wie Konflikte gelöst werden
- `"generate_reports": true` - Ob Berichte erstellt werden sollen
- `"backup_originals": true` - Ob Backups erstellt werden sollen

### 📊 **Schritt 6: Ergebnisse verstehen**

#### **Nach dem Merge erhalten Sie:**
1. **Merged ARXML-Datei** - Das Hauptergebnis
2. **HTML-Bericht** - Übersicht über den Merge-Vorgang
3. **Signal-Inventar (CSV)** - Liste aller Signale
4. **Konflikt-Bericht** - Details zu aufgelösten Konflikten

#### **Typische Ausgabe:**
```
✅ Merge erfolgreich abgeschlossen: projekt_merged.arxml
⚡ Verarbeitungszeit: 2.34s
📡 Erhaltene Signale: 1,247
🔧 Aufgelöste Konflikte: 23
📊 Berichte generiert in: reports/
```

### 🆘 **Schritt 7: Hilfe bei Problemen**

#### **Häufige Probleme und Lösungen:**

**Problem: "Datei nicht gefunden"**
```bash
# Lösung: Vollständigen Pfad angeben
python main.py merge ausgabe.arxml C:\Pfad\zu\datei1.arxml C:\Pfad\zu\datei2.arxml
```

**Problem: "Permission denied"**
```bash
# Lösung: Anderen Port verwenden
python run_web_server.py --port 8080
```

**Problem: "Memory Error"**
```bash
# Lösung: Niedrigere Validierungsstufe verwenden
python main.py merge --validation basic ausgabe.arxml eingabe*.arxml
```

#### **Hilfe anzeigen:**
```bash
python main.py --help              # Allgemeine Hilfe
python main.py merge --help        # Hilfe für Merge-Kommando
python main.py validate --help     # Hilfe für Validierung
```

### 🎯 **Schritt 8: Erweiterte Nutzung**

#### **Für regelmäßige Nutzung:**
```bash
# Batch-Datei erstellen (Windows)
echo python main.py merge --reports ausgabe.arxml eingabe*.arxml > merge_script.bat

# Shell-Skript erstellen (Linux/Mac)
echo "python main.py merge --reports ausgabe.arxml eingabe*.arxml" > merge_script.sh
chmod +x merge_script.sh
```

#### **Automatisierung:**
```bash
# Alle ARXML-Dateien in einem Ordner mergen
python main.py merge --reports projekt_komplett.arxml ordner/*.arxml
```

### ✅ **Erfolgskontrolle**

**Sie wissen, dass alles funktioniert, wenn:**
1. ✅ Das Web-Interface unter http://localhost:8000 erreichbar ist
2. ✅ Der Test-Befehl `python test_merger.py` erfolgreich läuft
3. ✅ Sie eine merged ARXML-Datei erhalten haben
4. ✅ Die Berichte im `reports/` Ordner erstellt wurden

---

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

