"""
Moderne Web-Interface für ARXML-Merger.

Dieses Modul implementiert eine benutzerfreundliche HTML5-Weboberfläche
mit Drag & Drop, Live-Feedback und erweiterten Konfigurationsoptionen.
"""

import http.server
import socketserver
import json
import tempfile
import os
import shutil
import threading
import time
from typing import Dict, List, Any, Optional
from urllib.parse import parse_qs, urlparse
import logging
from pathlib import Path

from arxml_merger_engine import ARXMLMergerEngine, MergeStrategy
from arxml_validator import ARXMLValidator, ValidationLevel
from conflict_resolver import ConflictResolver, ResolutionStrategy
from arxml_reporter import ReportGenerator, PerformanceMetrics

logger = logging.getLogger(__name__)


class MergeSession:
    """Repräsentiert eine Merge-Session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.uploaded_files: List[str] = []
        self.temp_dir = tempfile.mkdtemp(prefix=f"arxml_merge_{session_id}_")
        self.status = "initialized"
        self.progress = 0
        self.result = None
        self.error_message = None
        self.warnings: List[str] = []
        self.created_at = time.time()

    def cleanup(self):
        """Räumt temporäre Dateien auf."""
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Fehler beim Aufräumen der Session {self.session_id}: {e}")


class SessionManager:
    """Verwaltet aktive Merge-Sessions."""

    def __init__(self):
        self.sessions: Dict[str, MergeSession] = {}
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_sessions, daemon=True)
        self.cleanup_thread.start()

    def create_session(self) -> str:
        """Erstellt eine neue Session."""
        import uuid
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = MergeSession(session_id)
        logger.info(f"Neue Session erstellt: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[MergeSession]:
        """Gibt eine Session zurück."""
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str) -> None:
        """Entfernt eine Session."""
        if session_id in self.sessions:
            self.sessions[session_id].cleanup()
            del self.sessions[session_id]
            logger.info(f"Session entfernt: {session_id}")

    def _cleanup_old_sessions(self):
        """Räumt alte Sessions auf (läuft in separatem Thread)."""
        while True:
            try:
                current_time = time.time()
                old_sessions = []

                for session_id, session in self.sessions.items():
                    # Sessions älter als 1 Stunde entfernen
                    if current_time - session.created_at > 3600:
                        old_sessions.append(session_id)

                for session_id in old_sessions:
                    self.remove_session(session_id)

                time.sleep(300)  # Alle 5 Minuten prüfen

            except Exception as e:
                logger.error(f"Fehler beim Session-Cleanup: {e}")
                time.sleep(60)


class ARXMLMergeHandler(http.server.BaseHTTPRequestHandler):
    """HTTP-Handler für ARXML-Merge-Requests."""

    def __init__(self, *args, session_manager: SessionManager, **kwargs):
        self.session_manager = session_manager
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Behandelt GET-Requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/':
            self._serve_main_page()
        elif path == '/api/session':
            self._create_session()
        elif path.startswith('/api/session/'):
            session_id = path.split('/')[-1]
            self._get_session_status(session_id)
        elif path.startswith('/download/'):
            self._serve_download(path)
        elif path.startswith('/static/'):
            self._serve_static_file(path)
        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        """Behandelt POST-Requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/upload':
            self._handle_file_upload()
        elif path == '/api/merge':
            self._handle_merge_request()
        else:
            self._send_error(404, "Not Found")

    def _serve_main_page(self):
        """Serviert die Haupt-HTML-Seite."""
        html_content = self._get_main_html()
        self._send_response(200, html_content, 'text/html')

    def _create_session(self):
        """Erstellt eine neue Session."""
        session_id = self.session_manager.create_session()
        response = {'session_id': session_id}
        self._send_json_response(200, response)

    def _get_session_status(self, session_id: str):
        """Gibt den Status einer Session zurück."""
        session = self.session_manager.get_session(session_id)
        if not session:
            self._send_error(404, "Session not found")
            return

        response = {
            'session_id': session_id,
            'status': session.status,
            'progress': session.progress,
            'uploaded_files': len(session.uploaded_files),
            'warnings': session.warnings,
            'error_message': session.error_message
        }
        self._send_json_response(200, response)

    def _handle_file_upload(self):
        """Behandelt Datei-Uploads."""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self._send_error(400, "Invalid content type")
                return

            # Vereinfachte Implementierung - in Produktion sollte eine robuste
            # multipart/form-data Parser verwendet werden
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, "No content")
                return

            # Für diese Demo nehmen wir an, dass die Session-ID im Header steht
            session_id = self.headers.get('X-Session-ID')
            if not session_id:
                self._send_error(400, "No session ID")
                return

            session = self.session_manager.get_session(session_id)
            if not session:
                self._send_error(404, "Session not found")
                return

            # Lese und speichere Datei (vereinfacht)
            post_data = self.rfile.read(content_length)

            # In einer echten Implementierung würde hier ein multipart-Parser verwendet
            # Für Demo-Zwecke nehmen wir an, dass die Datei direkt übertragen wird
            file_path = os.path.join(session.temp_dir, f"upload_{len(session.uploaded_files)}.arxml")
            with open(file_path, 'wb') as f:
                f.write(post_data)

            session.uploaded_files.append(file_path)

            response = {
                'success': True,
                'file_count': len(session.uploaded_files)
            }
            self._send_json_response(200, response)

        except Exception as e:
            logger.error(f"Fehler beim Datei-Upload: {e}")
            self._send_error(500, str(e))

    def _handle_merge_request(self):
        """Behandelt Merge-Anfragen."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))

            session_id = request_data.get('session_id')
            if not session_id:
                self._send_error(400, "No session ID")
                return

            session = self.session_manager.get_session(session_id)
            if not session:
                self._send_error(404, "Session not found")
                return

            if not session.uploaded_files:
                self._send_error(400, "No files uploaded")
                return

            # Starte Merge in separatem Thread
            merge_config = {
                'strategy': request_data.get('strategy', 'conservative'),
                'validation_level': request_data.get('validation_level', 'structure'),
                'generate_reports': request_data.get('generate_reports', True)
            }

            thread = threading.Thread(
                target=self._perform_merge,
                args=(session, merge_config)
            )
            thread.start()

            response = {'success': True, 'message': 'Merge started'}
            self._send_json_response(200, response)

        except Exception as e:
            logger.error(f"Fehler beim Merge-Request: {e}")
            self._send_error(500, str(e))

    def _perform_merge(self, session: MergeSession, config: Dict[str, Any]):
        """Führt den Merge-Vorgang durch (läuft in separatem Thread)."""
        try:
            session.status = "merging"
            session.progress = 10

            # Initialisiere Merger
            strategy = MergeStrategy(config['strategy'])
            merger = ARXMLMergerEngine(strategy)

            session.progress = 20

            # Führe Merge durch
            output_file = os.path.join(session.temp_dir, "merged.arxml")
            result = merger.merge_files(session.uploaded_files, output_file)

            session.progress = 80

            if result.success:
                session.status = "completed"
                session.result = {
                    'output_file': output_file,
                    'preserved_signals': len(result.preserved_signals),
                    'conflicts': len(result.conflicts),
                    'processing_time': result.processing_time
                }

                # Generiere Berichte falls gewünscht
                if config.get('generate_reports', True):
                    self._generate_reports(session, result)

            else:
                session.status = "failed"
                session.error_message = "Merge failed"
                session.warnings.extend(result.errors)

            session.progress = 100

        except Exception as e:
            logger.error(f"Fehler beim Merge: {e}")
            session.status = "failed"
            session.error_message = str(e)
            session.progress = 100

    def _generate_reports(self, session: MergeSession, merge_result):
        """Generiert Berichte für das Merge-Ergebnis."""
        try:
            reporter = ReportGenerator()

            # Erstelle Performance-Metriken
            performance = PerformanceMetrics(
                total_processing_time=merge_result.processing_time,
                parsing_time=0,  # TODO: Implementiere detaillierte Zeitmessung
                merging_time=merge_result.processing_time,
                validation_time=0,
                writing_time=0,
                memory_peak_usage=merge_result.memory_usage,
                input_files_count=len(session.uploaded_files),
                total_input_size=sum(os.path.getsize(f) for f in session.uploaded_files),
                output_size=os.path.getsize(session.result['output_file']) if session.result else 0,
                elements_processed=0
            )

            # Generiere Bericht
            report = reporter.generate_report(
                input_files=session.uploaded_files,
                output_file=session.result['output_file'],
                merge_strategy="conservative",  # TODO: Verwende tatsächliche Strategie
                success=merge_result.success,
                conflicts=merge_result.conflicts,
                performance=performance,
                warnings=merge_result.warnings,
                errors=merge_result.errors,
                validation_results={}
            )

            # Speichere Berichte
            report_dir = os.path.join(session.temp_dir, "reports")
            os.makedirs(report_dir, exist_ok=True)

            reporter.save_report_json(report, os.path.join(report_dir, "merge_report.json"))
            reporter.generate_html_report(report, os.path.join(report_dir, "merge_report.html"))
            reporter.save_signal_inventory_csv(report, os.path.join(report_dir, "signal_inventory.csv"))

            if session.result:
                session.result['reports_available'] = True
                session.result['report_dir'] = report_dir

        except Exception as e:
            logger.error(f"Fehler beim Generieren der Berichte: {e}")
            session.warnings.append(f"Berichte konnten nicht erstellt werden: {e}")

    def _serve_download(self, path: str):
        """Serviert Download-Dateien."""
        # Implementierung für Datei-Downloads
        self._send_error(501, "Download not implemented yet")

    def _serve_static_file(self, path: str):
        """Serviert statische Dateien."""
        # Implementierung für statische Dateien (CSS, JS, etc.)
        self._send_error(404, "Static file not found")

    def _send_response(self, status_code: int, content: str, content_type: str = 'text/plain'):
        """Sendet eine HTTP-Antwort."""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Sendet eine JSON-Antwort."""
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        self._send_response(status_code, json_content, 'application/json')

    def _send_error(self, status_code: int, message: str):
        """Sendet eine Fehler-Antwort."""
        error_data = {'error': message, 'status': status_code}
        self._send_json_response(status_code, error_data)

    def _get_main_html(self) -> str:
        """Erstellt die Haupt-HTML-Seite."""
        return """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARXML Merger - Professional AUTOSAR Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .main-content {
            padding: 40px;
        }

        .upload-section {
            background: #f8f9fa;
            border: 3px dashed #dee2e6;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }

        .upload-section.dragover {
            border-color: #007bff;
            background: #e3f2fd;
        }

        .upload-icon {
            font-size: 4em;
            color: #6c757d;
            margin-bottom: 20px;
        }

        .upload-text {
            font-size: 1.2em;
            color: #6c757d;
            margin-bottom: 20px;
        }

        .file-input {
            display: none;
        }

        .upload-btn {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,123,255,0.3);
        }

        .config-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }

        .config-card {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #dee2e6;
        }

        .config-card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #495057;
        }

        .form-group select,
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            font-size: 1em;
        }

        .file-list {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            margin-bottom: 30px;
            max-height: 300px;
            overflow-y: auto;
        }

        .file-item {
            padding: 15px 20px;
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .file-item:last-child {
            border-bottom: none;
        }

        .file-name {
            font-weight: 500;
            color: #2c3e50;
        }

        .file-size {
            color: #6c757d;
            font-size: 0.9em;
        }

        .remove-file {
            background: #dc3545;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
        }

        .merge-btn {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 20px 40px;
            border-radius: 25px;
            font-size: 1.2em;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }

        .merge-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(40,167,69,0.3);
        }

        .merge-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .progress-section {
            display: none;
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #007bff, #28a745);
            width: 0%;
            transition: width 0.3s ease;
        }

        .progress-text {
            text-align: center;
            font-weight: 600;
            color: #495057;
        }

        .result-section {
            display: none;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
        }

        .result-section.error {
            background: #f8d7da;
            border-color: #f5c6cb;
        }

        .result-title {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #155724;
        }

        .result-section.error .result-title {
            color: #721c24;
        }

        .download-links {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .download-btn {
            background: #007bff;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            transition: background 0.3s ease;
        }

        .download-btn:hover {
            background: #0056b3;
        }

        .warning-list {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
        }

        .warning-item {
            color: #856404;
            margin-bottom: 5px;
        }

        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 10px;
            }

            .main-content {
                padding: 20px;
            }

            .config-section {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .download-links {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ARXML Merger</h1>
            <p>Professionelles Tool für AUTOSAR ARXML-Dateien</p>
        </div>

        <div class="main-content">
            <!-- Upload Section -->
            <div class="upload-section" id="uploadSection">
                <div class="upload-icon">📁</div>
                <div class="upload-text">
                    Ziehen Sie ARXML-Dateien hierher oder klicken Sie zum Auswählen
                </div>
                <input type="file" id="fileInput" class="file-input" multiple accept=".arxml,.xml">
                <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                    Dateien auswählen
                </button>
            </div>

            <!-- File List -->
            <div class="file-list" id="fileList" style="display: none;">
                <div style="padding: 15px 20px; background: #f8f9fa; font-weight: 600; color: #2c3e50;">
                    Ausgewählte Dateien
                </div>
            </div>

            <!-- Configuration -->
            <div class="config-section">
                <div class="config-card">
                    <h3>🔧 Merge-Konfiguration</h3>
                    <div class="form-group">
                        <label for="mergeStrategy">Merge-Strategie:</label>
                        <select id="mergeStrategy">
                            <option value="conservative">Conservative (Erste Datei hat Priorität)</option>
                            <option value="latest_wins">Latest Wins (Letzte Datei gewinnt)</option>
                            <option value="interactive">Interactive (Benutzer-Entscheidung)</option>
                            <option value="rule_based">Rule-Based (Regelbasiert)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="validationLevel">Validierungsstufe:</label>
                        <select id="validationLevel">
                            <option value="basic">Basic (XML-Wohlgeformtheit)</option>
                            <option value="structure" selected>Structure (AUTOSAR-Struktur)</option>
                            <option value="schema">Schema (Vollständige Schema-Validierung)</option>
                            <option value="semantic">Semantic (Semantische Validierung)</option>
                        </select>
                    </div>
                </div>

                <div class="config-card">
                    <h3>📊 Ausgabe-Optionen</h3>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="generateReports" checked>
                            Detaillierte Berichte generieren
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="prettyPrint" checked>
                            XML formatiert ausgeben
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="validateOutput" checked>
                            Ausgabe validieren
                        </label>
                    </div>
                </div>
            </div>

            <!-- Merge Button -->
            <button class="merge-btn" id="mergeBtn" onclick="startMerge()" disabled>
                🔄 ARXML-Dateien zusammenführen
            </button>

            <!-- Progress Section -->
            <div class="progress-section" id="progressSection">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-text" id="progressText">Initialisierung...</div>
            </div>

            <!-- Result Section -->
            <div class="result-section" id="resultSection">
                <div class="result-title" id="resultTitle">Merge erfolgreich abgeschlossen!</div>
                <div id="resultContent"></div>
                <div class="download-links" id="downloadLinks"></div>
                <div class="warning-list" id="warningList" style="display: none;"></div>
            </div>
        </div>
    </div>

    <script>
        let currentSession = null;
        let uploadedFiles = [];
        let pollInterval = null;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initializeSession();
            setupEventListeners();
        });

        function initializeSession() {
            fetch('/api/session')
                .then(response => response.json())
                .then(data => {
                    currentSession = data.session_id;
                    console.log('Session initialized:', currentSession);
                })
                .catch(error => {
                    console.error('Failed to initialize session:', error);
                    alert('Fehler beim Initialisieren der Session');
                });
        }

        function setupEventListeners() {
            const uploadSection = document.getElementById('uploadSection');
            const fileInput = document.getElementById('fileInput');

            // Drag and Drop
            uploadSection.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadSection.classList.add('dragover');
            });

            uploadSection.addEventListener('dragleave', function(e) {
                e.preventDefault();
                uploadSection.classList.remove('dragover');
            });

            uploadSection.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadSection.classList.remove('dragover');
                handleFiles(e.dataTransfer.files);
            });

            // File Input
            fileInput.addEventListener('change', function(e) {
                handleFiles(e.target.files);
            });
        }

        function handleFiles(files) {
            for (let file of files) {
                if (file.name.toLowerCase().endsWith('.arxml') || file.name.toLowerCase().endsWith('.xml')) {
                    uploadedFiles.push(file);
                } else {
                    alert(`Datei ${file.name} wird übersprungen (nur .arxml/.xml Dateien unterstützt)`);
                }
            }
            updateFileList();
            updateMergeButton();
        }

        function updateFileList() {
            const fileList = document.getElementById('fileList');

            if (uploadedFiles.length === 0) {
                fileList.style.display = 'none';
                return;
            }

            fileList.style.display = 'block';

            // Clear existing items (except header)
            const items = fileList.querySelectorAll('.file-item');
            items.forEach(item => item.remove());

            uploadedFiles.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatFileSize(file.size)}</div>
                    </div>
                    <button class="remove-file" onclick="removeFile(${index})">Entfernen</button>
                `;
                fileList.appendChild(fileItem);
            });
        }

        function removeFile(index) {
            uploadedFiles.splice(index, 1);
            updateFileList();
            updateMergeButton();
        }

        function updateMergeButton() {
            const mergeBtn = document.getElementById('mergeBtn');
            mergeBtn.disabled = uploadedFiles.length < 2;

            if (uploadedFiles.length < 2) {
                mergeBtn.textContent = '🔄 Mindestens 2 Dateien erforderlich';
            } else {
                mergeBtn.textContent = `🔄 ${uploadedFiles.length} ARXML-Dateien zusammenführen`;
            }
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        function startMerge() {
            if (!currentSession || uploadedFiles.length < 2) {
                alert('Session nicht initialisiert oder zu wenige Dateien');
                return;
            }

            // Show progress section
            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultSection').style.display = 'none';
            document.getElementById('mergeBtn').disabled = true;

            // Upload files first (simplified - in real implementation would use proper multipart upload)
            uploadFiles().then(() => {
                // Start merge
                const config = {
                    session_id: currentSession,
                    strategy: document.getElementById('mergeStrategy').value,
                    validation_level: document.getElementById('validationLevel').value,
                    generate_reports: document.getElementById('generateReports').checked,
                    pretty_print: document.getElementById('prettyPrint').checked,
                    validate_output: document.getElementById('validateOutput').checked
                };

                fetch('/api/merge', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(config)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        startPolling();
                    } else {
                        showError('Fehler beim Starten des Merge-Vorgangs');
                    }
                })
                .catch(error => {
                    console.error('Merge request failed:', error);
                    showError('Netzwerkfehler beim Merge-Request');
                });
            });
        }

        function uploadFiles() {
            // Simplified upload - in real implementation would upload each file properly
            return Promise.resolve();
        }

        function startPolling() {
            pollInterval = setInterval(checkProgress, 1000);
        }

        function checkProgress() {
            if (!currentSession) return;

            fetch(`/api/session/${currentSession}`)
                .then(response => response.json())
                .then(data => {
                    updateProgress(data.progress, data.status);

                    if (data.status === 'completed') {
                        clearInterval(pollInterval);
                        showSuccess(data);
                    } else if (data.status === 'failed') {
                        clearInterval(pollInterval);
                        showError(data.error_message || 'Merge fehlgeschlagen');
                    }
                })
                .catch(error => {
                    console.error('Progress check failed:', error);
                });
        }

        function updateProgress(progress, status) {
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');

            progressFill.style.width = progress + '%';

            const statusTexts = {
                'initialized': 'Initialisiert...',
                'merging': 'Zusammenführung läuft...',
                'completed': 'Abgeschlossen!',
                'failed': 'Fehlgeschlagen!'
            };

            progressText.textContent = statusTexts[status] || `${progress}%`;
        }

        function showSuccess(data) {
            const resultSection = document.getElementById('resultSection');
            const resultTitle = document.getElementById('resultTitle');
            const resultContent = document.getElementById('resultContent');
            const downloadLinks = document.getElementById('downloadLinks');

            resultSection.className = 'result-section';
            resultSection.style.display = 'block';
            resultTitle.textContent = 'Merge erfolgreich abgeschlossen!';

            resultContent.innerHTML = `
                <p><strong>📁 Verarbeitete Dateien:</strong> ${uploadedFiles.length}</p>
                <p><strong>⚡ Verarbeitungszeit:</strong> ${data.processing_time || 'N/A'} Sekunden</p>
                <p><strong>🔧 Konflikte aufgelöst:</strong> ${data.conflicts || 0}</p>
                <p><strong>📡 Signale erhalten:</strong> ${data.preserved_signals || 'N/A'}</p>
            `;

            downloadLinks.innerHTML = `
                <a href="/download/merged.arxml" class="download-btn">📥 Merged ARXML herunterladen</a>
                <a href="/download/reports/merge_report.html" class="download-btn">📊 HTML-Bericht anzeigen</a>
                <a href="/download/reports/signal_inventory.csv" class="download-btn">📋 Signal-Inventar (CSV)</a>
                <a href="/download/reports/merge_report.json" class="download-btn">🔧 JSON-Bericht</a>
            `;

            if (data.warnings && data.warnings.length > 0) {
                const warningList = document.getElementById('warningList');
                warningList.style.display = 'block';
                warningList.innerHTML = '<strong>⚠️ Warnungen:</strong><br>' +
                    data.warnings.map(w => `<div class="warning-item">• ${w}</div>`).join('');
            }

            document.getElementById('progressSection').style.display = 'none';
            document.getElementById('mergeBtn').disabled = false;
        }

        function showError(message) {
            const resultSection = document.getElementById('resultSection');
            const resultTitle = document.getElementById('resultTitle');
            const resultContent = document.getElementById('resultContent');

            resultSection.className = 'result-section error';
            resultSection.style.display = 'block';
            resultTitle.textContent = 'Merge fehlgeschlagen!';
            resultContent.innerHTML = `<p><strong>❌ Fehler:</strong> ${message}</p>`;

            document.getElementById('progressSection').style.display = 'none';
            document.getElementById('mergeBtn').disabled = false;
        }
    </script>
</body>
</html>
        """


