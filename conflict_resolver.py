"""
Erweiterte Konfliktauflösung für ARXML-Merger.

Dieser Modul implementiert intelligente Strategien zur Auflösung von Konflikten
beim Zusammenführen von AUTOSAR ARXML-Dateien.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Arten von Merge-Konflikten."""
    DUPLICATE_ELEMENT = "duplicate_element"
    DIFFERENT_ATTRIBUTES = "different_attributes"
    DIFFERENT_CONTENT = "different_content"
    INCOMPATIBLE_TYPES = "incompatible_types"
    REFERENCE_CONFLICT = "reference_conflict"
    VERSION_MISMATCH = "version_mismatch"


class ResolutionStrategy(Enum):
    """Strategien zur Konfliktauflösung."""
    KEEP_FIRST = "keep_first"
    KEEP_LAST = "keep_last"
    MERGE_ATTRIBUTES = "merge_attributes"
    MERGE_CONTENT = "merge_content"
    USER_CHOICE = "user_choice"
    RULE_BASED = "rule_based"
    SKIP = "skip"


@dataclass
class ConflictRule:
    """Regel für die Konfliktauflösung."""
    element_type: str
    conflict_type: ConflictType
    resolution_strategy: ResolutionStrategy
    priority: int = 0
    conditions: Optional[Dict[str, Any]] = None
    custom_handler: Optional[str] = None


@dataclass
class ConflictContext:
    """Kontext-Informationen für einen Konflikt."""
    element1: ET.Element
    element2: ET.Element
    source_file1: str
    source_file2: str
    element_path: str
    conflict_type: ConflictType
    metadata: Dict[str, Any]


@dataclass
class ConflictResolution:
    """Ergebnis einer Konfliktauflösung."""
    resolved_element: Optional[ET.Element]
    strategy_used: ResolutionStrategy
    description: str
    warnings: List[str]
    user_input_required: bool = False


