# 📖 ARXML Merger - Benutzeranleitung

## ❌ **Häufiges Problem: "Funktioniert nicht in der main Branch"**

Das Problem ist **NICHT** die main Branch - das Problem liegt in der **falschen Verwendung** der HTML-Dateien!

### 🔍 **Was passiert bei falscher Verwendung:**
1. HTML-Datei wird direkt von GitHub geöffnet
2. GitHub zeigt den Code oder öffnet die Datei im Browser
3. **Browser blockiert JavaScript** wegen Sicherheitsbeschränkungen
4. ❌ **Ergebnis**: "Funktioniert nicht!"

## ✅ **SO GEHT ES RICHTIG:**

### **Methode 1: HTML-Datei richtig herunterladen**

1. **Geht zu**: https://raw.githubusercontent.com/Asafphilipp/ARXML_Merger/main/arxml_merger_working.html
2. **Rechtsklick** → **"Speichern unter"** (NICHT einfach klicken!)
3. **Speichert die Datei** auf eurem Desktop oder in einem Ordner
4. **Doppelklick** auf die **gespeicherte Datei**
5. ✅ **Jetzt funktioniert es!**

### **Methode 2: Komplettes Paket (Empfohlen)**

1. **Download**: https://github.com/Asafphilipp/ARXML_Merger/archive/refs/heads/main.zip
2. **ZIP entpacken**
3. **Doppelklick** auf `START.bat`
4. ✅ **Browser öffnet sich automatisch**

### **Methode 3: Für Faule (Ein-Klick-Lösung)**

1. **Geht zu**: https://asafphilipp.github.io/ARXML_Merger/download.html
2. **Klickt** auf "HTML-Version herunterladen"
3. **Speichert** die Datei lokal
4. **Doppelklick** auf die gespeicherte Datei
5. ✅ **Fertig!**

## 🤔 **Warum gibt es mehrere Branches?**

- **main**: Stabile Hauptversion
- **professional-arxml-merger**: Für erweiterte Features
- **fix-standalone-and-reorganize**: Für Bugfixes

**Alle sind momentan identisch** - es gibt also KEINEN Unterschied!

## 🔧 **Technische Erklärung (für Interessierte):**

Das Problem sind **Browser-Sicherheitsbeschränkungen**:
- HTML-Dateien von GitHub können nicht direkt JavaScript ausführen
- **CORS-Policy** blockiert Datei-Zugriffe
- **Same-Origin-Policy** verhindert lokale Datei-Operationen

**Lösung**: Datei muss **lokal gespeichert** werden, dann funktioniert alles!

## 📞 **Immer noch Probleme?**

1. **Überprüft**: Habt ihr die Datei wirklich **lokal gespeichert**?
2. **Browser**: Verwendet Chrome, Firefox oder Edge (nicht Internet Explorer!)
3. **Antivirus**: Manchmal blockiert Antivirus-Software JavaScript
4. **Firewall**: Corporate Firewalls können lokale HTML-Dateien blockieren

## 🎯 **Zusammenfassung für Eilige:**

```
❌ FALSCH: GitHub-Link direkt im Browser öffnen
✅ RICHTIG: Datei herunterladen → lokal speichern → doppelklicken
```

**Die main Branch funktioniert perfekt - ihr müsst nur richtig vorgehen!** 🚀
