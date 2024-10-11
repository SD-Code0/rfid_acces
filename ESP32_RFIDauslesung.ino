#include <WiFi.h>

const char* ssid = "ssid";
const char* password = "Passwort";
const char* host = "172.20.10.6";  // IP-Adresse des Python-Servers
const uint16_t port = 12345;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

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

  String data = "123abc";
  data += ",";
  data += "gAAAAABnBqrLwJJat4cU-DxaBEkPcFD3Z7glzVPIuyyMpPAmixpabHyPtl8cn9xHFnEfPWaAntcFdDvgDBsSE6yE-kMORmKZZNw5KN1inwTLFny_tDj2K7_KgOgmkHiw5o_K7XELOopB";
  data += ",";
  data += "123";
  data += ",";
  data += "gAAAAABnBqsHBvoOdYnYI0Zxh4GNEncPy0yZLjmNXUUivYWlD6lhQdv1OvpoDNpnU_NDxj7YEnhn6Ry9i9d63R6ToRFhP8nHhQ==";
  client.print(data);
  Serial.println("Daten gesendet: " + data);

  client.stop();
  delay(10000);  // Warte 10 Sekunden, bevor erneut gesendet wird
}