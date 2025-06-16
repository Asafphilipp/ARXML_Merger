"""
Utility-Funktionen für ARXML-Merger.

Dieser Modul enthält allgemeine Hilfsfunktionen und Utilities
für den ARXML-Merger.
"""

import os
import time
import hashlib
import tempfile
import shutil
from typing import List, Dict, Any, Optional, Tuple, Generator
from pathlib import Path
import xml.etree.ElementTree as ET
import logging
import psutil
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Überwacht Performance-Metriken während der Verarbeitung."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Startet Performance-Monitoring."""
        self.start_time = time.time()
        self.monitoring = True
        self.memory_samples = []
        
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()
        
        logger.debug("Performance-Monitoring gestartet")
    
    def stop_monitoring(self):
        """Stoppt Performance-Monitoring."""
        self.end_time = time.time()
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        logger.debug("Performance-Monitoring gestoppt")
    
    def _monitor_memory(self):
        """Überwacht Memory-Usage in separatem Thread."""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                memory_info = process.memory_info()
                self.memory_samples.append({
                    'timestamp': time.time(),
                    'rss': memory_info.rss,
                    'vms': memory_info.vms
                })
                time.sleep(0.1)  # Sample alle 100ms
            except Exception as e:
                logger.warning(f"Fehler beim Memory-Monitoring: {e}")
                break
    
    def get_metrics(self) -> Dict[str, Any]:
        """Gibt Performance-Metriken zurück."""
        if not self.start_time:
            return {}
        
        end_time = self.end_time or time.time()
        total_time = end_time - self.start_time
        
        metrics = {
            'total_time': total_time,
            'start_time': self.start_time,
            'end_time': end_time
        }
        
        if self.memory_samples:
            rss_values = [sample['rss'] for sample in self.memory_samples]
            metrics.update({
                'peak_memory_rss': max(rss_values),
                'avg_memory_rss': sum(rss_values) / len(rss_values),
                'memory_samples_count': len(self.memory_samples)
            })
        
        return metrics


@contextmanager
def performance_monitor():
    """Context Manager für Performance-Monitoring."""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    try:
        yield monitor
    finally:
        monitor.stop_monitoring()