class ARXMLWebServer:
    """Hauptklasse für den ARXML-Merger Web-Server."""

    def __init__(self, port: int = 8000, host: str = 'localhost'):
        self.port = port
        self.host = host
        self.session_manager = SessionManager()

    def start(self):
        """Startet den Web-Server."""
        def handler_factory(*args, **kwargs):
            return ARXMLMergeHandler(*args, session_manager=self.session_manager, **kwargs)

        with socketserver.TCPServer((self.host, self.port), handler_factory) as httpd:
            print(f"🚀 ARXML Merger Web-Interface gestartet!")
            print(f"📡 Server läuft auf: http://{self.host}:{self.port}")
            print(f"🌐 Öffnen Sie die URL in Ihrem Browser")
            print(f"⏹️  Drücken Sie Ctrl+C zum Beenden")

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print(f"\n🛑 Server wird beendet...")
                self.session_manager._cleanup_old_sessions()
                print(f"✅ Server erfolgreich beendet")


def main():
    """Hauptfunktion für den Web-Server."""
    import argparse

    parser = argparse.ArgumentParser(
        description='ARXML Merger Web-Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python web_interface.py                    # Standard-Port 8000
  python web_interface.py --port 9000       # Benutzerdefinierter Port
  python web_interface.py --host 0.0.0.0    # Alle Interfaces
        """
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port für den Web-Server (Standard: 8000)'
    )

    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host-Adresse (Standard: localhost, 0.0.0.0 für alle Interfaces)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debug-Modus aktivieren'
    )

    args = parser.parse_args()

    # Konfiguriere Logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Starte Server
    server = ARXMLWebServer(port=args.port, host=args.host)
    server.start()


if __name__ == '__main__':
    main()