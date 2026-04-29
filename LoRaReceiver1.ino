#include <SPI.h>
#include <LoRa.h>


const int csPin = 5;          
const int resetPin = 14;      
const int irqPin = 26;        

void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  LoRa.setPins(csPin, resetPin, irqPin);
  
  if (!LoRa.begin(433E6)) {
    Serial.println("ERRORE_LORA");
    while (1);
  }

  LoRa.setSpreadingFactor(7); 
  
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String incoming = "";
    while (LoRa.available()) {
      incoming += (char)LoRa.read();
    }
    
    
    int rssi = LoRa.packetRssi();

    // Inviamo a Python: ID,ALT,ACCX,ACCY,ACCZ,GYROX,PRESS,RSSI
    Serial.print(incoming);
    Serial.print(",");
    Serial.println(rssi); 
  }
}