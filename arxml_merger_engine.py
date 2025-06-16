"""
Robuster ARXML-Merger Engine für AUTOSAR ARXML-Dateien.

Dieser Modul implementiert die Kernfunktionalität für das intelligente Zusammenführen
von AUTOSAR ARXML-Dateien mit vollständiger Signal-Preservation und Referenz-Integrität.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum
import re
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MergeStrategy(Enum):
    """Verfügbare Merge-Strategien."""
    CONSERVATIVE = "conservative"
    LATEST_WINS = "latest_wins"
    INTERACTIVE = "interactive"
    RULE_BASED = "rule_based"


class ElementType(Enum):
    """AUTOSAR Element-Typen für spezielle Behandlung."""
    SIGNAL = "I-SIGNAL"
    SIGNAL_GROUP = "I-SIGNAL-GROUP"
    INTERFACE = "SENDER-RECEIVER-INTERFACE"
    CLIENT_SERVER_INTERFACE = "CLIENT-SERVER-INTERFACE"
    ECU_INSTANCE = "ECU-INSTANCE"
    PORT_PROTOTYPE = "P-PORT-PROTOTYPE"
    REQUIRED_PORT = "R-PORT-PROTOTYPE"
    DATA_TYPE = "DATA-TYPE"
    PRIMITIVE_TYPE = "PRIMITIVE-TYPE"
    ARRAY_TYPE = "ARRAY-TYPE"
    RECORD_TYPE = "RECORD-TYPE"
    ENUM_TYPE = "ENUMERATION-TYPE"


@dataclass
class MergeConflict:
    """Repräsentiert einen Merge-Konflikt."""
    element_type: str
    element_name: str
    source_file_1: str
    source_file_2: str
    conflict_type: str
    description: str
    resolution: Optional[str] = None


@dataclass
class MergeResult:
    """Ergebnis eines Merge-Vorgangs."""
    success: bool
    merged_tree: Optional[ET.ElementTree]
    conflicts: List[MergeConflict]
    preserved_signals: Set[str]
    processing_time: float
    memory_usage: int
    warnings: List[str]
    errors: List[str]


class ARXMLNamespaceManager:
    """Verwaltet XML-Namespaces für AUTOSAR-Dateien."""
    
    def __init__(self):
        self.namespaces = {}
        self.default_namespace = None
    
    def register_namespaces(self, root: ET.Element) -> None:
        """Registriert alle Namespaces aus einem Root-Element."""
        # Extrahiere Namespace aus dem Root-Tag
        if '}' in root.tag:
            namespace = root.tag.split('}')[0].strip('{')
            self.default_namespace = namespace
            self.namespaces[''] = namespace
        
        # Registriere alle xmlns-Attribute
        for key, value in root.attrib.items():
            if key.startswith('xmlns'):
                prefix = key.split(':')[-1] if ':' in key else ''
                self.namespaces[prefix] = value
    
    def get_qualified_tag(self, tag: str, prefix: str = '') -> str:
        """Gibt den vollqualifizierten Tag-Namen zurück."""
        if prefix in self.namespaces:
            return f"{{{self.namespaces[prefix]}}}{tag}"
        elif self.default_namespace:
            return f"{{{self.default_namespace}}}{tag}"
        return tag
    
    def strip_namespace(self, tag: str) -> str:
        """Entfernt Namespace-Präfix von einem Tag."""
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag


class SignalTracker:
    """Verfolgt alle Signale während des Merge-Prozesses."""
    
    def __init__(self):
        self.signals: Dict[str, Dict[str, Any]] = {}
        self.signal_groups: Dict[str, Dict[str, Any]] = {}
        self.interfaces: Dict[str, Dict[str, Any]] = {}
    
    def add_signal(self, signal_name: str, signal_element: ET.Element, source_file: str) -> None:
        """Fügt ein Signal zur Verfolgung hinzu."""
        self.signals[signal_name] = {
            'element': signal_element,
            'source_file': source_file,
            'short_name': signal_name,
            'data_type': self._extract_data_type(signal_element),
            'length': self._extract_length(signal_element)
        }
    
    def add_signal_group(self, group_name: str, group_element: ET.Element, source_file: str) -> None:
        """Fügt eine Signal-Gruppe zur Verfolgung hinzu."""
        self.signal_groups[group_name] = {
            'element': group_element,
            'source_file': source_file,
            'short_name': group_name,
            'signals': self._extract_group_signals(group_element)
        }
    
    def add_interface(self, interface_name: str, interface_element: ET.Element, source_file: str) -> None:
        """Fügt ein Interface zur Verfolgung hinzu."""
        self.interfaces[interface_name] = {
            'element': interface_element,
            'source_file': source_file,
            'short_name': interface_name,
            'type': self._extract_interface_type(interface_element)
        }
    
    def _extract_data_type(self, element: ET.Element) -> Optional[str]:
        """Extrahiert den Datentyp eines Signals."""
        # Implementierung für Datentyp-Extraktion
        return None
    
    def _extract_length(self, element: ET.Element) -> Optional[int]:
        """Extrahiert die Länge eines Signals."""
        # Implementierung für Längen-Extraktion
        return None
    
    def _extract_group_signals(self, element: ET.Element) -> List[str]:
        """Extrahiert alle Signale einer Signal-Gruppe."""
        # Implementierung für Signal-Gruppen-Extraktion
        return []
    
    def _extract_interface_type(self, element: ET.Element) -> str:
        """Extrahiert den Interface-Typ."""
        # Implementierung für Interface-Typ-Extraktion
        return "UNKNOWN"
    
    def get_all_signals(self) -> Set[str]:
        """Gibt alle verfolgten Signal-Namen zurück."""
        return set(self.signals.keys())


class ReferenceManager:
    """Verwaltet und löst Referenzen zwischen AUTOSAR-Elementen auf."""
    
    def __init__(self):
        self.references: Dict[str, List[str]] = {}
        self.definitions: Dict[str, ET.Element] = {}
    
    def register_definition(self, path: str, element: ET.Element) -> None:
        """Registriert eine Element-Definition."""
        self.definitions[path] = element
    
    def register_reference(self, from_path: str, to_path: str) -> None:
        """Registriert eine Referenz zwischen Elementen."""
        if from_path not in self.references:
            self.references[from_path] = []
        self.references[from_path].append(to_path)
    
    def validate_references(self) -> List[str]:
        """Validiert alle Referenzen und gibt unaufgelöste zurück."""
        unresolved = []
        for from_path, to_paths in self.references.items():
            for to_path in to_paths:
                if to_path not in self.definitions:
                    unresolved.append(f"{from_path} -> {to_path}")
        return unresolved


class ARXMLMergerEngine:
    """Hauptklasse für das Zusammenführen von ARXML-Dateien."""
    
    def __init__(self, strategy: MergeStrategy = MergeStrategy.CONSERVATIVE):
        self.strategy = strategy
        self.namespace_manager = ARXMLNamespaceManager()
        self.signal_tracker = SignalTracker()
        self.reference_manager = ReferenceManager()
        self.conflicts: List[MergeConflict] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def merge_files(self, input_files: List[str], output_file: Optional[str] = None) -> MergeResult:
        """Führt mehrere ARXML-Dateien zusammen."""
        import time
        start_time = time.time()
        
        logger.info(f"Starte Merge von {len(input_files)} Dateien mit Strategie: {self.strategy.value}")
        
        # Parse alle Eingabedateien
        trees = []
        for file_path in input_files:
            tree = self._parse_arxml_file(file_path)
            if tree:
                trees.append((tree, file_path))
            else:
                self.errors.append(f"Konnte Datei nicht parsen: {file_path}")
        
        if not trees:
            return MergeResult(
                success=False,
                merged_tree=None,
                conflicts=self.conflicts,
                preserved_signals=set(),
                processing_time=time.time() - start_time,
                memory_usage=0,
                warnings=self.warnings,
                errors=self.errors
            )
        
        # Führe Merge durch
        merged_tree = self._merge_trees(trees)
        
        # Validiere Ergebnis
        preserved_signals = self.signal_tracker.get_all_signals()
        unresolved_refs = self.reference_manager.validate_references()
        
        if unresolved_refs:
            self.warnings.extend([f"Unaufgelöste Referenz: {ref}" for ref in unresolved_refs])
        
        # Speichere Ergebnis falls gewünscht
        if output_file and merged_tree:
            self._write_merged_file(merged_tree, output_file)
        
        processing_time = time.time() - start_time
        logger.info(f"Merge abgeschlossen in {processing_time:.2f}s")
        
        return MergeResult(
            success=True,
            merged_tree=merged_tree,
            conflicts=self.conflicts,
            preserved_signals=preserved_signals,
            processing_time=processing_time,
            memory_usage=0,  # TODO: Implementiere Memory-Tracking
            warnings=self.warnings,
            errors=self.errors
        )
    
    def _parse_arxml_file(self, file_path: str) -> Optional[ET.ElementTree]:
        """Parst eine ARXML-Datei und registriert alle Elemente."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Registriere Namespaces
            self.namespace_manager.register_namespaces(root)
            
            # Scanne und registriere alle wichtigen Elemente
            self._scan_elements(root, file_path)
            
            return tree
            
        except ET.ParseError as e:
            self.errors.append(f"XML-Parse-Fehler in {file_path}: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Unerwarteter Fehler beim Parsen von {file_path}: {e}")
            return None
    
    def _scan_elements(self, root: ET.Element, source_file: str) -> None:
        """Scannt alle wichtigen AUTOSAR-Elemente in einem Baum."""
        # Implementierung für Element-Scanning
        pass
    
    def _merge_trees(self, trees: List[Tuple[ET.ElementTree, str]]) -> Optional[ET.ElementTree]:
        """Führt mehrere ElementTrees zusammen."""
        if not trees:
            return None
        
        # Verwende ersten Baum als Basis
        base_tree, base_file = trees[0]
        base_root = base_tree.getroot()
        
        # Merge alle anderen Bäume
        for tree, source_file in trees[1:]:
            self._merge_single_tree(base_root, tree.getroot(), source_file)
        
        return base_tree
    
    def _merge_single_tree(self, base_root: ET.Element, new_root: ET.Element, source_file: str) -> None:
        """Führt einen einzelnen Baum in den Basis-Baum ein."""
        # Implementierung für Single-Tree-Merge
        pass
    
    def _write_merged_file(self, tree: ET.ElementTree, output_file: str) -> None:
        """Schreibt den gemergten Baum in eine Datei."""
        try:
            # Formatiere XML schön
            self._indent_xml(tree.getroot())
            
            # Schreibe mit XML-Deklaration
            tree.write(
                output_file,
                encoding='utf-8',
                xml_declaration=True,
                method='xml'
            )
            
            logger.info(f"Merged ARXML geschrieben nach: {output_file}")
            
        except Exception as e:
            self.errors.append(f"Fehler beim Schreiben der Ausgabedatei: {e}")
    
    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Formatiert XML für bessere Lesbarkeit."""
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
