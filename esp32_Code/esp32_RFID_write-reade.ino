#include <WiFi.h>
#include <WiFiClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <cmath> // Für ceil

// WLAN-Daten anpassen
const char* ssid = "tester";
const char* password = "";

// Serverdaten anpassen
const char* host = "123.132";
const int server_port = 12346;

// RC522 Pins anpassen!
#define RST_PIN 14
#define SS_PIN  21

MFRC522 mfrc522(SS_PIN, RST_PIN);
WiFiClient client;

String receivedFernetKey = "";
String rfidUID = ""; // Hier speichern wir die einmalig gelesene RFID

void setup() {
  Serial.begin(115200);
  Serial.println("Starte...");

  WiFi.begin(ssid, password);
  Serial.print("Verbinde mit WLAN: ");
  Serial.print(ssid);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWLAN verbunden!");
  Serial.print("IP-Adresse: ");
  Serial.println(WiFi.localIP());

  SPI.begin(13,12,11);
  mfrc522.PCD_Init();
  Serial.println("RC522 RFID Reader initialisiert.");
}

void loop() {
  // Warten auf eine neue Karte
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    rfidUID = getUID();
    Serial.println("RFID erkannt: " + rfidUID);

    // RFID einmal an den Server senden
    sendRFIDToServer(rfidUID);

    // Auf eine direkte ENC-Antwort warten (3s)
    bool directEnc = waitForDirectEncResponse();
    if (directEnc) {
      // Key wurde direkt empfangen
      writeFernetKeyToCard(receivedFernetKey);
    } else {
      // Kein direkter Key, jetzt bis zu 60s lang alle 5s versuchen
      bool keyReceived = false;
      int attempts = 0;
      int maxAttempts = 12; // 12 * 5s = 60s

      while (!keyReceived && attempts < maxAttempts) {
        Serial.println("Kein Key direkt erhalten. Versuche GET_FERNET...");
        keyReceived = fetchFernetKeyFromServer();
        if (keyReceived) {
          // Key empfangen, sofort schreiben und abbrechen
          writeFernetKeyToCard(receivedFernetKey);
          break; 
        } else {
          attempts++;
          Serial.println("Kein Key erhalten. Erneuter Versuch in 5 Sekunden...");
          delay(5000);
        }
      }

      if (!keyReceived) {
        Serial.println("Nach 60 Sekunden kein Fernet-Key erhalten.");
      }
    }

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    delay(1000);
  }

  delay(200);
}

void sendRFIDToServer(String uid) {
  if (client.connect(host, server_port)) {
    String message = "RFID:" + uid;
    client.println(message);
    Serial.println("Gesendet an Server: " + message);
    // Hier kein ENC erwarten, das macht waitForDirectEncResponse()
  } else {
    Serial.println("Konnte keine Verbindung zum Server aufbauen, um RFID zu senden.");
  }
}

bool waitForDirectEncResponse() {
  // 3s auf ENC-Antwort warten
  unsigned long startTime = millis();
  bool encFound = false;

  while (millis() - startTime < 3000) {
    if (client.available()) {
      String response = client.readStringUntil('\n');
      response.trim();
      Serial.println("Antwort vom Server: " + response);
      if (response.startsWith("ENC:")) {
        receivedFernetKey = response.substring(4);
        Serial.println("Fernet-Key direkt empfangen: " + receivedFernetKey);
        encFound = true;
        break;
      }
    }
    delay(10);
  }

  client.stop();
  return encFound;
}

bool fetchFernetKeyFromServer() {
  // Ein GET_FERNET Versuch, 30s warten
  bool keyFound = false;

  if (client.connect(host, server_port)) {
    Serial.println("Verbunden, sende GET_FERNET...");
    client.println("GET_FERNET");

    unsigned long startTime = millis();
    while (millis() - startTime < 30000) {
      if (client.available()) {
        String response = client.readStringUntil('\n');
        response.trim();
        Serial.println("Antwort vom Server: " + response);
        if (response.startsWith("ENC:")) {
          receivedFernetKey = response.substring(4);
          Serial.println("Fernet-Key empfangen: " + receivedFernetKey);
          keyFound = true;
          break;
        } else if (response == "NO_KEY") {
          Serial.println("Kein Fernet-Key vorhanden.");
          break;
        }
      }
      delay(10);
    }

    client.stop();
  } else {
    Serial.println("Konnte keine Verbindung zum Server aufbauen (GET_FERNET).");
  }

  return keyFound;
}

void writeFernetKeyToCard(String fKey) {
  // Keine erneute Kartenprüfung, wir verlassen uns auf die zuvor gelesene UID
  const char* write_data = fKey.c_str();
  int totalBlocks = ceil(strlen(write_data) / 16.0);
  Serial.println("Schreiben von " + String(totalBlocks) + " Blöcken...");

  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

  byte dataBlock[16];
  byte startBlock = 16;
  byte currentBlock = startBlock;

  for (int i = 0; i < totalBlocks; i++) {
    if ((currentBlock + 1) % 4 == 0) {
      currentBlock++;
    }

    memset(dataBlock, 0, 16);
    memcpy(dataBlock, write_data + (i * 16), 16);

    Serial.println("Authentifizieren für Block " + String(currentBlock));
    MFRC522::StatusCode status = mfrc522.PCD_Authenticate(
      MFRC522::PICC_CMD_MF_AUTH_KEY_A, currentBlock, &key, &(mfrc522.uid)
    );
    if (status != MFRC522::STATUS_OK) {
      Serial.println("Authentifizierung fehlgeschlagen bei Block " + String(currentBlock));
      return;
    }

    status = mfrc522.MIFARE_Write(currentBlock, dataBlock, 16);
    if (status != MFRC522::STATUS_OK) {
      Serial.println("Schreibfehler bei Block " + String(currentBlock));
      return;
    }
    Serial.println("Block " + String(currentBlock) + " erfolgreich geschrieben!");
    currentBlock++;
  }

  Serial.println("Fernet-Key erfolgreich auf die Karte geschrieben.");
}

String getUID() {
  String uidStr;
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uidStr += String(mfrc522.uid.uidByte[i], HEX);
  }
  uidStr.toUpperCase();
  return uidStr;
}