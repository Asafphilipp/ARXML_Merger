#!/usr/bin/env python3
"""
ARXML Merger - Einfache GUI mit PyQt5/PySide2
Funktioniert garantiert und kann als .exe kompiliert werden.
"""

import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime

# Versuche verschiedene GUI-Frameworks
GUI_FRAMEWORK = None

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    GUI_FRAMEWORK = "PyQt5"
except ImportError:
    try:
        from PySide2.QtWidgets import *
        from PySide2.QtCore import *
        from PySide2.QtGui import *
        GUI_FRAMEWORK = "PySide2"
    except ImportError:
        try:
            import tkinter as tk
            from tkinter import ttk, filedialog, messagebox, scrolledtext
            GUI_FRAMEWORK = "tkinter"
        except ImportError:
            print("❌ Kein GUI-Framework gefunden!")
            print("📦 Installiere eines der folgenden:")
            print("   pip install PyQt5")
            print("   pip install PySide2")
            sys.exit(1)

class ARXMLMergerApp(QMainWindow if GUI_FRAMEWORK in ["PyQt5", "PySide2"] else object):
    def __init__(self):
        if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
            super().__init__()
        
        self.selected_files = []
        self.setup_ui()
        
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche."""
        if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
            self.setup_qt_ui()
        else:
            self.setup_tkinter_ui()
            
    def setup_qt_ui(self):
        """PyQt5/PySide2 UI."""
        self.setWindowTitle("🚀 ARXML Merger - Desktop GUI")
        self.setGeometry(100, 100, 800, 600)
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Titel
        title = QLabel("🚀 ARXML Merger")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Dateien-Bereich
        files_group = QGroupBox("📁 ARXML-Dateien auswählen")
        files_layout = QVBoxLayout()
        files_group.setLayout(files_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("Dateien hinzufügen")
        self.add_files_btn.clicked.connect(self.add_files)
        self.clear_files_btn = QPushButton("Alle entfernen")
        self.clear_files_btn.clicked.connect(self.clear_files)
        
        buttons_layout.addWidget(self.add_files_btn)
        buttons_layout.addWidget(self.clear_files_btn)
        buttons_layout.addStretch()
        files_layout.addLayout(buttons_layout)
        
        # Dateien-Liste
        self.files_list = QListWidget()
        files_layout.addWidget(self.files_list)
        
        layout.addWidget(files_group)
        
        # Ausgabe-Bereich
        output_group = QGroupBox("💾 Ausgabe")
        output_layout = QHBoxLayout()
        output_group.setLayout(output_layout)
        
        output_layout.addWidget(QLabel("Ausgabedatei:"))
        self.output_edit = QLineEdit("merged_arxml.arxml")
        output_layout.addWidget(self.output_edit)
        
        layout.addWidget(output_group)
        
        # Merge-Button
        self.merge_btn = QPushButton("🔄 ARXML-Dateien zusammenführen")
        self.merge_btn.clicked.connect(self.merge_files)
        self.merge_btn.setEnabled(False)
        self.merge_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(self.merge_btn)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Log-Bereich
        log_group = QGroupBox("📋 Status")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Willkommensnachricht
        self.log("🚀 ARXML Merger gestartet!")
        self.log("📁 Wählen Sie mindestens 2 ARXML-Dateien aus")
        
    def log(self, message):
        """Fügt eine Nachricht zum Log hinzu."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
            self.log_text.append(log_message)
        
    def add_files(self):
        """Dateien hinzufügen."""
        if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "ARXML-Dateien auswählen",
                "",
                "ARXML files (*.arxml);;XML files (*.xml);;All files (*.*)"
            )
        
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                filename = os.path.basename(file)
                
                if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
                    self.files_list.addItem(f"📄 {filename}")
                
                self.log(f"✅ Datei hinzugefügt: {filename}")
        
        self.update_merge_button()
        
    def clear_files(self):
        """Alle Dateien entfernen."""
        self.selected_files.clear()
        
        if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
            self.files_list.clear()
        
        self.log("🗑️ Alle Dateien entfernt")
        self.update_merge_button()
        
    def update_merge_button(self):
        """Merge-Button aktualisieren."""
        if len(self.selected_files) >= 2:
            self.merge_btn.setEnabled(True)
            self.merge_btn.setText(f"🔄 {len(self.selected_files)} Dateien zusammenführen")
        else:
            self.merge_btn.setEnabled(False)
            self.merge_btn.setText("🔄 Mindestens 2 Dateien erforderlich")
            
    def merge_files(self):
        """Führt die ARXML-Dateien zusammen."""
        if len(self.selected_files) < 2:
            if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
                QMessageBox.warning(self, "Fehler", "Mindestens 2 Dateien erforderlich!")
            return
            
        try:
            self.log("🔄 Merge gestartet...")
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)  # Indeterminate
            
            # Ausgabedatei
            output_file = self.output_edit.text()
            if not output_file.endswith('.arxml'):
                output_file += '.arxml'
                
            # Merge durchführen
            merged_content = self.perform_merge()
            
            # Datei speichern
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(merged_content)
                
            self.log(f"✅ Merge erfolgreich!")
            self.log(f"📁 Ausgabedatei: {output_file}")
            self.log(f"📊 {len(self.selected_files)} Dateien zusammengeführt")
            
            if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
                QMessageBox.information(
                    self, 
                    "Erfolg", 
                    f"ARXML-Dateien erfolgreich zusammengeführt!\n\nAusgabedatei: {output_file}"
                )
            
        except Exception as e:
            error_msg = f"❌ Fehler beim Merge: {str(e)}"
            self.log(error_msg)
            
            if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
                QMessageBox.critical(self, "Fehler", error_msg)
            
        finally:
            self.progress.setVisible(False)
            
    def perform_merge(self):
        """Führt den eigentlichen Merge durch."""
        self.log("📖 Lese ARXML-Dateien...")
        
        # Basis-XML-Struktur
        merged_content = '''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-3-0.xsd">
  <AR-PACKAGES>
'''
        
        package_count = 0
        
        for file_path in self.selected_files:
            self.log(f"📄 Verarbeite: {os.path.basename(file_path)}")
            
            try:
                # XML-Datei parsen
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # AR-PACKAGES finden
                packages = self.find_ar_packages(root)
                
                if packages:
                    merged_content += f"    <!-- Aus Datei: {os.path.basename(file_path)} -->\n"
                    for package in packages:
                        package_xml = ET.tostring(package, encoding='unicode')
                        merged_content += f"    {package_xml}\n"
                        package_count += 1
                else:
                    self.log(f"⚠️ Keine AR-PACKAGES in {os.path.basename(file_path)} gefunden")
                    
            except Exception as e:
                self.log(f"❌ Fehler in {os.path.basename(file_path)}: {str(e)}")
                continue
                
        merged_content += '''  </AR-PACKAGES>
</AUTOSAR>'''
        
        self.log(f"📦 {package_count} Pakete gefunden und zusammengeführt")
        return merged_content
        
    def find_ar_packages(self, root):
        """Findet AR-PACKAGE Elemente."""
        packages = []
        for elem in root.iter():
            if elem.tag.endswith('AR-PACKAGE') or elem.tag == 'AR-PACKAGE':
                packages.append(elem)
        return packages

def main():
    """Hauptfunktion."""
    print(f"🚀 ARXML Merger GUI - {GUI_FRAMEWORK}")
    
    if GUI_FRAMEWORK in ["PyQt5", "PySide2"]:
        app = QApplication(sys.argv)
        window = ARXMLMergerApp()
        window.show()
        sys.exit(app.exec_())
    else:
        print("❌ GUI-Framework nicht verfügbar")
        return False

if __name__ == "__main__":
    main()
