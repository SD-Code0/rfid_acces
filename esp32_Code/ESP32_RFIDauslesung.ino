#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>



#define SS_PIN 5 //bei bedarf anpassen
#define RST_PIN 33 //bei bedarf anpassen
//testing
#include "esp_task_wdt.h"
#ifndef ESP_TASK_WDT_IDLE_CORE_MASK_ALL
#define ESP_TASK_WDT_IDLE_CORE_MASK_ALL ((1 << 0) | (1 << 1))
#endif
//testing end

MFRC522 mfrc522(SS_PIN, RST_PIN);  

// Bitte ändere volgende werte ensprechend mit ausnahme des ports

const char* ssid = "H304";
const char* password = "VTEa26-2426";
const char* host = "192.168.188.254";
const uint16_t port = 12345; // unverendert lassen
const char* pos = "eingang";



String RFID = ""; // nicht verändern
String fullData = ""; // nicht verändern
//testing
esp_task_wdt_config_t wdt_config = {
    .timeout_ms = 5000,  // Timeout in Millisekunden (5 Sekunden)
    .idle_core_mask = ESP_TASK_WDT_IDLE_CORE_MASK_ALL, // Alle Kerne überwachen
    .trigger_panic = true
  };  // System-Neustart bei Timeout
//testing end
void setup() {

  esp_task_wdt_init(&wdt_config);  // 5 Sekunden Watchdog aktivieren
  esp_task_wdt_add(NULL); // Watchdog für den Hauptprozess aktivieren

  Serial.begin(115200);

  SPI.begin(18,19,23);  // SCK, MISO, MOSI, SS
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
//Testing
  esp_task_wdt_reset(); // Muss regelmäßig aufgerufen werden, sonst Neustart
//testing end

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