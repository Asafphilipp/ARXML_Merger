#!/usr/bin/env python3
"""
ARXML Merger - Desktop GUI Application
Einfache, funktionsfähige GUI für ARXML-Dateien zusammenführen.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime
import threading

class ARXMLMergerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 ARXML Merger - Desktop GUI")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Dateien-Liste
        self.selected_files = []
        
        # GUI erstellen
        self.create_widgets()
        
    def create_widgets(self):
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titel
        title_label = ttk.Label(main_frame, text="🚀 ARXML Merger", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Dateien auswählen
        files_frame = ttk.LabelFrame(main_frame, text="📁 ARXML-Dateien auswählen", padding="10")
        files_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(files_frame, text="Dateien hinzufügen", 
                  command=self.add_files).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(files_frame, text="Alle entfernen", 
                  command=self.clear_files).grid(row=0, column=1)
        
        # Dateien-Liste
        self.files_listbox = tk.Listbox(files_frame, height=8, width=80)
        self.files_listbox.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # Scrollbar für Liste
        scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_listbox.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Optionen
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Optionen", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(options_frame, text="Ausgabedatei:").grid(row=0, column=0, sticky=tk.W)
        self.output_var = tk.StringVar(value="merged_arxml.arxml")
        ttk.Entry(options_frame, textvariable=self.output_var, width=50).grid(row=0, column=1, padx=(10, 0))
        
        # Merge-Button
        self.merge_button = ttk.Button(main_frame, text="🔄 ARXML-Dateien zusammenführen", 
                                      command=self.start_merge, state='disabled')
        self.merge_button.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status/Log
        log_frame = ttk.LabelFrame(main_frame, text="📋 Status", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid-Konfiguration für Responsive Design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        files_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Willkommensnachricht
        self.log("🚀 ARXML Merger gestartet!")
        self.log("📁 Wählen Sie mindestens 2 ARXML-Dateien aus")
        
    def log(self, message):
        """Fügt eine Nachricht zum Log hinzu."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def add_files(self):
        """Dateien hinzufügen."""
        files = filedialog.askopenfilenames(
            title="ARXML-Dateien auswählen",
            filetypes=[
                ("ARXML files", "*.arxml"),
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                filename = os.path.basename(file)
                self.files_listbox.insert(tk.END, f"📄 {filename}")
                self.log(f"✅ Datei hinzugefügt: {filename}")
        
        self.update_merge_button()
        
    def clear_files(self):
        """Alle Dateien entfernen."""
        self.selected_files.clear()
        self.files_listbox.delete(0, tk.END)
        self.log("🗑️ Alle Dateien entfernt")
        self.update_merge_button()
        
    def update_merge_button(self):
        """Merge-Button aktivieren/deaktivieren."""
        if len(self.selected_files) >= 2:
            self.merge_button.config(state='normal')
            self.merge_button.config(text=f"🔄 {len(self.selected_files)} Dateien zusammenführen")
        else:
            self.merge_button.config(state='disabled')
            self.merge_button.config(text="🔄 Mindestens 2 Dateien erforderlich")
            
    def start_merge(self):
        """Startet den Merge-Prozess in einem separaten Thread."""
        if len(self.selected_files) < 2:
            messagebox.showerror("Fehler", "Mindestens 2 Dateien erforderlich!")
            return
            
        # UI während Merge deaktivieren
        self.merge_button.config(state='disabled')
        self.progress.start()
        
        # Merge in separatem Thread
        thread = threading.Thread(target=self.perform_merge)
        thread.daemon = True
        thread.start()
        
    def perform_merge(self):
        """Führt den eigentlichen Merge durch."""
        try:
            self.log("🔄 Merge gestartet...")
            
            # Ausgabedatei
            output_file = self.output_var.get()
            if not output_file.endswith('.arxml'):
                output_file += '.arxml'
                
            # Merge durchführen
            merged_content = self.merge_arxml_files(self.selected_files)
            
            # Datei speichern
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(merged_content)
                
            self.log(f"✅ Merge erfolgreich!")
            self.log(f"📁 Ausgabedatei: {output_file}")
            self.log(f"📊 {len(self.selected_files)} Dateien zusammengeführt")
            
            # Erfolg-Dialog
            self.root.after(0, lambda: messagebox.showinfo(
                "Erfolg", 
                f"ARXML-Dateien erfolgreich zusammengeführt!\n\nAusgabedatei: {output_file}"
            ))
            
        except Exception as e:
            error_msg = f"❌ Fehler beim Merge: {str(e)}"
            self.log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Fehler", error_msg))
            
        finally:
            # UI wieder aktivieren
            self.root.after(0, self.merge_finished)
            
    def merge_finished(self):
        """Wird nach dem Merge aufgerufen."""
        self.progress.stop()
        self.update_merge_button()
        
    def merge_arxml_files(self, file_paths):
        """Führt die ARXML-Dateien zusammen."""
        self.log("📖 Lese ARXML-Dateien...")
        
        # Basis-XML-Struktur
        merged_content = '''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-3-0.xsd">
  <AR-PACKAGES>
'''
        
        package_count = 0
        
        for i, file_path in enumerate(file_paths):
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
        """Findet AR-PACKAGE Elemente in einem XML-Baum."""
        packages = []
        
        # Direkte AR-PACKAGE Elemente
        for elem in root.iter():
            if elem.tag.endswith('AR-PACKAGE') or elem.tag == 'AR-PACKAGE':
                packages.append(elem)
                
        return packages

def main():
    """Hauptfunktion."""
    # Tkinter Root erstellen
    root = tk.Tk()
    
    # GUI erstellen
    app = ARXMLMergerGUI(root)
    
    # Programm starten
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Programm beendet.")

if __name__ == "__main__":
    main()
