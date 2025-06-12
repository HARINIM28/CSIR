#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

bool shouldSend = false;  

void setup() {
  delay(1000); 
  Serial.begin(115200);
  Wire.begin(21, 22); 

  if (!ads.begin()) {
    Serial.println("ADS1115 not detected. Check wiring!");
    while (1);
  }

  ads.setGain(GAIN_ONE);  // ±4.096V range
  Serial.println("ADS1115 Ready. Waiting for START...");
}

void loop() {
  
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  

    if (command.equalsIgnoreCase("START")) {
      shouldSend = true;
      Serial.println("START command received.");
    } else if (command.equalsIgnoreCase("STOP")) {
      shouldSend = false;
      Serial.println("STOP command received.");
    }
  }

  if (shouldSend) {
    int16_t raw = ads.readADC_SingleEnded(0);  
    float voltage = (raw / 32767.0) * 3.3;      

    
    Serial.print("Voltage: ");
    Serial.print(voltage, 3);
    Serial.println(" V");

    delay(500); 
  }
}

