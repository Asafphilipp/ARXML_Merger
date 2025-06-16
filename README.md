# ARXML Merger

Dieses Repository enthält ein einfaches Python-Skript, das mehrere AUTOSAR
ARXML-Dateien zu einer gemeinsamen Ausgabedatei zusammenführt.

## Voraussetzungen
* Python 3.10 oder neuer (bereits in dieser Umgebung vorhanden)

## Verwendung
```bash
python3 arxml_merger.py output.arxml input1.arxml input2.arxml [...]
```
Das Skript liest alle angegebenen Eingabedateien, überspringt ungültige
Dateien und schreibt das Ergebnis nach `output.arxml`.

## Aktueller Funktionsumfang
* Einfache Zusammenführung der Root-Elemente aus mehreren Dateien
* Warnungen bei ungültig formatierten Eingabedateien

## Geplante Erweiterungen (Auszug)
* Vollständige Signal-Preservation und Referenz-Integrität
* Unterstützung verschiedener Merge-Strategien (Conservative, Latest-Wins,
  Interactive, Rule-Based)
* Schema-Validierung der Ausgabe gegen die jeweilige AUTOSAR-Version
* Detaillierte Berichte über Konflikte und gemergte Signale

Diese Stichpunkte orientieren sich an der umfangreichen
Anforderungsliste im Prompt und dienen als Ausgangspunkt für eine
weiterführende Implementierung.
