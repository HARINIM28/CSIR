#include "MCP48xx.h"

const int DAC_CS_PIN = 5;
const int ADC_PIN = 35;

MCP4822 dac(DAC_CS_PIN);

void setup() {
  Serial.begin(115200);
  Serial.println("--- ESP32 DAC Single Value Test (MCP48xx Library) ---");
  Serial.println();

  dac.init();
  dac.setGainB(MCP4822::Gain::High);
  dac.turnOnChannelB();
  analogReadResolution(12);

  const int dacValueToTest = 1100;

  Serial.print("Commanding DAC with digital value: ");
  Serial.println(dacValueToTest);

  dac.setVoltageB(dacValueToTest);
  dac.updateDAC();
  
  delay(100);

  int rawAdcValue = analogRead(ADC_PIN);
  float measuredVoltage = rawAdcValue * (3.3 / 4095.0);

  Serial.print("Measured Voltage: ");
  Serial.print(measuredVoltage, 3);
  Serial.println(" V");

  Serial.println("\n--- Test Complete ---");
}

void loop() {
  
}