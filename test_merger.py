#!/usr/bin/env python3
"""
Test-Skript für ARXML-Merger.

Dieses Skript testet die grundlegenden Funktionen des ARXML-Mergers
mit Beispieldateien und verschiedenen Konfigurationen.
"""

import sys
import tempfile
import os
from pathlib import Path
import xml.etree.ElementTree as ET

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

try:
    from arxml_merger_engine import ARXMLMergerEngine, MergeStrategy
    from arxml_validator import ARXMLValidator, ValidationLevel
    from utils import TempFileManager, setup_logging
except ImportError as e:
    print(f"❌ Fehler beim Importieren der Module: {e}")
    print("💡 Stellen Sie sicher, dass alle Module verfügbar sind")
    sys.exit(1)


def create_sample_arxml(filename: str, content_variant: str = "A") -> str:
    """Erstellt eine Beispiel-ARXML-Datei für Tests."""
    
    # Basis-AUTOSAR-Struktur
    autosar_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-3-0.xsd">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>TestPackage{content_variant}</SHORT-NAME>
      <AR-PACKAGES>
        <AR-PACKAGE>
          <SHORT-NAME>Signals</SHORT-NAME>
          <ELEMENTS>
            <I-SIGNAL>
              <SHORT-NAME>TestSignal{content_variant}_1</SHORT-NAME>
              <LENGTH>8</LENGTH>
              <DATA-TYPE-POLICY>LEGACY</DATA-TYPE-POLICY>
            </I-SIGNAL>
            <I-SIGNAL>
              <SHORT-NAME>TestSignal{content_variant}_2</SHORT-NAME>
              <LENGTH>16</LENGTH>
              <DATA-TYPE-POLICY>LEGACY</DATA-TYPE-POLICY>
            </I-SIGNAL>
          </ELEMENTS>
        </AR-PACKAGE>
        <AR-PACKAGE>
          <SHORT-NAME>Interfaces</SHORT-NAME>
          <ELEMENTS>
            <SENDER-RECEIVER-INTERFACE>
              <SHORT-NAME>TestInterface{content_variant}</SHORT-NAME>
              <IS-SERVICE>false</IS-SERVICE>
              <DATA-ELEMENTS>
                <VARIABLE-DATA-ELEMENT>
                  <SHORT-NAME>DataElement{content_variant}</SHORT-NAME>
                  <TYPE-TREF DEST="PRIMITIVE-TYPE">/TestPackage{content_variant}/DataTypes/uint8</TYPE-TREF>
                </VARIABLE-DATA-ELEMENT>
              </DATA-ELEMENTS>
            </SENDER-RECEIVER-INTERFACE>
          </ELEMENTS>
        </AR-PACKAGE>
        <AR-PACKAGE>
          <SHORT-NAME>DataTypes</SHORT-NAME>
          <ELEMENTS>
            <PRIMITIVE-TYPE>
              <SHORT-NAME>uint8</SHORT-NAME>
              <SW-DATA-DEF-PROPS>
                <SW-DATA-DEF-PROPS-VARIANTS>
                  <SW-DATA-DEF-PROPS-CONDITIONAL>
                    <BASE-TYPE-ENCODING>NONE</BASE-TYPE-ENCODING>
                    <SW-IMPL-POLICY>STANDARD</SW-IMPL-POLICY>
                  </SW-DATA-DEF-PROPS-CONDITIONAL>
                </SW-DATA-DEF-PROPS-VARIANTS>
              </SW-DATA-DEF-PROPS>
            </PRIMITIVE-TYPE>
          </ELEMENTS>
        </AR-PACKAGE>
      </AR-PACKAGES>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(autosar_content)
    
    return filename


def test_basic_merge():
    """Testet grundlegende Merge-Funktionalität."""
    print("🧪 Test: Grundlegende Merge-Funktionalität")
    
    with TempFileManager() as temp_manager:
        # Erstelle Test-Dateien
        file1 = temp_manager.create_temp_file(suffix='.arxml')
        file2 = temp_manager.create_temp_file(suffix='.arxml')
        output_file = temp_manager.create_temp_file(suffix='.arxml')
        
        create_sample_arxml(file1, "A")
        create_sample_arxml(file2, "B")
        
        # Führe Merge durch
        merger = ARXMLMergerEngine(MergeStrategy.CONSERVATIVE)
        result = merger.merge_files([file1, file2], output_file)
        
        if result.success:
            print("  ✅ Merge erfolgreich")
            print(f"  📊 Verarbeitungszeit: {result.processing_time:.3f}s")
            print(f"  📡 Erhaltene Signale: {len(result.preserved_signals)}")
            print(f"  🔧 Konflikte: {len(result.conflicts)}")
            
            # Validiere Ausgabe
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print("  ✅ Ausgabedatei erstellt")
                return True
            else:
                print("  ❌ Ausgabedatei leer oder nicht erstellt")
                return False
        else:
            print("  ❌ Merge fehlgeschlagen")
            for error in result.errors:
                print(f"    - {error}")
            return False


