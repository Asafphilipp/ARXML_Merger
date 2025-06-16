"""
Reporting und Logging für ARXML-Merger.

Dieser Modul erstellt detaillierte Berichte über Merge-Vorgänge,
Signal-Inventare und Performance-Metriken.
"""

import json
import csv
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SignalInfo:
    """Informationen über ein Signal."""
    name: str
    source_file: str
    data_type: Optional[str]
    length: Optional[int]
    interface: Optional[str]
    description: Optional[str]
    path: str


@dataclass
class InterfaceInfo:
    """Informationen über ein Interface."""
    name: str
    source_file: str
    interface_type: str
    signals: List[str]
    operations: List[str]
    path: str


@dataclass
class ConflictInfo:
    """Informationen über einen Konflikt."""
    element_type: str
    element_name: str
    conflict_type: str
    source_files: List[str]
    resolution_strategy: str
    description: str
    warnings: List[str]


@dataclass
class PerformanceMetrics:
    """Performance-Metriken für den Merge-Vorgang."""
    total_processing_time: float
    parsing_time: float
    merging_time: float
    validation_time: float
    writing_time: float
    memory_peak_usage: int
    input_files_count: int
    total_input_size: int
    output_size: int
    elements_processed: int


@dataclass
class MergeReport:
    """Vollständiger Merge-Bericht."""
    timestamp: str
    input_files: List[str]
    output_file: str
    merge_strategy: str
    success: bool
    signals: List[SignalInfo]
    interfaces: List[InterfaceInfo]
    conflicts: List[ConflictInfo]
    performance: PerformanceMetrics
    warnings: List[str]
    errors: List[str]
    validation_results: Dict[str, Any]


