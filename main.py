#!/usr/bin/env python3
"""
Haupteinstiegspunkt für ARXML-Merger.

Dieser Modul bietet sowohl Command-Line-Interface als auch Web-Interface
für den robusten ARXML-Merger.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

from arxml_merger_engine import ARXMLMergerEngine, MergeStrategy
from arxml_validator import ARXMLValidator, ValidationLevel
from conflict_resolver import ConflictResolver, ResolutionStrategy
from arxml_reporter import ReportGenerator
from config import get_config_manager
from utils import setup_logging, performance_monitor, TempFileManager
from web_interface import ARXMLWebServer


def create_argument_parser() -> argparse.ArgumentParser:
    """Erstellt den Argument-Parser für die Command-Line."""
    parser = argparse.ArgumentParser(
        description='Robuster ARXML-Merger für AUTOSAR-Dateien',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Einfacher Merge mit Standard-Einstellungen
  python main.py merge output.arxml input1.arxml input2.arxml
  
  # Merge mit spezifischer Strategie
  python main.py merge --strategy latest_wins output.arxml input1.arxml input2.arxml
  
  # Merge mit Validierung und Berichten
  python main.py merge --validation schema --reports output.arxml input1.arxml input2.arxml
  
  # Web-Interface starten
  python main.py web --port 8080
  
  # Nur Validierung durchführen
  python main.py validate input1.arxml input2.arxml
  
  # Konfiguration erstellen
  python main.py config --create
        """
    )
    
    # Globale Optionen
    parser.add_argument(
        '--config',
        type=str,
        help='Pfad zur Konfigurationsdatei'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='count',
        default=0,
        help='Erhöht Verbosity (kann mehrfach verwendet werden)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Unterdrückt alle Ausgaben außer Fehlern'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Pfad zur Log-Datei'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Verfügbare Kommandos')
    
    # Merge Command
    merge_parser = subparsers.add_parser('merge', help='ARXML-Dateien zusammenführen')
    merge_parser.add_argument(
        'output',
        help='Pfad zur Ausgabe-ARXML-Datei'
    )
    merge_parser.add_argument(
        'inputs',
        nargs='+',
        help='Eingabe-ARXML-Dateien'
    )
    merge_parser.add_argument(
        '--strategy',
        choices=['conservative', 'latest_wins', 'interactive', 'rule_based'],
        default='conservative',
        help='Merge-Strategie (Standard: conservative)'
    )
    merge_parser.add_argument(
        '--validation',
        choices=['basic', 'structure', 'schema', 'semantic'],
        default='structure',
        help='Validierungsstufe (Standard: structure)'
    )
    merge_parser.add_argument(
        '--rules',
        type=str,
        help='Pfad zur JSON-Datei mit Konfliktauflösungsregeln'
    )
    merge_parser.add_argument(
        '--reports',
        action='store_true',
        help='Generiert detaillierte Berichte'
    )
    merge_parser.add_argument(
        '--backup',
        action='store_true',
        help='Erstellt Backups der Eingabedateien'
    )
    merge_parser.add_argument(
        '--output-dir',
        type=str,
        help='Verzeichnis für Ausgabedateien und Berichte'
    )
    
    # Web Command
    web_parser = subparsers.add_parser('web', help='Web-Interface starten')
    web_parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host-Adresse (Standard: localhost)'
    )
    web_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port-Nummer (Standard: 8000)'
    )
    web_parser.add_argument(
        '--debug',
        action='store_true',
        help='Debug-Modus für Web-Interface'
    )
    
    # Validate Command
    validate_parser = subparsers.add_parser('validate', help='ARXML-Dateien validieren')
    validate_parser.add_argument(
        'inputs',
        nargs='+',
        help='Zu validierende ARXML-Dateien'
    )
    validate_parser.add_argument(
        '--level',
        choices=['basic', 'structure', 'schema', 'semantic'],
        default='structure',
        help='Validierungsstufe (Standard: structure)'
    )
    validate_parser.add_argument(
        '--report',
        type=str,
        help='Pfad für Validierungsbericht'
    )
    
    # Config Command
    config_parser = subparsers.add_parser('config', help='Konfiguration verwalten')
    config_parser.add_argument(
        '--create',
        action='store_true',
        help='Erstellt Standard-Konfigurationsdatei'
    )
    config_parser.add_argument(
        '--show',
        action='store_true',
        help='Zeigt aktuelle Konfiguration'
    )
    config_parser.add_argument(
        '--set',
        nargs=2,
        metavar=('KEY', 'VALUE'),
        help='Setzt Konfigurationswert'
    )
    
    return parser


