#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>

#define SS_PIN 21
#define RST_PIN 14

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

const char* ssid = "H304";
const char* password = "VTEa26-2426";
const char* host = "192.168.188.22";  // IP-Adresse des Python-Servers
const uint16_t port = 12345;
const char* pos = "eingang"; // RFID-Nummer

String RFID = ""; // RFID-Nummer
String data = ""; // Daten von der Karte

void setup() {
  Serial.begin(115200);

  // SPI-Pins explizit initialisieren
  SPI.begin(13, 12, 11, SS_PIN);  // SCK, MISO, MOSI, SS

  mfrc522.PCD_Init();    // Init MFRC522
  Serial.println("RFID reader initialized.");

  WiFi.begin(ssid, password);

  // MAC-Adresse des ESP32 abrufen
  String macAddress = WiFi.macAddress();
  Serial.println("MAC-Adresse des ESP32:");
  Serial.println(macAddress);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Verbindung zu WiFi...");
  }

  Serial.println("WiFi verbunden.");
}

void loop() {
  // Look for new cards
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Store UID in RFID variable
  RFID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    RFID += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    RFID += String(mfrc522.uid.uidByte[i], HEX);
  }
  RFID.toUpperCase();
  Serial.println("RFID: " + RFID);

  // Read data from the card
  byte buffer[18];
  byte size = sizeof(buffer);
  byte blockAddr = 4; // Example block address, change as needed
  if (mfrc522.MIFARE_Read(blockAddr, buffer, &size) == MFRC522::STATUS_OK) {
    data = "";
    for (byte i = 0; i < 16; i++) {
      data += char(buffer[i]);
    }
    Serial.println("Data: " + data);
  } else {
    Serial.println("Reading data failed");
  }

  // Send data to server
  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("Verbindung zum Server fehlgeschlagen.");
    delay(1000);
    return;
  }

  String payload = RFID + "," + data + "," + pos;
  client.print(payload);
  Serial.println("Daten gesendet: " + payload);

  delay(1000); // Add a delay to avoid flooding the server
}