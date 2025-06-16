# ARXML Merger

Dieses Repository enthält ein einfaches Python-Skript, das mehrere AUTOSAR-ARXML-Dateien zu einer gemeinsamen Ausgabedatei zusammenführt.

## Voraussetzungen
* Python 3.10 oder neuer (bereits in dieser Umgebung vorhanden)

## Verwendung
```bash
python3 arxml_merger.py [--encoding UTF-8] [--strategy latest-wins] \
    [--rules rules.json] output.arxml input1.arxml input2.arxml [...]
```
Das Skript liest alle angegebenen Eingabedateien, überspringt ungültige
Dateien und schreibt das Ergebnis nach `output.arxml`.

## Aktueller Funktionsumfang
* Rekursives Zusammenführen der `AR-PACKAGES`-Hierarchie
* Warnungen bei ungültig formatierten Eingabedateien oder falschen Root-Elementen
* Wählbare Konfliktstrategie (`conservative`, `latest-wins`, `interactive`, `rule-based`)
* Optionale Angabe des Eingabe-Encodings
* Regelbasierte Konfliktauflösung mittels JSON-Datei

## Geplante Erweiterungen (Auszug)
* Vollständige Signal-Preservation und Referenz-Integrität
* Unterstützung verschiedener Merge-Strategien (Conservative, Latest-Wins,
  Interactive, Rule-Based)
* Schema-Validierung der Ausgabe gegen die jeweilige AUTOSAR-Version
* Detaillierte Berichte über Konflikte und gemergte Signale

Diese Stichpunkte orientieren sich an der umfangreichen
Anforderungsliste im Prompt und dienen als Ausgangspunkt für eine
weiterführende Implementierung.

## Lokale Web-Oberfläche
Ein einfacher HTTP-Server ermöglicht das Mergen direkt im Browser:
```bash
python3 web_ui.py --port 8000
```
Danach kann die Seite `http://localhost:8000` aufgerufen werden, um ARXML-Dateien
hochzuladen und zusammenzuführen.
