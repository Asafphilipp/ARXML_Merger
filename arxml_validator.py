"""
ARXML Validator für AUTOSAR-Schema-Validierung und Strukturprüfung.

Dieser Modul implementiert umfassende Validierungsfunktionen für ARXML-Dateien,
einschließlich Schema-Validierung, Encoding-Detection und Strukturprüfung.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import chardet
import re
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validierungsstufen."""
    BASIC = "basic"          # Nur XML-Wohlgeformtheit
    STRUCTURE = "structure"  # AUTOSAR-Struktur-Validierung
    SCHEMA = "schema"        # Vollständige Schema-Validierung
    SEMANTIC = "semantic"    # Semantische Validierung


class ValidationSeverity(Enum):
    """Schweregrade für Validierungsfehler."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Repräsentiert ein Validierungsproblem."""
    severity: ValidationSeverity
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    element_path: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Ergebnis einer Validierung."""
    is_valid: bool
    issues: List[ValidationIssue]
    encoding: Optional[str]
    autosar_version: Optional[str]
    schema_version: Optional[str]
    element_count: int
    file_size: int


class EncodingDetector:
    """Erkennt und validiert Datei-Encodings."""
    
    SUPPORTED_ENCODINGS = ['utf-8', 'utf-16', 'iso-8859-1', 'windows-1252']
    
    @staticmethod
    def detect_encoding(file_path: str) -> Tuple[str, float]:
        """Erkennt das Encoding einer Datei."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Lese ersten 10KB
            
            # Versuche chardet
            detection = chardet.detect(raw_data)
            if detection and detection['confidence'] > 0.7:
                encoding = detection['encoding'].lower()
                confidence = detection['confidence']
                
                # Normalisiere bekannte Encodings
                if encoding in ['utf-8-sig']:
                    encoding = 'utf-8'
                elif encoding.startswith('iso-8859'):
                    encoding = 'iso-8859-1'
                
                return encoding, confidence
            
            # Fallback: Versuche XML-Header zu parsen
            xml_header = raw_data[:200].decode('utf-8', errors='ignore')
            encoding_match = re.search(r'encoding=["\']([^"\']+)["\']', xml_header)
            if encoding_match:
                return encoding_match.group(1).lower(), 0.9
            
            # Default fallback
            return 'utf-8', 0.5
            
        except Exception as e:
            logger.warning(f"Encoding-Detection fehlgeschlagen für {file_path}: {e}")
            return 'utf-8', 0.0
    
    @staticmethod
    def validate_encoding(file_path: str, expected_encoding: str) -> bool:
        """Validiert, ob eine Datei das erwartete Encoding hat."""
        try:
            with open(file_path, 'r', encoding=expected_encoding) as f:
                f.read()
            return True
        except UnicodeDecodeError:
            return False


