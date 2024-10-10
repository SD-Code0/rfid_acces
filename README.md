## 1. Projektbeschreibung

Dieses Projekt ist ein RFID-Zugangskontrollsystem, das verschiedene Technologien wie Python, SQLite, Flask und Arduino verwendet. Es ermöglicht die Verwaltung von Benutzern und deren Zugriffsrechten sowie die Protokollierung von Zugriffsereignissen.

## 2. Installation

1. **Repository klonen**:
   ```sh
   git clone https://github.com/dein-benutzername/dein-projekt.git
   cd dein-projekt

2. **Abhängigkeiten installieren:**:
   ```sh
    pip install -r requirements.txt

3. **Arduino-Sketch hochladen**:

    Öffne die Datei RFIDauslesung.ino in der Arduino IDE.
    ## Konfiguration

    - **WiFi-Einstellungen**:
    - Bearbeite die Datei [RFIDauslesung_copy_20241009134215.ino] und füge deine WiFi-SSID und dein Passwort hinzu:
        ```c++
        const char* ssid = "deine-ssid";
        const char* password = "dein-passwort";
        ```

        - **Server-Einstellungen**:
        - Stelle sicher, dass der Flask-Server auf dem richtigen Host und Port läuft, wie in der Arduino-Sketch-Datei angegeben.
        
    Lade den Sketch auf dein ESP32 hoch.

4. **Verwendung**:

    Starte das Hauptskript:
    ```sh
    python main.py
    ```
  

    Wähle die Option 1, um einen neuen Benutzer hinzuzufügen, und folge den Anweisungen.
    Benutzer löschen:

    Wähle die Option 2, um einen Benutzer zu löschen, und gib die RFID-UID des Benutzers ein.
    Alle Benutzer anzeigen:

    Wähle die Option 3, um alle Benutzer anzuzeigen.
    Tür öffnen:

    Wähle die Option 4, um die Tür zu öffnen, und gib die RFID-UID ein.
    Zugriffsprotokolle anzeigen:

    Wähle die Option 5, um die Zugriffsprotokolle anzuzeigen.
    Alle Zugriffsprotokolle löschen:

    Wähle die Option 6, um alle Zugriffsprotokolle zu löschen.

5. **Lizenz**:

    Dieses Projekt steht unter der MIT-Lizenz. Siehe die LICENSE-Datei für weitere Details. 

6. **Third-Party Libraries**:
    This project uses the following third-party libraries:

    **SQLite**
         - License: Public Domain
         - Link: [SQLite License](https://www.sqlite.org/copyright.html)

    **Flask**
        - License: BSD-3-Clause
        - Link: [Flask License](https://github.com/pallets/flask/blob/main/LICENSE.rst)

    **cryptography**
        - License: Apache License 2.0
        - Link: [cryptography License](https://github.com/pyca/cryptography/blob/main/LICENSE)
    

