```sh
1. Projektbeschreibung
2. Installation
1. Repository klonen
2. Abhängigkeiten installieren
3. Arduino-Sketch hochladen
```

## 1. Projektbeschreibung

Dieses Projekt ist ein RFID-Zugangskontrollsystem, das verschiedene Technologien wie Python, SQLite, Flask und Arduino verwendet. Es ermöglicht die Verwaltung von Benutzern und deren Zugriffsrechten sowie die Protokollierung von Zugriffsereignissen.

## 2. Installation

1. **Repository klonen**:
   ```sh
   git clone https://github.com/SD-Code0/rfid_acces.git
   cd rfid_acces
   ```

2. **Abhängigkeiten installieren:**:
    ```sh
    python3 -m venv rfid_venv
    source rfid_venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Arduino-Sketch hochladen**:

    Öffne die Datei RFIDauslesung.ino in der Arduino IDE.
    ## Konfiguration

    - **WiFi-Einstellungen**:
    - Bearbeite die Datei [ESP32_RFIDauslesung.ino] und füge deine WiFi-SSID und dein Passwort hinzu:
        ```c++
        const char* ssid = "deine-ssid";
        const char* password = "dein-passwort";
        const char* host = "die ip des servers hier angeben"
        ```
        
    Lade den Sketch auf dein ESP32 hoch.

## 3. Verwendung

    Starte das Hauptskript:
    ```sh
    source rfid_venv/bin/activate
    python3 main.py
    ```

    Beachte das die ip-adressen im code mit der des Servers übereinstimmen
    die Web-ui kann man unter ip des servers + port 5001 
    Beispielsweise:
    ```sh
    192.168.188.2:5001
    ```
    bei erstmaligen aufraufen der web ui wird man dazu aufgerufen ein Admin Konto anzulegen die für zukünftige zugriffe der web-ui erforderlich ist

5. **Geräte hinzufügen**
    öffne die web-ui und navigiere zu den Tab Geräte --> Gerät hinzufügen dort alle daten eingeben

6. **Benutzer hinzufügen**
    öffne die Web-ui und navigiere zu den Tab Benutzerverwaltung --> Benutzerhinzufügen dort alle erforderlichen daten eingeben die RFID kann mittels der Schreibstation auch ausgelesen werden 
7. **Benutzer löschen**
    öffne die Web-ui und navigiere zu den Tab Benutzerverwaltung --> Benutzer löschen dort entweder die RFID manuell eintragen oder die karte auf die Schreibstation legen und RFID auslesen klicken


## 4. Lizenz

    Dieses Projekt steht unter der MIT-Lizenz. Siehe die LICENSE-Datei für weitere Details. 

## 5. Third-Party Libraries
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
    

