#include <SPI.h>

const int SPI_SCLK = 18;
const int SPI_MOSI = 23;
const int DAC_CS_PIN = 5;
const int ADC_PIN = 34;

void setDacVoltage(int dacValue) {
  uint16_t command = 0x1000;
  command |= (dacValue & 0x0FFF);

  SPI.beginTransaction(SPISettings(20000000, MSBFIRST, SPI_MODE0));
  digitalWrite(DAC_CS_PIN, LOW); 
  SPI.transfer16(command);
  digitalWrite(DAC_CS_PIN, HIGH);
  SPI.endTransaction();
}

void setup() {
  Serial.begin(115200);
  Serial.println("--- ESP32 DAC Voltmeter ---");
  Serial.println();

  pinMode(DAC_CS_PIN, OUTPUT);
  digitalWrite(DAC_CS_PIN, HIGH);

  SPI.begin(SPI_SCLK, -1, SPI_MOSI, -1); 

  analogReadResolution(12);
}

void loop() {
  for (int i = 0; i <= 3300; i += 100) {
    setDacVoltage(i);
    delay(10); 

    int rawAdcValue = analogRead(ADC_PIN);
    float measuredVoltage = rawAdcValue * (3.3 / 4095.0);

    Serial.print(measuredVoltage, 3);
    Serial.println(" V");

    delay(490); 
  }

  Serial.println("\n---Top Reached - Resetting---\n");
  delay(2000);
}