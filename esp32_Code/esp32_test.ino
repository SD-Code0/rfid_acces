#include <WiFi.h>          // Für ESP32



const char* ssid     = "H304";
const char* password = "VTEa26-2426";

const char* server_ip = "192.168.188.22"; 
const int server_port2 = 12346;    

String rfid_uid = "rfid12345";

// Funktion zum Senden von Daten und Empfangen der Antwort
void sendDataAndReceiveResponse(int port, String dataToSend) {
  WiFiClient client;
  Serial.print("Verbinde zu Server ");
  Serial.print(server_ip);
  Serial.print(" auf Port ");
  Serial.println(port);

  if (!client.connect(server_ip, port)) {
    Serial.println("Verbindung fehlgeschlagen!");
    return;
  }

  Serial.println("Verbunden. Daten senden...");

  // Daten senden
  client.print(dataToSend);
  Serial.println("Daten gesendet:");

  Serial.println(dataToSend);

  // Warten auf Antwort vom Server
  while (client.connected()) {
    if (client.available()) {
      String response = client.readStringUntil('\n');
      Serial.println("Antwort vom Server:");
      Serial.println(response);
    }
  }
}