class RuleEngine:
    """Engine für regelbasierte Konfliktauflösung."""
    
    def __init__(self):
        self.rules: List[ConflictRule] = []
        self.custom_handlers: Dict[str, Callable] = {}
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Lädt Standard-Konfliktauflösungsregeln."""
        # Signale: Erste Datei hat Priorität
        self.rules.append(ConflictRule(
            element_type="I-SIGNAL",
            conflict_type=ConflictType.DUPLICATE_ELEMENT,
            resolution_strategy=ResolutionStrategy.KEEP_FIRST,
            priority=10
        ))
        
        # Interfaces: Merge Attribute
        self.rules.append(ConflictRule(
            element_type="SENDER-RECEIVER-INTERFACE",
            conflict_type=ConflictType.DIFFERENT_ATTRIBUTES,
            resolution_strategy=ResolutionStrategy.MERGE_ATTRIBUTES,
            priority=8
        ))
        
        # Datentypen: Letzte Datei gewinnt
        self.rules.append(ConflictRule(
            element_type="PRIMITIVE-TYPE",
            conflict_type=ConflictType.DUPLICATE_ELEMENT,
            resolution_strategy=ResolutionStrategy.KEEP_LAST,
            priority=5
        ))
        
        # ECU-Instanzen: Benutzer-Entscheidung
        self.rules.append(ConflictRule(
            element_type="ECU-INSTANCE",
            conflict_type=ConflictType.DUPLICATE_ELEMENT,
            resolution_strategy=ResolutionStrategy.USER_CHOICE,
            priority=15
        ))
    
    def load_rules_from_file(self, rules_file: str) -> None:
        """Lädt Regeln aus einer JSON-Datei."""
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            
            for rule_data in rules_data.get('rules', []):
                rule = ConflictRule(
                    element_type=rule_data['element_type'],
                    conflict_type=ConflictType(rule_data['conflict_type']),
                    resolution_strategy=ResolutionStrategy(rule_data['resolution_strategy']),
                    priority=rule_data.get('priority', 0),
                    conditions=rule_data.get('conditions'),
                    custom_handler=rule_data.get('custom_handler')
                )
                self.rules.append(rule)
            
            # Sortiere nach Priorität
            self.rules.sort(key=lambda r: r.priority, reverse=True)
            
            logger.info(f"Geladen: {len(rules_data.get('rules', []))} Regeln aus {rules_file}")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Regeln aus {rules_file}: {e}")
    
    def find_applicable_rule(self, context: ConflictContext) -> Optional[ConflictRule]:
        """Findet die passende Regel für einen Konflikt."""
        element_type = self._get_element_type(context.element1)
        
        for rule in self.rules:
            if (rule.element_type == element_type or rule.element_type == "*") and \
               rule.conflict_type == context.conflict_type:
                
                # Prüfe zusätzliche Bedingungen
                if rule.conditions and not self._check_conditions(rule.conditions, context):
                    continue
                
                return rule
        
        return None
    
    def _get_element_type(self, element: ET.Element) -> str:
        """Extrahiert den AUTOSAR-Element-Typ."""
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]
        return tag
    
    def _check_conditions(self, conditions: Dict[str, Any], context: ConflictContext) -> bool:
        """Prüft, ob die Bedingungen einer Regel erfüllt sind."""
        # Implementierung für Bedingungsprüfung
        return True
    
    def register_custom_handler(self, name: str, handler: Callable) -> None:
        """Registriert einen benutzerdefinierten Konflikt-Handler."""
        self.custom_handlers[name] = handler


class InteractiveResolver:
    """Interaktive Konfliktauflösung mit Benutzer-Eingabe."""
    
    def __init__(self):
        self.user_choices: Dict[str, str] = {}
    
    def resolve_interactively(self, context: ConflictContext) -> ConflictResolution:
        """Löst einen Konflikt interaktiv auf."""
        print(f"\n=== KONFLIKT ERKANNT ===")
        print(f"Element-Typ: {self._get_element_type(context.element1)}")
        print(f"Pfad: {context.element_path}")
        print(f"Konflikt-Typ: {context.conflict_type.value}")
        print(f"Quelle 1: {context.source_file1}")
        print(f"Quelle 2: {context.source_file2}")
        
        # Zeige Element-Details
        self._show_element_details("Element 1", context.element1)
        self._show_element_details("Element 2", context.element2)
        
        # Benutzer-Auswahl
        while True:
            choice = input("\nWählen Sie eine Option:\n"
                          "1) Element 1 behalten\n"
                          "2) Element 2 behalten\n"
                          "3) Elemente zusammenführen\n"
                          "4) Überspringen\n"
                          "Ihre Wahl (1-4): ").strip()
            
            if choice == '1':
                return ConflictResolution(
                    resolved_element=context.element1,
                    strategy_used=ResolutionStrategy.KEEP_FIRST,
                    description="Benutzer wählte Element 1",
                    warnings=[]
                )
            elif choice == '2':
                return ConflictResolution(
                    resolved_element=context.element2,
                    strategy_used=ResolutionStrategy.KEEP_LAST,
                    description="Benutzer wählte Element 2",
                    warnings=[]
                )
            elif choice == '3':
                merged = self._merge_elements(context.element1, context.element2)
                return ConflictResolution(
                    resolved_element=merged,
                    strategy_used=ResolutionStrategy.MERGE_CONTENT,
                    description="Benutzer wählte Zusammenführung",
                    warnings=[]
                )
            elif choice == '4':
                return ConflictResolution(
                    resolved_element=None,
                    strategy_used=ResolutionStrategy.SKIP,
                    description="Benutzer wählte Überspringen",
                    warnings=["Element wurde übersprungen"]
                )
            else:
                print("Ungültige Eingabe. Bitte wählen Sie 1-4.")
    
    def _get_element_type(self, element: ET.Element) -> str:
        """Extrahiert den Element-Typ."""
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]
        return tag
    
    def _show_element_details(self, title: str, element: ET.Element) -> None:
        """Zeigt Details eines Elements."""
        print(f"\n{title}:")
        
        # Short-Name
        short_name = element.findtext('.//SHORT-NAME')
        if short_name:
            print(f"  SHORT-NAME: {short_name}")
        
        # Attribute
        if element.attrib:
            print("  Attribute:")
            for key, value in element.attrib.items():
                print(f"    {key}: {value}")
        
        # Wichtige Kinder-Elemente
        for child in element[:3]:  # Zeige nur erste 3 Kinder
            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if child.text and child.text.strip():
                print(f"  {child_tag}: {child.text.strip()}")
    
    def _merge_elements(self, elem1: ET.Element, elem2: ET.Element) -> ET.Element:
        """Führt zwei Elemente zusammen."""
        # Erstelle Kopie von elem1 als Basis
        merged = ET.Element(elem1.tag, elem1.attrib)
        merged.text = elem1.text
        merged.tail = elem1.tail
        
        # Füge alle Kinder von elem1 hinzu
        for child in elem1:
            merged.append(child)
        
        # Füge einzigartige Kinder von elem2 hinzu
        elem1_children = {self._get_child_key(child): child for child in elem1}
        
        for child in elem2:
            child_key = self._get_child_key(child)
            if child_key not in elem1_children:
                merged.append(child)
        
        return merged
    
    def _get_child_key(self, element: ET.Element) -> str:
        """Erstellt einen eindeutigen Schlüssel für ein Kind-Element."""
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        short_name = element.findtext('.//SHORT-NAME')
        return f"{tag}:{short_name}" if short_name else tag


class AutomaticResolver:
    """Automatische Konfliktauflösung basierend auf Strategien."""
    
    def __init__(self):
        self.strategy_handlers = {
            ResolutionStrategy.KEEP_FIRST: self._keep_first,
            ResolutionStrategy.KEEP_LAST: self._keep_last,
            ResolutionStrategy.MERGE_ATTRIBUTES: self._merge_attributes,
            ResolutionStrategy.MERGE_CONTENT: self._merge_content,
            ResolutionStrategy.SKIP: self._skip
        }
    
    def resolve_automatically(self, context: ConflictContext, strategy: ResolutionStrategy) -> ConflictResolution:
        """Löst einen Konflikt automatisch auf."""
        handler = self.strategy_handlers.get(strategy)
        if not handler:
            return ConflictResolution(
                resolved_element=context.element1,
                strategy_used=ResolutionStrategy.KEEP_FIRST,
                description=f"Unbekannte Strategie {strategy}, verwende KEEP_FIRST",
                warnings=[f"Strategie {strategy} nicht implementiert"]
            )
        
        return handler(context)
    
    def _keep_first(self, context: ConflictContext) -> ConflictResolution:
        """Behält das erste Element."""
        return ConflictResolution(
            resolved_element=context.element1,
            strategy_used=ResolutionStrategy.KEEP_FIRST,
            description=f"Erstes Element aus {context.source_file1} beibehalten",
            warnings=[]
        )
    
    def _keep_last(self, context: ConflictContext) -> ConflictResolution:
        """Behält das letzte Element."""
        return ConflictResolution(
            resolved_element=context.element2,
            strategy_used=ResolutionStrategy.KEEP_LAST,
            description=f"Letztes Element aus {context.source_file2} beibehalten",
            warnings=[]
        )
    
    def _merge_attributes(self, context: ConflictContext) -> ConflictResolution:
        """Führt Attribute zusammen."""
        merged = ET.Element(context.element1.tag)
        merged.text = context.element1.text
        merged.tail = context.element1.tail
        
        # Kopiere alle Kinder von element1
        for child in context.element1:
            merged.append(child)
        
        # Merge Attribute (element2 überschreibt element1)
        merged.attrib.update(context.element1.attrib)
        merged.attrib.update(context.element2.attrib)
        
        warnings = []
        conflicting_attrs = set(context.element1.attrib.keys()) & set(context.element2.attrib.keys())
        if conflicting_attrs:
            warnings.append(f"Überschriebene Attribute: {', '.join(conflicting_attrs)}")
        
        return ConflictResolution(
            resolved_element=merged,
            strategy_used=ResolutionStrategy.MERGE_ATTRIBUTES,
            description="Attribute zusammengeführt",
            warnings=warnings
        )
    
    def _merge_content(self, context: ConflictContext) -> ConflictResolution:
        """Führt Inhalte zusammen."""
        merged = ET.Element(context.element1.tag, context.element1.attrib)
        merged.text = context.element1.text
        merged.tail = context.element1.tail
        
        # Sammle alle Kinder
        children_map = {}
        
        # Füge Kinder von element1 hinzu
        for child in context.element1:
            key = self._get_element_key(child)
            children_map[key] = child
        
        # Füge Kinder von element2 hinzu (überschreibt bei Konflikten)
        for child in context.element2:
            key = self._get_element_key(child)
            children_map[key] = child
        
        # Füge alle Kinder zum merged Element hinzu
        for child in children_map.values():
            merged.append(child)
        
        return ConflictResolution(
            resolved_element=merged,
            strategy_used=ResolutionStrategy.MERGE_CONTENT,
            description="Inhalte zusammengeführt",
            warnings=[]
        )
    
    def _skip(self, context: ConflictContext) -> ConflictResolution:
        """Überspringt das Element."""
        return ConflictResolution(
            resolved_element=None,
            strategy_used=ResolutionStrategy.SKIP,
            description="Element übersprungen",
            warnings=["Element wurde aufgrund von Konflikten übersprungen"]
        )
    
    def _get_element_key(self, element: ET.Element) -> str:
        """Erstellt einen eindeutigen Schlüssel für ein Element."""
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        short_name = element.findtext('.//SHORT-NAME')
        return f"{tag}:{short_name}" if short_name else f"{tag}:{id(element)}"


class ConflictResolver:
    """Hauptklasse für Konfliktauflösung."""
    
    def __init__(self, default_strategy: ResolutionStrategy = ResolutionStrategy.KEEP_FIRST):
        self.default_strategy = default_strategy
        self.rule_engine = RuleEngine()
        self.interactive_resolver = InteractiveResolver()
        self.automatic_resolver = AutomaticResolver()
        self.resolved_conflicts: List[Tuple[ConflictContext, ConflictResolution]] = []
    
    def resolve_conflict(self, context: ConflictContext) -> ConflictResolution:
        """Löst einen Konflikt basierend auf den verfügbaren Strategien auf."""
        # Versuche regelbasierte Auflösung
        rule = self.rule_engine.find_applicable_rule(context)
        
        if rule:
            if rule.custom_handler and rule.custom_handler in self.rule_engine.custom_handlers:
                # Verwende benutzerdefinierten Handler
                handler = self.rule_engine.custom_handlers[rule.custom_handler]
                resolution = handler(context)
            elif rule.resolution_strategy == ResolutionStrategy.USER_CHOICE:
                # Interaktive Auflösung
                resolution = self.interactive_resolver.resolve_interactively(context)
            else:
                # Automatische Auflösung
                resolution = self.automatic_resolver.resolve_automatically(context, rule.resolution_strategy)
        else:
            # Fallback auf Standard-Strategie
            resolution = self.automatic_resolver.resolve_automatically(context, self.default_strategy)
        
        # Speichere Auflösung für Berichterstattung
        self.resolved_conflicts.append((context, resolution))
        
        logger.info(f"Konflikt aufgelöst: {context.element_path} -> {resolution.strategy_used.value}")
        
        return resolution
    
    def load_rules(self, rules_file: str) -> None:
        """Lädt Konfliktauflösungsregeln aus einer Datei."""
        self.rule_engine.load_rules_from_file(rules_file)
    
    def get_conflict_summary(self) -> Dict[str, Any]:
        """Erstellt eine Zusammenfassung aller aufgelösten Konflikte."""
        summary = {
            'total_conflicts': len(self.resolved_conflicts),
            'strategies_used': {},
            'conflict_types': {},
            'warnings': []
        }
        
        for context, resolution in self.resolved_conflicts:
            # Zähle Strategien
            strategy = resolution.strategy_used.value
            summary['strategies_used'][strategy] = summary['strategies_used'].get(strategy, 0) + 1
            
            # Zähle Konflikt-Typen
            conflict_type = context.conflict_type.value
            summary['conflict_types'][conflict_type] = summary['conflict_types'].get(conflict_type, 0) + 1
            
            # Sammle Warnungen
            summary['warnings'].extend(resolution.warnings)
        
        return summary