class AutosarStructureValidator:
    """Validiert AUTOSAR-spezifische Strukturen."""
    
    # AUTOSAR-spezifische Element-Hierarchien
    REQUIRED_ROOT_ELEMENTS = ['AUTOSAR']
    REQUIRED_AUTOSAR_CHILDREN = ['AR-PACKAGES']
    
    # Bekannte AUTOSAR-Versionen
    AUTOSAR_VERSIONS = {
        '4.0.1', '4.0.2', '4.0.3',
        '4.1.1', '4.1.2', '4.1.3',
        '4.2.1', '4.2.2',
        '4.3.0', '4.3.1',
        '4.4.0', '4.5.0'
    }
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
    
    def validate_structure(self, tree: ET.ElementTree) -> List[ValidationIssue]:
        """Validiert die AUTOSAR-Struktur eines XML-Baums."""
        self.issues = []
        root = tree.getroot()
        
        # Validiere Root-Element
        self._validate_root_element(root)
        
        # Validiere AUTOSAR-Version
        self._validate_autosar_version(root)
        
        # Validiere Package-Struktur
        self._validate_package_structure(root)
        
        # Validiere Short-Names
        self._validate_short_names(root)
        
        # Validiere Referenzen
        self._validate_references(root)
        
        return self.issues
    
    def _validate_root_element(self, root: ET.Element) -> None:
        """Validiert das Root-Element."""
        root_tag = self._strip_namespace(root.tag)
        
        if root_tag not in self.REQUIRED_ROOT_ELEMENTS:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                message=f"Ungültiges Root-Element: {root_tag}. Erwartet: {self.REQUIRED_ROOT_ELEMENTS}",
                element_path="/",
                suggestion="Stellen Sie sicher, dass die Datei ein gültiges AUTOSAR-Root-Element hat."
            ))
    
    def _validate_autosar_version(self, root: ET.Element) -> None:
        """Validiert die AUTOSAR-Version."""
        # Suche nach Schema-Location oder Version-Attributen
        schema_location = root.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation')
        if schema_location:
            # Extrahiere Version aus Schema-Location
            version_match = re.search(r'AUTOSAR_(\d+\.\d+\.\d+)', schema_location)
            if version_match:
                version = version_match.group(1)
                if version not in self.AUTOSAR_VERSIONS:
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Unbekannte AUTOSAR-Version: {version}",
                        element_path="/AUTOSAR",
                        suggestion=f"Unterstützte Versionen: {', '.join(sorted(self.AUTOSAR_VERSIONS))}"
                    ))
    
    def _validate_package_structure(self, root: ET.Element) -> None:
        """Validiert die AR-PACKAGES-Struktur."""
        ar_packages = self._find_elements(root, 'AR-PACKAGES')
        
        if not ar_packages:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Keine AR-PACKAGES gefunden",
                element_path="/AUTOSAR",
                suggestion="AUTOSAR-Dateien müssen mindestens ein AR-PACKAGES-Element enthalten."
            ))
            return
        
        # Validiere Package-Hierarchie
        for packages in ar_packages:
            self._validate_packages_recursive(packages, "/AUTOSAR/AR-PACKAGES")
    
    def _validate_packages_recursive(self, packages_element: ET.Element, path: str) -> None:
        """Validiert Package-Hierarchie rekursiv."""
        ar_packages = self._find_elements(packages_element, 'AR-PACKAGE')
        
        for i, package in enumerate(ar_packages):
            package_path = f"{path}/AR-PACKAGE[{i+1}]"
            
            # Validiere Short-Name
            short_name = self._find_element_text(package, 'SHORT-NAME')
            if not short_name:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message="AR-PACKAGE ohne SHORT-NAME",
                    element_path=package_path,
                    suggestion="Jedes AR-PACKAGE muss ein SHORT-NAME-Element haben."
                ))
            elif not self._is_valid_short_name(short_name):
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Ungültiger SHORT-NAME: {short_name}",
                    element_path=f"{package_path}/SHORT-NAME",
                    suggestion="SHORT-NAME sollte nur alphanumerische Zeichen und Unterstriche enthalten."
                ))
            
            # Rekursive Validierung von Unter-Packages
            sub_packages = self._find_elements(package, 'AR-PACKAGES')
            for sub_package in sub_packages:
                self._validate_packages_recursive(sub_package, f"{package_path}/AR-PACKAGES")
    
    def _validate_short_names(self, root: ET.Element) -> None:
        """Validiert alle SHORT-NAME-Elemente."""
        short_names = {}
        
        for elem in root.iter():
            if self._strip_namespace(elem.tag) == 'SHORT-NAME' and elem.text:
                path = self._get_element_path(elem)
                if elem.text in short_names:
                    # Prüfe auf Duplikate im gleichen Scope
                    existing_path = short_names[elem.text]
                    if self._same_scope(path, existing_path):
                        self.issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Doppelter SHORT-NAME im gleichen Scope: {elem.text}",
                            element_path=path,
                            suggestion="SHORT-NAMEs müssen innerhalb ihres Scopes eindeutig sein."
                        ))
                else:
                    short_names[elem.text] = path
    
    def _validate_references(self, root: ET.Element) -> None:
        """Validiert Referenzen zwischen Elementen."""
        # Sammle alle definierten Elemente
        definitions = set()
        references = []
        
        for elem in root.iter():
            # Sammle Definitionen (Elemente mit SHORT-NAME)
            short_name_elem = self._find_element(elem, 'SHORT-NAME')
            if short_name_elem is not None and short_name_elem.text:
                path = self._get_autosar_path(elem)
                if path:
                    definitions.add(path)
            
            # Sammle Referenzen
            if elem.text and elem.text.startswith('/'):
                references.append((elem.text, self._get_element_path(elem)))
        
        # Validiere Referenzen
        for ref, ref_path in references:
            if ref not in definitions:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Unaufgelöste Referenz: {ref}",
                    element_path=ref_path,
                    suggestion="Stellen Sie sicher, dass das referenzierte Element existiert."
                ))
    
    def _strip_namespace(self, tag: str) -> str:
        """Entfernt Namespace-Präfix von einem Tag."""
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    def _find_elements(self, parent: ET.Element, tag: str) -> List[ET.Element]:
        """Findet alle direkten Kinder mit dem gegebenen Tag."""
        return [child for child in parent if self._strip_namespace(child.tag) == tag]
    
    def _find_element(self, parent: ET.Element, tag: str) -> Optional[ET.Element]:
        """Findet das erste direkte Kind mit dem gegebenen Tag."""
        elements = self._find_elements(parent, tag)
        return elements[0] if elements else None
    
    def _find_element_text(self, parent: ET.Element, tag: str) -> Optional[str]:
        """Findet den Text des ersten direkten Kindes mit dem gegebenen Tag."""
        element = self._find_element(parent, tag)
        return element.text if element is not None else None
    
    def _is_valid_short_name(self, name: str) -> bool:
        """Prüft, ob ein SHORT-NAME gültig ist."""
        return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name))
    
    def _get_element_path(self, element: ET.Element) -> str:
        """Erstellt einen XPath-ähnlichen Pfad für ein Element."""
        # Vereinfachte Implementierung
        return f"/{self._strip_namespace(element.tag)}"
    
    def _get_autosar_path(self, element: ET.Element) -> Optional[str]:
        """Erstellt einen AUTOSAR-Pfad für ein Element."""
        # Vereinfachte Implementierung
        return None
    
    def _same_scope(self, path1: str, path2: str) -> bool:
        """Prüft, ob zwei Pfade im gleichen Scope sind."""
        # Vereinfachte Implementierung
        return path1.rsplit('/', 1)[0] == path2.rsplit('/', 1)[0]


