# 🔧 ARXML Merger - Troubleshooting

## 🛡️ **"Der Computer wurde durch Windows geschützt"**

### ❌ **Problem:**
Beim Ausführen von `ARXML_Merger.exe` erscheint eine Windows-Schutzwarnung.

### ✅ **Sofort-Lösung:**
1. **Klicken Sie auf "Weitere Informationen"**
2. **Klicken Sie auf "Trotzdem ausführen"**
3. ✅ Das Programm startet normal

### 🔄 **Alternative (KEINE Warnung):**
- **Doppelklick auf `START_PYTHON.bat`**
- Identische Funktionalität, keine Warnung

### 💡 **Warum passiert das?**
- Windows Defender schützt vor unbekannten .exe-Dateien
- Die Datei ist nicht digital signiert (kostet Geld)
- **Das ist normal und harmlos!**

📖 **Ausführliche Anleitung**: [WINDOWS_SCHUTZ_LÖSUNG.md](WINDOWS_SCHUTZ_LÖSUNG.md)

---

## 🚨 **"Es funktioniert nicht in der main Branch!"**

### ❌ **Häufigster Fehler:**
Ihr versucht die HTML-Dateien **direkt von GitHub** zu öffnen!

### ✅ **Lösung:**
1. **Datei herunterladen** (Rechtsklick → "Speichern unter")
2. **Lokal speichern** (Desktop/Ordner)
3. **Doppelklick** auf gespeicherte Datei

---

## 🔍 **Weitere häufige Probleme:**

### **Problem: "Dateien können nicht geladen werden"**
**Ursache:** Browser-Sicherheitsbeschränkungen
**Lösung:** 
- HTML-Datei muss **lokal gespeichert** sein
- Nicht direkt von GitHub öffnen

### **Problem: "Download funktioniert nicht"**
**Ursache:** Pop-up-Blocker oder Antivirus
**Lösung:**
- Pop-up-Blocker deaktivieren
- Antivirus-Ausnahme hinzufügen
- Anderen Browser versuchen

### **Problem: "JavaScript-Fehler"**
**Ursache:** Veralteter Browser
**Lösung:**
- Chrome 90+, Firefox 88+, Edge 90+ verwenden
- Browser aktualisieren

### **Problem: "Merge-Ergebnis ist leer"**
**Ursache:** Ungültige ARXML-Dateien
**Lösung:**
- Dateien auf Gültigkeit prüfen
- Nur .arxml oder .xml Dateien verwenden

---

## 🎯 **Schnelle Lösungen:**

### **Für Ungeduldige:**
```
1. https://github.com/Asafphilipp/ARXML_Merger/archive/refs/heads/main.zip
2. ZIP entpacken
3. START.bat doppelklicken
4. Fertig!
```

### **Für Browser-Nutzer:**
```
1. Rechtsklick auf HTML-Download-Link
2. "Speichern unter" wählen
3. Datei auf Desktop speichern
4. Doppelklick auf gespeicherte Datei
```

---

## 📞 **Immer noch Probleme?**

1. **Browser-Konsole öffnen** (F12) und Fehlermeldungen prüfen
2. **Andere Browser** versuchen
3. **Firewall/Antivirus** temporär deaktivieren
4. **Issue auf GitHub** erstellen mit Details

---

## ✅ **Erfolgskontrolle:**

**Es funktioniert, wenn:**
- ✅ HTML-Datei öffnet sich im Browser
- ✅ "Dateien auswählen" Button ist sichtbar
- ✅ Dateien können hochgeladen werden
- ✅ "Zusammenführen" Button wird aktiv
- ✅ Download startet automatisch

**Es funktioniert NICHT, wenn:**
- ❌ Nur Code/Text wird angezeigt
- ❌ "Datei nicht gefunden" Fehler
- ❌ JavaScript-Fehler in Konsole
- ❌ Buttons reagieren nicht

---

## 🔄 **Branch-Verwirrung aufgeklärt:**

**Alle Branches sind identisch!**
- `main` = `professional-arxml-merger` = `fix-standalone-and-reorganize`
- Es gibt **keinen Unterschied** zwischen den Branches
- Das Problem liegt **nicht** an der Branch-Wahl
- Das Problem liegt an der **falschen Verwendung**

**Die main Branch funktioniert perfekt - man muss nur richtig vorgehen!** 🚀

📖 **Ausführliche Anleitung**: [BENUTZERANLEITUNG.md](BENUTZERANLEITUNG.md)
