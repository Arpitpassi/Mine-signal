#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWD";

ESP8266WebServer server(80);

const int ledPin = 2; // GPIO2 on ESP8266

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  
  server.on("/toggle", HTTP_GET, handleToggle);
  server.begin();
  Serial.println("HTTP server started");
  Serial.println(WiFi.localIP());
}

void loop() {
  server.handleClient();
}

void handleToggle() {
  digitalWrite(ledPin, !digitalRead(ledPin));
  server.send(200, "text/plain", "LED toggled");
}