class ARXMLValidator:
    """Hauptklasse für ARXML-Validierung."""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRUCTURE):
        self.validation_level = validation_level
        self.encoding_detector = EncodingDetector()
        self.structure_validator = AutosarStructureValidator()
    
    def validate_file(self, file_path: str) -> ValidationResult:
        """Validiert eine ARXML-Datei."""
        issues = []
        file_size = 0
        element_count = 0
        encoding = None
        autosar_version = None
        schema_version = None
        
        try:
            # Datei-Größe ermitteln
            file_size = Path(file_path).stat().st_size
            
            # Encoding erkennen
            encoding, confidence = self.encoding_detector.detect_encoding(file_path)
            if confidence < 0.8:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Unsichere Encoding-Erkennung: {encoding} (Konfidenz: {confidence:.2f})",
                    suggestion="Überprüfen Sie das Datei-Encoding manuell."
                ))
            
            # XML parsen
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                element_count = len(list(root.iter()))
                
            except ET.ParseError as e:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    message=f"XML-Parse-Fehler: {e}",
                    line_number=getattr(e, 'lineno', None),
                    suggestion="Überprüfen Sie die XML-Syntax der Datei."
                ))
                return ValidationResult(
                    is_valid=False,
                    issues=issues,
                    encoding=encoding,
                    autosar_version=autosar_version,
                    schema_version=schema_version,
                    element_count=0,
                    file_size=file_size
                )
            
            # Struktur-Validierung
            if self.validation_level in [ValidationLevel.STRUCTURE, ValidationLevel.SCHEMA, ValidationLevel.SEMANTIC]:
                structure_issues = self.structure_validator.validate_structure(tree)
                issues.extend(structure_issues)
            
            # Schema-Validierung (falls implementiert)
            if self.validation_level in [ValidationLevel.SCHEMA, ValidationLevel.SEMANTIC]:
                # TODO: Implementiere XSD-Schema-Validierung
                pass
            
            # Semantische Validierung (falls implementiert)
            if self.validation_level == ValidationLevel.SEMANTIC:
                # TODO: Implementiere semantische Validierung
                pass
            
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                message=f"Unerwarteter Fehler: {e}",
                suggestion="Überprüfen Sie die Datei auf Beschädigungen."
            ))
        
        # Bestimme Gesamtvalidität
        is_valid = not any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] for issue in issues)
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            encoding=encoding,
            autosar_version=autosar_version,
            schema_version=schema_version,
            element_count=element_count,
            file_size=file_size
        )