def setup_logging_from_args(args) -> None:
    """Konfiguriert Logging basierend auf Command-Line-Argumenten."""
    if args.quiet:
        level = logging.ERROR
    elif args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose >= 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    setup_logging(level=level, log_file=args.log_file)


def handle_merge_command(args) -> int:
    """Behandelt das Merge-Kommando."""
    logger = logging.getLogger(__name__)
    
    try:
        # Lade Konfiguration
        config_manager = get_config_manager(args.config)
        
        # Validiere Eingabedateien
        for input_file in args.inputs:
            if not Path(input_file).exists():
                logger.error(f"Eingabedatei nicht gefunden: {input_file}")
                return 1
        
        # Erstelle Ausgabeverzeichnis falls nötig
        output_path = Path(args.output)
        if args.output_dir:
            output_path = Path(args.output_dir) / output_path.name
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with performance_monitor() as monitor:
            # Initialisiere Merger
            strategy = MergeStrategy(args.strategy)
            merger = ARXMLMergerEngine(strategy)
            
            # Lade Konfliktauflösungsregeln falls vorhanden
            if args.rules:
                merger.conflict_resolver.load_rules(args.rules)
            
            # Führe Merge durch
            logger.info(f"Starte Merge von {len(args.inputs)} Dateien...")
            result = merger.merge_files(args.inputs, str(output_path))
            
            if result.success:
                logger.info(f"Merge erfolgreich abgeschlossen: {output_path}")
                logger.info(f"Verarbeitungszeit: {result.processing_time:.2f}s")
                logger.info(f"Erhaltene Signale: {len(result.preserved_signals)}")
                logger.info(f"Aufgelöste Konflikte: {len(result.conflicts)}")
                
                # Generiere Berichte falls gewünscht
                if args.reports:
                    generate_reports(result, args, config_manager)
                
                # Zeige Warnungen
                if result.warnings:
                    logger.warning("Warnungen aufgetreten:")
                    for warning in result.warnings:
                        logger.warning(f"  - {warning}")
                
                return 0
            else:
                logger.error("Merge fehlgeschlagen")
                for error in result.errors:
                    logger.error(f"  - {error}")
                return 1
    
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim Merge: {e}")
        return 1


def generate_reports(merge_result, args, config_manager) -> None:
    """Generiert Berichte für das Merge-Ergebnis."""
    logger = logging.getLogger(__name__)
    
    try:
        reporter = ReportGenerator()
        
        # Bestimme Ausgabeverzeichnis für Berichte
        if args.output_dir:
            report_dir = Path(args.output_dir) / "reports"
        else:
            report_dir = Path(args.output).parent / "reports"
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Erstelle Performance-Metriken (vereinfacht)
        from arxml_reporter import PerformanceMetrics
        performance = PerformanceMetrics(
            total_processing_time=merge_result.processing_time,
            parsing_time=0,
            merging_time=merge_result.processing_time,
            validation_time=0,
            writing_time=0,
            memory_peak_usage=merge_result.memory_usage,
            input_files_count=len(args.inputs),
            total_input_size=sum(Path(f).stat().st_size for f in args.inputs if Path(f).exists()),
            output_size=Path(args.output).stat().st_size if Path(args.output).exists() else 0,
            elements_processed=0
        )
        
        # Generiere Bericht
        report = reporter.generate_report(
            input_files=args.inputs,
            output_file=args.output,
            merge_strategy=args.strategy,
            success=merge_result.success,
            conflicts=merge_result.conflicts,
            performance=performance,
            warnings=merge_result.warnings,
            errors=merge_result.errors,
            validation_results={}
        )
        
        # Speichere Berichte
        reporter.save_report_json(report, str(report_dir / "merge_report.json"))
        reporter.generate_html_report(report, str(report_dir / "merge_report.html"))
        reporter.save_signal_inventory_csv(report, str(report_dir / "signal_inventory.csv"))
        reporter.save_conflict_report_csv(report, str(report_dir / "conflicts.csv"))
        
        logger.info(f"Berichte generiert in: {report_dir}")
        
    except Exception as e:
        logger.error(f"Fehler beim Generieren der Berichte: {e}")


def handle_web_command(args) -> int:
    """Behandelt das Web-Kommando."""
    logger = logging.getLogger(__name__)
    
    try:
        # Lade Konfiguration
        config_manager = get_config_manager(args.config)
        
        # Überschreibe Web-Konfiguration mit Command-Line-Argumenten
        web_config = config_manager.get_web_config()
        if args.host:
            web_config.host = args.host
        if args.port:
            web_config.port = args.port
        if args.debug:
            web_config.debug_mode = args.debug
        
        # Starte Web-Server
        server = ARXMLWebServer(port=web_config.port, host=web_config.host)
        server.start()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Web-Server durch Benutzer beendet")
        return 0
    except Exception as e:
        logger.error(f"Fehler beim Starten des Web-Servers: {e}")
        return 1


