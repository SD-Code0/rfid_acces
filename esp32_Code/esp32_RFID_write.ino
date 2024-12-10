#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 21
#define RST_PIN 14

const char* write_data = "gAAAAABnUEgS4TtAbcEd6qx_0BNVYtLxZhW-uCttihsMo95Mk1zwhRtcuvchxIz72lNeO2vyOiRutoZ3DnNI4nqeG6taHhQwrazm_d-rDlniV2gWye0hEyTenHZAPTKcw1Ude95H1023";

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(115200);

  // Initialize SPI bus and RFID module
  SPI.begin(13, 12, 11);
  mfrc522.PCD_Init();
  Serial.println("Place your card near the reader...");
}

void loop() {
  // Check for a new card
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select the card
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Authenticate block 4 with key A
  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;  // Default key: 0xFF

  byte blockAddr = 4;  // Block to write to
  byte dataBlock[16] = {"gAAAAABnUEgS4TtAbcEd6qx_0BNVYtLxZhW-uCttihsMo95Mk1zwhRtcuvchxIz72lNeO2vyOiRutoZ3DnNI4nqeG6taHhQwrazm_d-rDlniV2gWye0hEyTenHZAPTKcw1Ude95H1023"};  // Data to write (16 bytes max)

  MFRC522::StatusCode status = mfrc522.PCD_Authenticate(
      MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockAddr, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Authentication failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }

  // Write data to the block
  status = mfrc522.MIFARE_Write(blockAddr, dataBlock, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("Write failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
  } else {
    Serial.println("Data written successfully!");
  }

  // Halt PICC (end communication with the card)
  mfrc522.PICC_HaltA();

  // Stop encryption on PCD
  mfrc522.PCD_StopCrypto1();
}