class SignalInventoryGenerator:
    """Erstellt ein vollständiges Signal-Inventar."""
    
    def __init__(self):
        self.signals: Dict[str, SignalInfo] = {}
        self.interfaces: Dict[str, InterfaceInfo] = {}
    
    def scan_tree(self, tree: ET.ElementTree, source_file: str) -> None:
        """Scannt einen XML-Baum nach Signalen und Interfaces."""
        root = tree.getroot()
        
        # Scanne nach I-Signalen
        for signal_elem in root.iter():
            if self._get_tag_name(signal_elem.tag) == 'I-SIGNAL':
                self._process_signal(signal_elem, source_file)
        
        # Scanne nach Signal-Gruppen
        for group_elem in root.iter():
            if self._get_tag_name(group_elem.tag) == 'I-SIGNAL-GROUP':
                self._process_signal_group(group_elem, source_file)
        
        # Scanne nach Interfaces
        for interface_elem in root.iter():
            tag_name = self._get_tag_name(interface_elem.tag)
            if tag_name in ['SENDER-RECEIVER-INTERFACE', 'CLIENT-SERVER-INTERFACE']:
                self._process_interface(interface_elem, source_file)
    
    def _process_signal(self, signal_elem: ET.Element, source_file: str) -> None:
        """Verarbeitet ein I-Signal."""
        short_name = self._get_short_name(signal_elem)
        if not short_name:
            return
        
        signal_info = SignalInfo(
            name=short_name,
            source_file=source_file,
            data_type=self._extract_data_type(signal_elem),
            length=self._extract_length(signal_elem),
            interface=self._extract_interface_ref(signal_elem),
            description=self._extract_description(signal_elem),
            path=self._get_element_path(signal_elem)
        )
        
        self.signals[short_name] = signal_info
    
    def _process_signal_group(self, group_elem: ET.Element, source_file: str) -> None:
        """Verarbeitet eine Signal-Gruppe."""
        short_name = self._get_short_name(group_elem)
        if not short_name:
            return
        
        # Extrahiere Signale der Gruppe
        group_signals = []
        for signal_ref in group_elem.iter():
            if self._get_tag_name(signal_ref.tag) == 'I-SIGNAL-REF':
                ref_path = signal_ref.text
                if ref_path:
                    signal_name = ref_path.split('/')[-1]
                    group_signals.append(signal_name)
        
        # Erstelle Signal-Info für die Gruppe
        signal_info = SignalInfo(
            name=short_name,
            source_file=source_file,
            data_type="SIGNAL_GROUP",
            length=len(group_signals),
            interface=self._extract_interface_ref(group_elem),
            description=f"Signal-Gruppe mit {len(group_signals)} Signalen: {', '.join(group_signals)}",
            path=self._get_element_path(group_elem)
        )
        
        self.signals[short_name] = signal_info
    
    def _process_interface(self, interface_elem: ET.Element, source_file: str) -> None:
        """Verarbeitet ein Interface."""
        short_name = self._get_short_name(interface_elem)
        if not short_name:
            return
        
        interface_type = self._get_tag_name(interface_elem.tag)
        
        # Extrahiere Signale
        signals = []
        for data_elem in interface_elem.iter():
            if self._get_tag_name(data_elem.tag) == 'DATA-ELEMENT':
                elem_name = self._get_short_name(data_elem)
                if elem_name:
                    signals.append(elem_name)
        
        # Extrahiere Operationen (für Client-Server-Interfaces)
        operations = []
        for op_elem in interface_elem.iter():
            if self._get_tag_name(op_elem.tag) == 'OPERATION':
                op_name = self._get_short_name(op_elem)
                if op_name:
                    operations.append(op_name)
        
        interface_info = InterfaceInfo(
            name=short_name,
            source_file=source_file,
            interface_type=interface_type,
            signals=signals,
            operations=operations,
            path=self._get_element_path(interface_elem)
        )
        
        self.interfaces[short_name] = interface_info
    
    def _get_tag_name(self, tag: str) -> str:
        """Extrahiert den Tag-Namen ohne Namespace."""
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    def _get_short_name(self, element: ET.Element) -> Optional[str]:
        """Extrahiert den SHORT-NAME eines Elements."""
        short_name_elem = element.find('.//*[local-name()="SHORT-NAME"]')
        return short_name_elem.text if short_name_elem is not None else None
    
    def _extract_data_type(self, element: ET.Element) -> Optional[str]:
        """Extrahiert den Datentyp eines Signals."""
        # Suche nach TYPE-TREF
        type_ref = element.find('.//*[local-name()="TYPE-TREF"]')
        if type_ref is not None and type_ref.text:
            return type_ref.text.split('/')[-1]
        return None
    
    def _extract_length(self, element: ET.Element) -> Optional[int]:
        """Extrahiert die Länge eines Signals."""
        length_elem = element.find('.//*[local-name()="LENGTH"]')
        if length_elem is not None and length_elem.text:
            try:
                return int(length_elem.text)
            except ValueError:
                pass
        return None
    
    def _extract_interface_ref(self, element: ET.Element) -> Optional[str]:
        """Extrahiert die Interface-Referenz."""
        # Vereinfachte Implementierung
        return None
    
    def _extract_description(self, element: ET.Element) -> Optional[str]:
        """Extrahiert die Beschreibung eines Elements."""
        desc_elem = element.find('.//*[local-name()="DESC"]')
        if desc_elem is not None:
            p_elem = desc_elem.find('.//*[local-name()="P"]')
            if p_elem is not None and p_elem.text:
                return p_elem.text.strip()
        return None
    
    def _get_element_path(self, element: ET.Element) -> str:
        """Erstellt einen Pfad für ein Element."""
        # Vereinfachte Implementierung
        return f"/{self._get_tag_name(element.tag)}"
    
    def get_signal_summary(self) -> Dict[str, Any]:
        """Erstellt eine Zusammenfassung aller Signale."""
        return {
            'total_signals': len(self.signals),
            'total_interfaces': len(self.interfaces),
            'signals_by_type': self._group_signals_by_type(),
            'interfaces_by_type': self._group_interfaces_by_type(),
            'source_files': list(set(signal.source_file for signal in self.signals.values()))
        }
    
    def _group_signals_by_type(self) -> Dict[str, int]:
        """Gruppiert Signale nach Datentyp."""
        type_counts = {}
        for signal in self.signals.values():
            data_type = signal.data_type or 'UNKNOWN'
            type_counts[data_type] = type_counts.get(data_type, 0) + 1
        return type_counts
    
    def _group_interfaces_by_type(self) -> Dict[str, int]:
        """Gruppiert Interfaces nach Typ."""
        type_counts = {}
        for interface in self.interfaces.values():
            interface_type = interface.interface_type
            type_counts[interface_type] = type_counts.get(interface_type, 0) + 1
        return type_counts