def test_validation():
    """Testet Validierungsfunktionalität."""
    print("\n🧪 Test: Validierungsfunktionalität")
    
    with TempFileManager() as temp_manager:
        # Erstelle Test-Datei
        test_file = temp_manager.create_temp_file(suffix='.arxml')
        create_sample_arxml(test_file, "Test")
        
        # Validiere Datei
        validator = ARXMLValidator(ValidationLevel.STRUCTURE)
        result = validator.validate_file(test_file)
        
        print(f"  📄 Datei: {os.path.basename(test_file)}")
        print(f"  📏 Größe: {result.file_size} Bytes")
        print(f"  🔤 Encoding: {result.encoding}")
        print(f"  📊 Elemente: {result.element_count}")
        
        if result.is_valid:
            print("  ✅ Validierung erfolgreich")
            return True
        else:
            print("  ❌ Validierung fehlgeschlagen")
            for issue in result.issues:
                print(f"    - {issue.severity.value}: {issue.message}")
            return False


def test_different_strategies():
    """Testet verschiedene Merge-Strategien."""
    print("\n🧪 Test: Verschiedene Merge-Strategien")
    
    strategies = [
        MergeStrategy.CONSERVATIVE,
        MergeStrategy.LATEST_WINS
    ]
    
    results = {}
    
    with TempFileManager() as temp_manager:
        # Erstelle Test-Dateien mit Konflikten
        file1 = temp_manager.create_temp_file(suffix='.arxml')
        file2 = temp_manager.create_temp_file(suffix='.arxml')
        
        create_sample_arxml(file1, "Conflict1")
        create_sample_arxml(file2, "Conflict2")
        
        for strategy in strategies:
            print(f"  🔧 Teste Strategie: {strategy.value}")
            
            output_file = temp_manager.create_temp_file(suffix='.arxml')
            merger = ARXMLMergerEngine(strategy)
            result = merger.merge_files([file1, file2], output_file)
            
            results[strategy.value] = result.success
            
            if result.success:
                print(f"    ✅ Erfolgreich ({result.processing_time:.3f}s)")
            else:
                print(f"    ❌ Fehlgeschlagen")
    
    # Zusammenfassung
    successful = sum(1 for success in results.values() if success)
    print(f"  📊 Erfolgreiche Strategien: {successful}/{len(strategies)}")
    
    return successful == len(strategies)


def test_large_file_simulation():
    """Simuliert Test mit größeren Dateien."""
    print("\n🧪 Test: Simulation größerer Dateien")
    
    with TempFileManager() as temp_manager:
        # Erstelle größere Test-Datei durch Wiederholung
        large_file = temp_manager.create_temp_file(suffix='.arxml')
        
        # Basis-Inhalt
        base_content = create_sample_arxml(temp_manager.create_temp_file(suffix='.arxml'), "Large")
        
        # Lese Basis-Inhalt
        with open(base_content, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Erweitere Inhalt (simuliere größere Datei)
        extended_content = content.replace(
            '<SHORT-NAME>TestSignal',
            '<SHORT-NAME>TestSignal'
        )
        
        # Füge zusätzliche Signale hinzu
        additional_signals = ""
        for i in range(10):
            additional_signals += f'''
            <I-SIGNAL>
              <SHORT-NAME>AdditionalSignal_{i}</SHORT-NAME>
              <LENGTH>32</LENGTH>
              <DATA-TYPE-POLICY>LEGACY</DATA-TYPE-POLICY>
            </I-SIGNAL>'''
        
        extended_content = extended_content.replace(
            '</ELEMENTS>',
            additional_signals + '\n          </ELEMENTS>',
            1
        )
        
        with open(large_file, 'w', encoding='utf-8') as f:
            f.write(extended_content)
        
        file_size = os.path.getsize(large_file)
        print(f"  📏 Simulierte Dateigröße: {file_size} Bytes")
        
        # Teste Merge
        output_file = temp_manager.create_temp_file(suffix='.arxml')
        merger = ARXMLMergerEngine(MergeStrategy.CONSERVATIVE)
        result = merger.merge_files([large_file], output_file)
        
        if result.success:
            print(f"  ✅ Verarbeitung erfolgreich ({result.processing_time:.3f}s)")
            return True
        else:
            print("  ❌ Verarbeitung fehlgeschlagen")
            return False


def run_all_tests():
    """Führt alle Tests aus."""
    print("🚀 ARXML-Merger Test Suite")
    print("=" * 50)
    
    # Setup Logging
    setup_logging()
    
    tests = [
        ("Grundlegende Merge-Funktionalität", test_basic_merge),
        ("Validierungsfunktionalität", test_validation),
        ("Verschiedene Merge-Strategien", test_different_strategies),
        ("Simulation größerer Dateien", test_large_file_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ❌ Unerwarteter Fehler: {e}")
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 50)
    print("📊 Test-Zusammenfassung:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ BESTANDEN" if success else "❌ FEHLGESCHLAGEN"
        print(f"  {status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\n🏆 Ergebnis: {passed}/{len(tests)} Tests bestanden")
    
    if passed == len(tests):
        print("🎉 Alle Tests erfolgreich!")
        return 0
    else:
        print("⚠️  Einige Tests fehlgeschlagen")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
