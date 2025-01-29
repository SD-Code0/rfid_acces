#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>

#define SS_PIN 21 //bei bedarf anpassen
#define RST_PIN 14 //bei bedarf anpassen

MFRC522 mfrc522(SS_PIN, RST_PIN);  

// Bitte ändere volgende werte ensprechend mit ausnahme des ports

const char* ssid = "";
const char* password = "None";
const char* host = "";
const uint16_t port = 12345; // unverendert lassen
const char* pos = "";



String RFID = ""; // nicht verändern
String fullData = ""; // nicht verändern

void setup() {
  Serial.begin(115200);

  SPI.begin(13, 12, 11);  // SCK, MISO, MOSI, SS
  mfrc522.PCD_Init();
  Serial.println("Lesen von höheren Blöcken...");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Verbindung zu WiFi...");
  }
  Serial.println("WiFi verbunden.");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  RFID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    RFID += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    RFID += String(mfrc522.uid.uidByte[i], HEX);
  }
  RFID.toUpperCase();
  Serial.println("RFID: " + RFID);

  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

  byte buffer[18];
  byte startBlock = 16;
  byte currentBlock = startBlock;
  fullData = "";


  for (byte i = 0; i < 12; i++) {
    if ((currentBlock + 1) % 4 == 0) {
      currentBlock++;  // Überspringe Schlüsselblock
    }

    // Authentifizieren des Blocks
    Serial.println("Authentifizieren für Block " + String(currentBlock));
    MFRC522::StatusCode status = mfrc522.PCD_Authenticate(
        MFRC522::PICC_CMD_MF_AUTH_KEY_A, currentBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      Serial.println("Authentifizierung fehlgeschlagen bei Block " + String(currentBlock));
      return;
    }

    // Block lesen
    byte size = sizeof(buffer);
    status = mfrc522.MIFARE_Read(currentBlock, buffer, &size);
    if (status == MFRC522::STATUS_OK) {
      for (byte j = 0; j < 16; j++) {
        if (buffer[j] != 0)  // Leere Bytes ignorieren
          fullData += char(buffer[j]);
      }
      Serial.println("Block " + String(currentBlock) + " gelesen");
    } else {
      Serial.println("Lesefehler bei Block " + String(currentBlock));
      return;
    }

    currentBlock++;  // Zum nächsten Block wechseln
  }

  Serial.println("Gesamte Daten: " + fullData);
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  // Daten an den Server senden
  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("Serververbindung fehlgeschlagen.");
    return;
  }

  String payload = RFID + "," + fullData + "," + pos;
  client.print(payload);
  Serial.println("Daten gesendet: " + payload);

  delay(1000);
}