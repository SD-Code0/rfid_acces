#include <WiFi.h>
#include <SPI.h>
#include <MFRC522.h>

const char* ssid = "H304";
const char* password = "VTEa26-2426";
const char* host = "192.168.188.22";  // IP-Adresse des Python-Servers
const uint16_t port = 12345;

const char* RFID = "2426"; // RFID-Nummer
const char* enc_fernet = "gAAAAABnUEgS4TtAbcEd6qx_0BNVYtLxZhW-uCttihsMo95Mk1zwhRtcuvchxIz72lNeO2vyOiRutoZ3DnNI4nqeG6taHhQwrazm_d-rDlniV2gWye0hEyTenHZAPTKcw1Ude95H1023"; // Verschlüsselter fernet key
const char* challange_data = ""; // Verschlüsselte Daten
const char* challange_response = ""; // Verschlüsselte Signatur
const char* pos = "eingang"; // Position des RFID-Lesers


void setup() {
  Serial.begin(115200);
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
  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("Verbindung zum Server fehlgeschlagen.");
    delay(1000);
    return;
  }

  if (RFID && enc_fernet && challange_data[0] != '\0' && challange_response[0] != '\0' && pos) {
    String data = String(RFID) + "," + String(enc_fernet) + "," + String(challange_data) + "," + String(challange_response) + "," + String(pos);
    client.print(data);
    Serial.println("Daten gesendet: " + data);
  } else if (RFID && enc_fernet && pos) {
    String data = String(RFID) + "," + String(enc_fernet) + "," + String(pos);
    client.print(data);
    Serial.println("Daten gesendet: " + data);
  } else {
    Serial.println("Fehler: RFID, enc_fernet und pos müssen gesetzt sein.");
    return;
  }

  client.stop();
  delay(30000);  // Warte 30 Sekunden, bevor erneut gesendet wird
}