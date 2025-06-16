"""
Konfigurationsmanagement für ARXML-Merger.

Dieser Modul verwaltet alle Konfigurationsoptionen und Einstellungen
für den ARXML-Merger.
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class MergeConfig:
    """Konfiguration für Merge-Vorgänge."""
    strategy: str = "conservative"
    validation_level: str = "structure"
    generate_reports: bool = True
    pretty_print: bool = True
    validate_output: bool = True
    backup_originals: bool = False
    max_file_size_mb: int = 100
    timeout_seconds: int = 300
    parallel_processing: bool = True
    preserve_comments: bool = True


@dataclass
class ValidationConfig:
    """Konfiguration für Validierung."""
    check_schema: bool = True
    check_references: bool = True
    check_signal_integrity: bool = True
    autosar_versions: List[str] = None
    custom_schema_path: Optional[str] = None
    strict_mode: bool = False
    
    def __post_init__(self):
        if self.autosar_versions is None:
            self.autosar_versions = ["4.2.1", "4.3.0", "4.4.0", "4.5.0"]


@dataclass
class ReportConfig:
    """Konfiguration für Berichtserstellung."""
    generate_html: bool = True
    generate_json: bool = True
    generate_csv: bool = True
    include_signal_inventory: bool = True
    include_conflict_details: bool = True
    include_performance_metrics: bool = True
    output_directory: str = "reports"
    template_path: Optional[str] = None


@dataclass
class WebConfig:
    """Konfiguration für Web-Interface."""
    host: str = "localhost"
    port: int = 8000
    max_upload_size_mb: int = 50
    session_timeout_minutes: int = 60
    enable_cors: bool = True
    debug_mode: bool = False
    static_files_path: str = "static"


@dataclass
class PerformanceConfig:
    """Konfiguration für Performance-Optimierung."""
    max_memory_usage_mb: int = 1024
    chunk_size_kb: int = 64
    enable_streaming: bool = True
    parallel_workers: int = 4
    cache_parsed_files: bool = True
    compression_level: int = 6


@dataclass
class ARXMLMergerConfig:
    """Hauptkonfiguration für ARXML-Merger."""
    merge: MergeConfig
    validation: ValidationConfig
    reporting: ReportConfig
    web: WebConfig
    performance: PerformanceConfig
    
    def __init__(self):
        self.merge = MergeConfig()
        self.validation = ValidationConfig()
        self.reporting = ReportConfig()
        self.web = WebConfig()
        self.performance = PerformanceConfig()


class ConfigManager:
    """Verwaltet Konfigurationsdateien und -einstellungen."""
    
    DEFAULT_CONFIG_FILE = "arxml_merger_config.json"
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.config = ARXMLMergerConfig()
        self._load_config()
    
    def _load_config(self) -> None:
        """Lädt Konfiguration aus Datei."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Lade Merge-Konfiguration
                if 'merge' in config_data:
                    self._update_dataclass(self.config.merge, config_data['merge'])
                
                # Lade Validierungs-Konfiguration
                if 'validation' in config_data:
                    self._update_dataclass(self.config.validation, config_data['validation'])
                
                # Lade Reporting-Konfiguration
                if 'reporting' in config_data:
                    self._update_dataclass(self.config.reporting, config_data['reporting'])
                
                # Lade Web-Konfiguration
                if 'web' in config_data:
                    self._update_dataclass(self.config.web, config_data['web'])
                
                # Lade Performance-Konfiguration
                if 'performance' in config_data:
                    self._update_dataclass(self.config.performance, config_data['performance'])
                
                logger.info(f"Konfiguration geladen aus: {self.config_file}")
                
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Konfiguration: {e}")
                logger.info("Verwende Standard-Konfiguration")
        else:
            logger.info(f"Keine Konfigurationsdatei gefunden ({self.config_file}), verwende Standardwerte")
    
    def _update_dataclass(self, target_obj: Any, source_dict: Dict[str, Any]) -> None:
        """Aktualisiert ein Dataclass-Objekt mit Werten aus einem Dictionary."""
        for key, value in source_dict.items():
            if hasattr(target_obj, key):
                setattr(target_obj, key, value)
            else:
                logger.warning(f"Unbekannte Konfigurationsoption: {key}")
    
    def save_config(self) -> None:
        """Speichert aktuelle Konfiguration in Datei."""
        try:
            config_dict = {
                'merge': asdict(self.config.merge),
                'validation': asdict(self.config.validation),
                'reporting': asdict(self.config.reporting),
                'web': asdict(self.config.web),
                'performance': asdict(self.config.performance)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Konfiguration gespeichert in: {self.config_file}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
    
    def get_merge_config(self) -> MergeConfig:
        """Gibt Merge-Konfiguration zurück."""
        return self.config.merge
    
    def get_validation_config(self) -> ValidationConfig:
        """Gibt Validierungs-Konfiguration zurück."""
        return self.config.validation
    
    def get_reporting_config(self) -> ReportConfig:
        """Gibt Reporting-Konfiguration zurück."""
        return self.config.reporting
    
    def get_web_config(self) -> WebConfig:
        """Gibt Web-Konfiguration zurück."""
        return self.config.web
    
    def get_performance_config(self) -> PerformanceConfig:
        """Gibt Performance-Konfiguration zurück."""
        return self.config.performance
    
    def update_merge_strategy(self, strategy: str) -> None:
        """Aktualisiert die Merge-Strategie."""
        valid_strategies = ["conservative", "latest_wins", "interactive", "rule_based"]
        if strategy in valid_strategies:
            self.config.merge.strategy = strategy
            logger.info(f"Merge-Strategie geändert zu: {strategy}")
        else:
            logger.error(f"Ungültige Merge-Strategie: {strategy}")
    
    def update_validation_level(self, level: str) -> None:
        """Aktualisiert die Validierungsstufe."""
        valid_levels = ["basic", "structure", "schema", "semantic"]
        if level in valid_levels:
            self.config.validation.check_schema = level in ["schema", "semantic"]
            logger.info(f"Validierungsstufe geändert zu: {level}")
        else:
            logger.error(f"Ungültige Validierungsstufe: {level}")
    
    def create_default_config_file(self) -> None:
        """Erstellt eine Standard-Konfigurationsdatei."""
        if not os.path.exists(self.config_file):
            self.save_config()
            logger.info(f"Standard-Konfigurationsdatei erstellt: {self.config_file}")
        else:
            logger.info(f"Konfigurationsdatei existiert bereits: {self.config_file}")


class EnvironmentConfig:
    """Verwaltet Umgebungsvariablen für ARXML-Merger."""
    
    @staticmethod
    def get_config_from_env() -> Dict[str, Any]:
        """Lädt Konfiguration aus Umgebungsvariablen."""
        config = {}
        
        # Web-Konfiguration
        if 'ARXML_MERGER_HOST' in os.environ:
            config['web'] = config.get('web', {})
            config['web']['host'] = os.environ['ARXML_MERGER_HOST']
        
        if 'ARXML_MERGER_PORT' in os.environ:
            config['web'] = config.get('web', {})
            try:
                config['web']['port'] = int(os.environ['ARXML_MERGER_PORT'])
            except ValueError:
                logger.warning("Ungültiger Port in ARXML_MERGER_PORT")
        
        # Debug-Modus
        if 'ARXML_MERGER_DEBUG' in os.environ:
            config['web'] = config.get('web', {})
            config['web']['debug_mode'] = os.environ['ARXML_MERGER_DEBUG'].lower() in ['true', '1', 'yes']
        
        # Performance-Konfiguration
        if 'ARXML_MERGER_MAX_MEMORY' in os.environ:
            config['performance'] = config.get('performance', {})
            try:
                config['performance']['max_memory_usage_mb'] = int(os.environ['ARXML_MERGER_MAX_MEMORY'])
            except ValueError:
                logger.warning("Ungültiger Wert in ARXML_MERGER_MAX_MEMORY")
        
        # Merge-Strategie
        if 'ARXML_MERGER_STRATEGY' in os.environ:
            config['merge'] = config.get('merge', {})
            config['merge']['strategy'] = os.environ['ARXML_MERGER_STRATEGY']
        
        return config
    
    @staticmethod
    def apply_env_config(config_manager: ConfigManager) -> None:
        """Wendet Umgebungsvariablen auf ConfigManager an."""
        env_config = EnvironmentConfig.get_config_from_env()
        
        if 'web' in env_config:
            config_manager._update_dataclass(config_manager.config.web, env_config['web'])
        
        if 'performance' in env_config:
            config_manager._update_dataclass(config_manager.config.performance, env_config['performance'])
        
        if 'merge' in env_config:
            config_manager._update_dataclass(config_manager.config.merge, env_config['merge'])
        
        logger.info("Umgebungsvariablen angewendet")


# Globale Konfigurationsinstanz
_global_config_manager = None


def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """Gibt die globale ConfigManager-Instanz zurück."""
    global _global_config_manager
    
    if _global_config_manager is None:
        _global_config_manager = ConfigManager(config_file)
        EnvironmentConfig.apply_env_config(_global_config_manager)
    
    return _global_config_manager


def reset_config_manager() -> None:
    """Setzt die globale ConfigManager-Instanz zurück."""
    global _global_config_manager
    _global_config_manager = None