class ReportGenerator:
    """Hauptklasse für die Berichtserstellung."""
    
    def __init__(self):
        self.signal_inventory = SignalInventoryGenerator()
    
    def generate_report(self, 
                       input_files: List[str],
                       output_file: str,
                       merge_strategy: str,
                       success: bool,
                       conflicts: List[Any],
                       performance: PerformanceMetrics,
                       warnings: List[str],
                       errors: List[str],
                       validation_results: Dict[str, Any]) -> MergeReport:
        """Erstellt einen vollständigen Merge-Bericht."""
        
        # Sammle Signal-Informationen
        signals = list(self.signal_inventory.signals.values())
        interfaces = list(self.signal_inventory.interfaces.values())
        
        # Konvertiere Konflikte
        conflict_infos = []
        for conflict in conflicts:
            conflict_info = ConflictInfo(
                element_type=getattr(conflict, 'element_type', 'UNKNOWN'),
                element_name=getattr(conflict, 'element_name', 'UNKNOWN'),
                conflict_type=getattr(conflict, 'conflict_type', 'UNKNOWN'),
                source_files=getattr(conflict, 'source_files', []),
                resolution_strategy=getattr(conflict, 'resolution', 'UNKNOWN'),
                description=getattr(conflict, 'description', ''),
                warnings=getattr(conflict, 'warnings', [])
            )
            conflict_infos.append(conflict_info)
        
        report = MergeReport(
            timestamp=datetime.now().isoformat(),
            input_files=input_files,
            output_file=output_file,
            merge_strategy=merge_strategy,
            success=success,
            signals=signals,
            interfaces=interfaces,
            conflicts=conflict_infos,
            performance=performance,
            warnings=warnings,
            errors=errors,
            validation_results=validation_results
        )
        
        return report
    
    def save_report_json(self, report: MergeReport, output_path: str) -> None:
        """Speichert den Bericht als JSON-Datei."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False)
            logger.info(f"JSON-Bericht gespeichert: {output_path}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern des JSON-Berichts: {e}")
    
    def save_signal_inventory_csv(self, report: MergeReport, output_path: str) -> None:
        """Speichert das Signal-Inventar als CSV-Datei."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Signal Name', 'Source File', 'Data Type', 'Length',
                    'Interface', 'Description', 'Path'
                ])
                
                # Daten
                for signal in report.signals:
                    writer.writerow([
                        signal.name,
                        signal.source_file,
                        signal.data_type or '',
                        signal.length or '',
                        signal.interface or '',
                        signal.description or '',
                        signal.path
                    ])
            
            logger.info(f"Signal-Inventar CSV gespeichert: {output_path}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Signal-Inventars: {e}")
    
    def save_conflict_report_csv(self, report: MergeReport, output_path: str) -> None:
        """Speichert den Konflikt-Bericht als CSV-Datei."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Element Type', 'Element Name', 'Conflict Type',
                    'Source Files', 'Resolution Strategy', 'Description', 'Warnings'
                ])
                
                # Daten
                for conflict in report.conflicts:
                    writer.writerow([
                        conflict.element_type,
                        conflict.element_name,
                        conflict.conflict_type,
                        '; '.join(conflict.source_files),
                        conflict.resolution_strategy,
                        conflict.description,
                        '; '.join(conflict.warnings)
                    ])
            
            logger.info(f"Konflikt-Bericht CSV gespeichert: {output_path}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Konflikt-Berichts: {e}")
    
    def generate_html_report(self, report: MergeReport, output_path: str) -> None:
        """Erstellt einen HTML-Bericht."""
        html_content = self._create_html_report(report)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML-Bericht gespeichert: {output_path}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern des HTML-Berichts: {e}")
    
    def _create_html_report(self, report: MergeReport) -> str:
        """Erstellt den HTML-Inhalt für den Bericht."""
        html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARXML Merge Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }}
        .metric-card {{ background: #f9f9f9; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ARXML Merge Report</h1>
        <p><strong>Zeitstempel:</strong> {report.timestamp}</p>
        <p><strong>Status:</strong> <span class="{'success' if report.success else 'error'}">
            {'Erfolgreich' if report.success else 'Fehlgeschlagen'}</span></p>
        <p><strong>Merge-Strategie:</strong> {report.merge_strategy}</p>
    </div>
    
    <div class="section">
        <h2>Eingabedateien</h2>
        <ul>
            {''.join(f'<li>{file}</li>' for file in report.input_files)}
        </ul>
        <p><strong>Ausgabedatei:</strong> {report.output_file}</p>
    </div>
    
    <div class="section">
        <h2>Performance-Metriken</h2>
        <div class="metrics">
            <div class="metric-card">
                <h3>Verarbeitungszeit</h3>
                <p>{report.performance.total_processing_time:.2f} Sekunden</p>
            </div>
            <div class="metric-card">
                <h3>Verarbeitete Elemente</h3>
                <p>{report.performance.elements_processed}</p>
            </div>
            <div class="metric-card">
                <h3>Eingabegröße</h3>
                <p>{report.performance.total_input_size / 1024 / 1024:.2f} MB</p>
            </div>
            <div class="metric-card">
                <h3>Ausgabegröße</h3>
                <p>{report.performance.output_size / 1024 / 1024:.2f} MB</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Signal-Zusammenfassung</h2>
        <p><strong>Gesamte Signale:</strong> {len(report.signals)}</p>
        <p><strong>Gesamte Interfaces:</strong> {len(report.interfaces)}</p>
    </div>
    
    <div class="section">
        <h2>Konflikte</h2>
        <p><strong>Anzahl Konflikte:</strong> {len(report.conflicts)}</p>
        {self._create_conflicts_table(report.conflicts)}
    </div>
    
    <div class="section">
        <h2>Warnungen und Fehler</h2>
        {self._create_warnings_section(report.warnings, report.errors)}
    </div>
</body>
</html>
        """
        return html
    
    def _create_conflicts_table(self, conflicts: List[ConflictInfo]) -> str:
        """Erstellt eine HTML-Tabelle für Konflikte."""
        if not conflicts:
            return "<p>Keine Konflikte aufgetreten.</p>"
        
        rows = []
        for conflict in conflicts:
            rows.append(f"""
                <tr>
                    <td>{conflict.element_type}</td>
                    <td>{conflict.element_name}</td>
                    <td>{conflict.conflict_type}</td>
                    <td>{conflict.resolution_strategy}</td>
                    <td>{conflict.description}</td>
                </tr>
            """)
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Element-Typ</th>
                    <th>Element-Name</th>
                    <th>Konflikt-Typ</th>
                    <th>Auflösungsstrategie</th>
                    <th>Beschreibung</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    def _create_warnings_section(self, warnings: List[str], errors: List[str]) -> str:
        """Erstellt eine HTML-Sektion für Warnungen und Fehler."""
        content = ""
        
        if errors:
            content += "<h3 class='error'>Fehler:</h3><ul>"
            content += ''.join(f'<li class="error">{error}</li>' for error in errors)
            content += "</ul>"
        
        if warnings:
            content += "<h3 class='warning'>Warnungen:</h3><ul>"
            content += ''.join(f'<li class="warning">{warning}</li>' for warning in warnings)
            content += "</ul>"
        
        if not content:
            content = "<p>Keine Warnungen oder Fehler.</p>"
        
        return content
