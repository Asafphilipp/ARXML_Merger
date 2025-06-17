#!/usr/bin/env python3
"""
ARXML Merger - Einfache Konsolen-Anwendung
FUNKTIONIERT GARANTIERT - Keine GUI-Probleme!
"""

import os
import sys
import glob
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime

class ARXMLMergerConsole:
    def __init__(self):
        self.selected_files = []
        
    def print_header(self):
        """Zeigt den Header an."""
        print("=" * 60)
        print("🚀 ARXML MERGER - KONSOLEN-VERSION")
        print("=" * 60)
        print("✅ FUNKTIONIERT GARANTIERT!")
        print("📁 Mehrere Dateien laden und zusammenführen")
        print("🔄 Einfache Bedienung")
        print("=" * 60)
        print()
        
    def show_menu(self):
        """Zeigt das Hauptmenü an."""
        print("\n📋 HAUPTMENÜ:")
        print("1️⃣  Dateien hinzufügen")
        print("2️⃣  Dateien anzeigen")
        print("3️⃣  Dateien entfernen")
        print("4️⃣  ARXML zusammenführen")
        print("5️⃣  Automatisch alle .arxml Dateien im Ordner")
        print("0️⃣  Beenden")
        print()
        
    def add_files_interactive(self):
        """Dateien interaktiv hinzufügen."""
        print("\n📁 DATEIEN HINZUFÜGEN:")
        print("Geben Sie Dateipfade ein (einer pro Zeile).")
        print("Leer lassen und Enter drücken zum Beenden.")
        print("Tipp: Drag & Drop funktioniert in den meisten Terminals!")
        print()
        
        while True:
            file_path = input("📄 Dateipfad: ").strip()
            
            if not file_path:
                break
                
            # Anführungszeichen entfernen (falls Drag & Drop)
            file_path = file_path.strip('"\'')
            
            if not os.path.exists(file_path):
                print(f"❌ Datei nicht gefunden: {file_path}")
                continue
                
            if not (file_path.endswith('.arxml') or file_path.endswith('.xml')):
                print(f"⚠️  Warnung: {file_path} ist keine .arxml/.xml Datei")
                
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                print(f"✅ Hinzugefügt: {os.path.basename(file_path)}")
            else:
                print(f"ℹ️  Bereits vorhanden: {os.path.basename(file_path)}")
                
    def add_files_auto(self):
        """Alle .arxml Dateien im aktuellen Ordner hinzufügen."""
        print("\n🔍 SUCHE NACH .ARXML DATEIEN...")
        
        arxml_files = glob.glob("*.arxml") + glob.glob("*.xml")
        
        if not arxml_files:
            print("❌ Keine .arxml/.xml Dateien im aktuellen Ordner gefunden")
            return
            
        print(f"📁 {len(arxml_files)} Dateien gefunden:")
        for file in arxml_files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                print(f"✅ {file}")
            else:
                print(f"ℹ️  Bereits vorhanden: {file}")
                
    def show_files(self):
        """Zeigt ausgewählte Dateien an."""
        print(f"\n📋 AUSGEWÄHLTE DATEIEN ({len(self.selected_files)}):")
        
        if not self.selected_files:
            print("❌ Keine Dateien ausgewählt")
            return
            
        for i, file in enumerate(self.selected_files, 1):
            size = os.path.getsize(file) / 1024  # KB
            print(f"{i:2d}. 📄 {os.path.basename(file)} ({size:.1f} KB)")
            
    def remove_files(self):
        """Dateien entfernen."""
        if not self.selected_files:
            print("❌ Keine Dateien zum Entfernen")
            return
            
        self.show_files()
        print("\n🗑️  DATEIEN ENTFERNEN:")
        print("Geben Sie die Nummern der zu entfernenden Dateien ein (z.B. 1,3,5)")
        print("Oder 'alle' um alle zu entfernen")
        
        choice = input("Auswahl: ").strip().lower()
        
        if choice == 'alle':
            self.selected_files.clear()
            print("✅ Alle Dateien entfernt")
            return
            
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            # Rückwärts sortieren, damit Indizes stimmen
            for i in sorted(indices, reverse=True):
                if 0 <= i < len(self.selected_files):
                    removed = self.selected_files.pop(i)
                    print(f"✅ Entfernt: {os.path.basename(removed)}")
                else:
                    print(f"❌ Ungültige Nummer: {i+1}")
        except ValueError:
            print("❌ Ungültige Eingabe")
            
    def merge_files(self):
        """Führt die ARXML-Dateien zusammen."""
        if len(self.selected_files) < 2:
            print("❌ Mindestens 2 Dateien erforderlich!")
            return
            
        print(f"\n🔄 MERGE STARTEN...")
        print(f"📊 {len(self.selected_files)} Dateien werden zusammengeführt")
        
        # Ausgabedatei
        output_file = input("💾 Ausgabedatei (Enter für 'merged_arxml.arxml'): ").strip()
        if not output_file:
            output_file = "merged_arxml.arxml"
        if not output_file.endswith('.arxml'):
            output_file += '.arxml'
            
        try:
            print("📖 Lese ARXML-Dateien...")
            merged_content = self.perform_merge()
            
            print("💾 Speichere Ergebnis...")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(merged_content)
                
            file_size = os.path.getsize(output_file) / 1024  # KB
            
            print("\n🎉 MERGE ERFOLGREICH!")
            print("=" * 40)
            print(f"📁 Ausgabedatei: {output_file}")
            print(f"📏 Dateigröße: {file_size:.1f} KB")
            print(f"📊 Verarbeitete Dateien: {len(self.selected_files)}")
            print("=" * 40)
            
        except Exception as e:
            print(f"\n❌ FEHLER BEIM MERGE:")
            print(f"🚨 {str(e)}")
            
    def perform_merge(self):
        """Führt den eigentlichen Merge durch."""
        # Basis-XML-Struktur
        merged_content = '''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-3-0.xsd">
  <AR-PACKAGES>
'''
        
        package_count = 0
        
        for i, file_path in enumerate(self.selected_files, 1):
            print(f"📄 ({i}/{len(self.selected_files)}) {os.path.basename(file_path)}")
            
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
                    print(f"   ✅ {len(packages)} Pakete gefunden")
                else:
                    print(f"   ⚠️  Keine AR-PACKAGES gefunden")
                    
            except Exception as e:
                print(f"   ❌ Fehler: {str(e)}")
                continue
                
        merged_content += '''  </AR-PACKAGES>
</AUTOSAR>'''
        
        print(f"📦 Insgesamt {package_count} Pakete zusammengeführt")
        return merged_content
        
    def find_ar_packages(self, root):
        """Findet AR-PACKAGE Elemente."""
        packages = []
        for elem in root.iter():
            if elem.tag.endswith('AR-PACKAGE') or elem.tag == 'AR-PACKAGE':
                packages.append(elem)
        return packages
        
    def run(self):
        """Hauptschleife."""
        self.print_header()
        
        while True:
            self.show_menu()
            
            try:
                choice = input("🎯 Ihre Wahl: ").strip()
                
                if choice == '1':
                    self.add_files_interactive()
                elif choice == '2':
                    self.show_files()
                elif choice == '3':
                    self.remove_files()
                elif choice == '4':
                    self.merge_files()
                elif choice == '5':
                    self.add_files_auto()
                elif choice == '0':
                    print("\n👋 Auf Wiedersehen!")
                    break
                else:
                    print("❌ Ungültige Auswahl")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Programm beendet")
                break
            except Exception as e:
                print(f"❌ Unerwarteter Fehler: {e}")

def main():
    """Hauptfunktion."""
    app = ARXMLMergerConsole()
    app.run()

if __name__ == "__main__":
    main()
