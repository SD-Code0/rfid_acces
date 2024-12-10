#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 21  // SPI SS Pin
#define RST_PIN 14 // Reset Pin

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(115200);        // Start serial communication
  SPI.begin();                 // Init SPI bus
  mfrc522.PCD_Init();          // Init RFID reader
  Serial.println("RFID-Reader bereit. Halten Sie eine Karte an den Leser.");
}

void loop() {
  // Check if a new card is present
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return; // No card detected
  }

  // Select the card
  if (!mfrc522.PICC_ReadCardSerial()) {
    return; // Could not read the card
  }

  // Assemble UID as a single uppercase string
  String RFID = ""; // Variable to store the UID
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    RFID += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""); // Add leading zero
    RFID += String(mfrc522.uid.uidByte[i], HEX);             // Convert to HEX
  }
  RFID.toUpperCase(); // Convert to uppercase
  Serial.println("RFID UID: " + RFID);

  // Halt communication with the card
  mfrc522.PICC_HaltA();
}