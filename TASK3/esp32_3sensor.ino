
bool shouldSendData = false;
unsigned long previousDataSendMillis = 0;
const long dataSendInterval = 5000; 

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 Ready. Simulating 3 generic sensors. Waiting for START command.");
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

      
      float sensor1_value = random(0, 1001) / 10.0;     
      float sensor2_value = random(500, 1501) / 10.0;    
      float sensor3_value = (random(-200, 201)) / 10.0;  

      Serial.print(sensor1_value, 1);
      Serial.print(",");
      Serial.print(sensor2_value, 1);
      Serial.print(",");
      Serial.println(sensor3_value, 1);
    }
  }
}