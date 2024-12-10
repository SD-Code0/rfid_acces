#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 21
#define RST_PIN 14

const char* write_data = "gAAAAABnV_ctCvNJfXcBEmMO1Vu3JsGC-Q4G3oUJ9ex5t3HCl6o9UGNgH_M0r3jHZ7R0xc15qan0ry8TKkp-lNtmOgyNgmgOMbhOHPL4TJyTWGISMBPlhm73GWbNQPuym3BfTsrK--99";

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(115200);

  // Initialize SPI bus and RFID module
  SPI.begin(13, 12, 11);
  mfrc522.PCD_Init();
  Serial.println("Schreiben auf höhere Blöcke...");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;  // Standard-Schlüssel

  byte dataBlock[16];
  int totalBlocks = ceil(strlen(write_data) / 16.0);
  Serial.println("Schreiben von " + String(totalBlocks) + " Blöcken...");

  // Beginne mit Block 16 (im 5. Sektor) und vermeide Schlüsselblöcke
  byte startBlock = 16;
  byte currentBlock = startBlock;

  for (int i = 0; i < totalBlocks; i++) {
    // Prüfen, ob der aktuelle Block ein Schlüsselblock ist, und überspringen
    if ((currentBlock + 1) % 4 == 0) {
      currentBlock++;  // Überspringe Schlüsselblock
    }

    memset(dataBlock, 0, 16);  // Puffer leeren
    memcpy(dataBlock, write_data + (i * 16), 16);

    // Authentifizieren des Blocks
    Serial.println("Authentifizieren für Block " + String(currentBlock));
    MFRC522::StatusCode status = mfrc522.PCD_Authenticate(
        MFRC522::PICC_CMD_MF_AUTH_KEY_A, currentBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      Serial.println("Authentifizierung fehlgeschlagen bei Block " + String(currentBlock));
      return;
    }

    // Block schreiben
    status = mfrc522.MIFARE_Write(currentBlock, dataBlock, 16);
    if (status != MFRC522::STATUS_OK) {
      Serial.println("Schreibfehler bei Block " + String(currentBlock));
      return;
    }
    Serial.println("Block " + String(currentBlock) + " erfolgreich geschrieben!");

    currentBlock++;  // Zum nächsten Block wechseln
  }

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  Serial.println("Schreiben abgeschlossen.");
}