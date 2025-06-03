bool shouldSendData = false;
unsigned long previousDataSendMillis = 0;
const long dataSendInterval = 16000;

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Ready. Waiting for START command.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equalsIgnoreCase("START")) {
      shouldSendData = true;
      previousDataSendMillis = millis();
      Serial.println("INFO: START command received. Sending data.");
    } else if (command.equalsIgnoreCase("STOP")) {
      shouldSendData = false;
      Serial.println("INFO: STOP command received. Stopping data transmission.");
    }
  }

  if (shouldSendData) {
    unsigned long currentMillis = millis();
    if (currentMillis - previousDataSendMillis >= dataSendInterval) {
      previousDataSendMillis = currentMillis;

      float temperature = random(150, 351) / 10.0;
      float humidity = random(300, 801) / 10.0;

      Serial.print(temperature, 1);
      Serial.print(",");
      Serial.println(humidity, 1);
    }
  }
}