def handle_validate_command(args) -> int:
    """Behandelt das Validate-Kommando."""
    logger = logging.getLogger(__name__)
    
    try:
        validation_level = ValidationLevel(args.level)
        validator = ARXMLValidator(validation_level)
        
        all_valid = True
        results = []
        
        for input_file in args.inputs:
            if not Path(input_file).exists():
                logger.error(f"Datei nicht gefunden: {input_file}")
                all_valid = False
                continue
            
            logger.info(f"Validiere: {input_file}")
            result = validator.validate_file(input_file)
            results.append((input_file, result))
            
            if result.is_valid:
                logger.info(f"✅ {input_file} ist gültig")
            else:
                logger.error(f"❌ {input_file} ist ungültig")
                all_valid = False
            
            # Zeige Issues
            for issue in result.issues:
                level_symbol = {
                    'info': 'ℹ️',
                    'warning': '⚠️',
                    'error': '❌',
                    'critical': '🚨'
                }.get(issue.severity.value, '❓')
                
                logger.log(
                    logging.INFO if issue.severity.value == 'info' else
                    logging.WARNING if issue.severity.value == 'warning' else
                    logging.ERROR,
                    f"  {level_symbol} {issue.message}"
                )
        
        # Generiere Validierungsbericht falls gewünscht
        if args.report:
            generate_validation_report(results, args.report)
        
        return 0 if all_valid else 1
        
    except Exception as e:
        logger.error(f"Fehler bei der Validierung: {e}")
        return 1


def generate_validation_report(results, report_path: str) -> None:
    """Generiert einen Validierungsbericht."""
    logger = logging.getLogger(__name__)
    
    try:
        import json
        
        report_data = {
            'timestamp': str(Path().cwd()),
            'total_files': len(results),
            'valid_files': sum(1 for _, result in results if result.is_valid),
            'files': []
        }
        
        for file_path, result in results:
            file_data = {
                'path': file_path,
                'valid': result.is_valid,
                'encoding': result.encoding,
                'autosar_version': result.autosar_version,
                'element_count': result.element_count,
                'file_size': result.file_size,
                'issues': [
                    {
                        'severity': issue.severity.value,
                        'message': issue.message,
                        'line_number': issue.line_number,
                        'element_path': issue.element_path,
                        'suggestion': issue.suggestion
                    }
                    for issue in result.issues
                ]
            }
            report_data['files'].append(file_data)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Validierungsbericht gespeichert: {report_path}")
        
    except Exception as e:
        logger.error(f"Fehler beim Generieren des Validierungsberichts: {e}")


def handle_config_command(args) -> int:
    """Behandelt das Config-Kommando."""
    logger = logging.getLogger(__name__)
    
    try:
        config_manager = get_config_manager(args.config)
        
        if args.create:
            config_manager.create_default_config_file()
            logger.info("Standard-Konfigurationsdatei erstellt")
        
        if args.show:
            import json
            from dataclasses import asdict
            
            config_dict = {
                'merge': asdict(config_manager.config.merge),
                'validation': asdict(config_manager.config.validation),
                'reporting': asdict(config_manager.config.reporting),
                'web': asdict(config_manager.config.web),
                'performance': asdict(config_manager.config.performance)
            }
            
            print(json.dumps(config_dict, indent=2, ensure_ascii=False))
        
        if args.set:
            key, value = args.set
            # Vereinfachte Implementierung für Konfiguration setzen
            logger.info(f"Konfiguration setzen: {key} = {value}")
            # TODO: Implementiere das Setzen von Konfigurationswerten
        
        return 0
        
    except Exception as e:
        logger.error(f"Fehler bei der Konfiguration: {e}")
        return 1


def main() -> int:
    """Hauptfunktion."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup Logging
    setup_logging_from_args(args)
    logger = logging.getLogger(__name__)
    
    # Zeige Hilfe wenn kein Kommando angegeben
    if not args.command:
        parser.print_help()
        return 1
    
    # Führe entsprechendes Kommando aus
    try:
        if args.command == 'merge':
            return handle_merge_command(args)
        elif args.command == 'web':
            return handle_web_command(args)
        elif args.command == 'validate':
            return handle_validate_command(args)
        elif args.command == 'config':
            return handle_config_command(args)
        else:
            logger.error(f"Unbekanntes Kommando: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        logger.info("Vorgang durch Benutzer abgebrochen")
        return 130  # Standard exit code für SIGINT
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        if args.verbose >= 2:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