class FileUtils:
    """Utility-Funktionen für Datei-Operationen."""
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """Berechnet Hash einer Datei."""
        hash_func = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Fehler beim Berechnen des Hash für {file_path}: {e}")
            return ""
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Sammelt Informationen über eine Datei."""
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'hash_md5': FileUtils.calculate_file_hash(file_path, 'md5'),
                'exists': True
            }
        except Exception as e:
            logger.error(f"Fehler beim Sammeln von Datei-Informationen für {file_path}: {e}")
            return {
                'path': file_path,
                'exists': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_backup(file_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
        """Erstellt ein Backup einer Datei."""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Datei für Backup nicht gefunden: {file_path}")
                return None
            
            if backup_dir is None:
                backup_dir = os.path.dirname(file_path)
            
            os.makedirs(backup_dir, exist_ok=True)
            
            # Erstelle Backup-Namen mit Zeitstempel
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup erstellt: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Backups für {file_path}: {e}")
            return None
    
    @staticmethod
    def safe_write_file(content: str, file_path: str, encoding: str = 'utf-8', 
                       create_backup: bool = True) -> bool:
        """Schreibt eine Datei sicher (mit optionalem Backup)."""
        try:
            # Erstelle Backup falls gewünscht und Datei existiert
            if create_backup and os.path.exists(file_path):
                FileUtils.create_backup(file_path)
            
            # Schreibe in temporäre Datei zuerst
            temp_path = file_path + '.tmp'
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Atomisches Verschieben
            shutil.move(temp_path, file_path)
            logger.debug(f"Datei sicher geschrieben: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim sicheren Schreiben von {file_path}: {e}")
            # Cleanup temporäre Datei
            temp_path = file_path + '.tmp'
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False
    
    @staticmethod
    def ensure_directory(dir_path: str) -> bool:
        """Stellt sicher, dass ein Verzeichnis existiert."""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Verzeichnisses {dir_path}: {e}")
            return False


class XMLUtils:
    """Utility-Funktionen für XML-Verarbeitung."""
    
    @staticmethod
    def strip_namespace(tag: str) -> str:
        """Entfernt Namespace-Präfix von einem XML-Tag."""
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    @staticmethod
    def get_namespace(tag: str) -> Optional[str]:
        """Extrahiert Namespace aus einem XML-Tag."""
        if '}' in tag:
            return tag.split('}', 0)[0].strip('{')
        return None
    
    @staticmethod
    def find_element_by_path(root: ET.Element, path: str) -> Optional[ET.Element]:
        """Findet ein Element über einen XPath-ähnlichen Pfad."""
        try:
            # Vereinfachte XPath-Implementierung
            parts = path.strip('/').split('/')
            current = root
            
            for part in parts:
                if '[' in part and ']' in part:
                    # Handle array notation like "AR-PACKAGE[0]"
                    tag_name = part.split('[')[0]
                    index = int(part.split('[')[1].split(']')[0])
                    elements = [child for child in current if XMLUtils.strip_namespace(child.tag) == tag_name]
                    if index < len(elements):
                        current = elements[index]
                    else:
                        return None
                else:
                    # Simple tag name
                    found = False
                    for child in current:
                        if XMLUtils.strip_namespace(child.tag) == part:
                            current = child
                            found = True
                            break
                    if not found:
                        return None
            
            return current
            
        except Exception as e:
            logger.error(f"Fehler beim Finden des Elements über Pfad {path}: {e}")
            return None
    
    @staticmethod
    def get_element_path(element: ET.Element, root: ET.Element) -> str:
        """Erstellt einen Pfad für ein Element relativ zur Wurzel."""
        try:
            path_parts = []
            current = element
            
            # Gehe den Baum nach oben bis zur Wurzel
            while current != root and current is not None:
                tag = XMLUtils.strip_namespace(current.tag)
                
                # Finde Index unter Geschwistern
                parent = current.getparent() if hasattr(current, 'getparent') else None
                if parent is not None:
                    siblings = [child for child in parent if XMLUtils.strip_namespace(child.tag) == tag]
                    if len(siblings) > 1:
                        index = siblings.index(current)
                        tag = f"{tag}[{index}]"
                
                path_parts.insert(0, tag)
                current = parent
            
            return '/' + '/'.join(path_parts) if path_parts else '/'
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Element-Pfads: {e}")
            return "/unknown"
    
    @staticmethod
    def pretty_print_xml(element: ET.Element, indent: str = "  ") -> None:
        """Formatiert XML für bessere Lesbarkeit (in-place)."""
        XMLUtils._indent_recursive(element, 0, indent)
    
    @staticmethod
    def _indent_recursive(elem: ET.Element, level: int, indent: str) -> None:
        """Rekursive Hilfsfunktion für XML-Formatierung."""
        i = "\n" + level * indent
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + indent
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                XMLUtils._indent_recursive(child, level + 1, indent)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    @staticmethod
    def validate_xml_structure(file_path: str) -> Tuple[bool, Optional[str]]:
        """Validiert die grundlegende XML-Struktur einer Datei."""
        try:
            ET.parse(file_path)
            return True, None
        except ET.ParseError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unerwarteter Fehler: {e}"


class StringUtils:
    """Utility-Funktionen für String-Verarbeitung."""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalisiert Whitespace in einem String."""
        return ' '.join(text.split())
    
    @staticmethod
    def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
        """Kürzt einen String auf maximale Länge."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Bereinigt einen Dateinamen von ungültigen Zeichen."""
        import re
        # Entferne/ersetze ungültige Zeichen
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Entferne führende/nachfolgende Punkte und Leerzeichen
        sanitized = sanitized.strip('. ')
        # Stelle sicher, dass der Name nicht leer ist
        return sanitized if sanitized else 'unnamed'
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formatiert Dateigröße in menschenlesbarer Form."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Formatiert Zeitdauer in menschenlesbarer Form."""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


class TempFileManager:
    """Verwaltet temporäre Dateien und Verzeichnisse."""
    
    def __init__(self):
        self.temp_files: List[str] = []
        self.temp_dirs: List[str] = []
    
    def create_temp_file(self, suffix: str = '', prefix: str = 'arxml_', 
                        content: Optional[str] = None) -> str:
        """Erstellt eine temporäre Datei."""
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(fd)
            
            if content:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.temp_files.append(temp_path)
            logger.debug(f"Temporäre Datei erstellt: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der temporären Datei: {e}")
            raise
    
    def create_temp_dir(self, prefix: str = 'arxml_') -> str:
        """Erstellt ein temporäres Verzeichnis."""
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
            self.temp_dirs.append(temp_dir)
            logger.debug(f"Temporäres Verzeichnis erstellt: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des temporären Verzeichnisses: {e}")
            raise
    
    def cleanup(self) -> None:
        """Räumt alle temporären Dateien und Verzeichnisse auf."""
        # Cleanup temporäre Dateien
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Temporäre Datei entfernt: {temp_file}")
            except Exception as e:
                logger.warning(f"Fehler beim Entfernen der temporären Datei {temp_file}: {e}")
        
        # Cleanup temporäre Verzeichnisse
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Temporäres Verzeichnis entfernt: {temp_dir}")
            except Exception as e:
                logger.warning(f"Fehler beim Entfernen des temporären Verzeichnisses {temp_dir}: {e}")
        
        self.temp_files.clear()
        self.temp_dirs.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Konfiguriert Logging für die Anwendung."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    
    # Reduziere Logging-Level für externe Bibliotheken
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
