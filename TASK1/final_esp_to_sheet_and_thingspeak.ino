#include <WiFi.h>
#include <HTTPClient.h>

// WiFi
const char* ssid = "SENSOR";
const char* password = "Sensor@9334";

//Google Apps Script Web App URL
String gasWebAppUrl = "https://script.google.com/macros/s/AKfycbyu6VpioMoEJwnFXK8KcV0on_5IIfa3McCRBtv6X6YZ-vbPML79GQvkhkOAQPN-VNbv/exec";

// ThingSpeak 
const char* thingspeakApiKey = "MDMLGTT2MVZK9MHJ";  
const char* thingspeakServer = "http://api.thingspeak.com/update";

const float TEMP_MIN = 15.0;
const float TEMP_MAX = 35.0;
const float HUM_MIN = 30.0;
const float HUM_MAX = 80.0;

const unsigned long SEND_INTERVAL_MS = 16000;  
unsigned long lastSendTime = 0;

void setup() {
  Serial.begin(115200);
  delay(100);

  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retries++;
    if (retries > 20) {
      Serial.println("\nFailed to connect to WiFi. Restarting...");
      ESP.restart();
    }
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  randomSeed(analogRead(0)); // For generating random values
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    if (millis() - lastSendTime > SEND_INTERVAL_MS) {
      lastSendTime = millis();

      // Generate random temperature and humidity
      float temperature = random(TEMP_MIN * 100, TEMP_MAX * 100) / 100.0;
      float humidity = random(HUM_MIN * 100, HUM_MAX * 100) / 100.0;

      Serial.print("Temperature: ");
      Serial.print(temperature);
      Serial.print(" °C | Humidity: ");
      Serial.print(humidity);
      Serial.println(" %");

      // Send to Google Sheets
      String sheetUrl = gasWebAppUrl + "?temperature=" + String(temperature, 2) + "&humidity=" + String(humidity, 2);
      HTTPClient http;
      http.begin(sheetUrl);
      int httpCode = http.GET();

      if (httpCode > 0) {
        Serial.print("Google Sheets Response Code: ");
        Serial.println(httpCode);
        String payload = http.getString();
        Serial.print("Payload: ");
        Serial.println(payload);
      } else {
        Serial.print("Google Sheets GET failed: ");
        Serial.println(http.errorToString(httpCode).c_str());
      }
      http.end();

      // Send to ThingSpeak 
      String tsUrl = String(thingspeakServer) + "?api_key=" + thingspeakApiKey +
                     "&field1=" + String(temperature, 2) +
                     "&field2=" + String(humidity, 2);

      HTTPClient tsHttp;
      tsHttp.begin(tsUrl);
      int tsResponse = tsHttp.GET();

      if (tsResponse > 0) {
        Serial.print("ThingSpeak Response Code: ");
        Serial.println(tsResponse);
        String tsPayload = tsHttp.getString();
        Serial.print("ThingSpeak Payload: ");
        Serial.println(tsPayload);
      } else {
        Serial.print("ThingSpeak GET failed: ");
        Serial.println(tsHttp.errorToString(tsResponse).c_str());
      }
      tsHttp.end();
    }
  } else {
    Serial.println("WiFi Disconnected. Reconnecting...");
    WiFi.begin(ssid, password);
    delay(1000);
  }
}
