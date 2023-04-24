#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// Replace with your network credentials
const char* ssid = "firmly grasp it";
const char* password = "7087840074";
const int port = 80;

// Set the static IP address
IPAddress staticIP(192, 168, 1, 100);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

ESP8266WebServer server(port);

// Sensor calibration (meant to be calibrated by app)
int dry = 850;
int wet = 385;

int readWaterSensor(){
  int sensorVal = analogRead(A0);
  int percentageHumidity = map(sensorVal, wet, dry, 100, 0);
  return percentageHumidity;
}

void handleEcho() {
  String message = server.arg("message");
  server.send(200, "text/plain", message);
}

void handleSensor() {
  String sensorString = String(readWaterSensor());
  server.send(200, "text/plain", sensorString);
}

void setup() {
  Serial.begin(115200);
  delay(500); // small delay
  Serial.println("\nStarting..."); // marker
  WiFi.begin(ssid, password);

  // Set the static IP address
  WiFi.config(staticIP, gateway, subnet);

  Serial.println(WiFi.localIP().toString()); // Print the IP of NodeMCU

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");

  server.on("/echo", handleEcho);
  server.on("/sensor", handleSensor);
  server.begin();
}

void loop() {
  Serial.println(String(readWaterSensor()) + "%");
  server.handleClient();
  delay(100);
}