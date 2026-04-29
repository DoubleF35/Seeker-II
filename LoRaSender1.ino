#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>

// Definizione Pin per ESP32-C3 Super Mini
const int SCK_PIN = 4;
const int MISO_PIN = 5;
const int MOSI_PIN = 6;
const int SS_PIN = 7;
const int RST_LORA = 10;
const int DIO0_LORA = 3;
const int BOARD_LED = 8; // LED integrato sulla Super Mini

Adafruit_BMP280 bmp;
Adafruit_MPU6050 mpu;
long packetCounter = 0;

void setup() {
  // Configurazione LED (Sulla Super Mini il LED è sul pin 8)
  pinMode(BOARD_LED, OUTPUT);
  digitalWrite(BOARD_LED, HIGH); // Spegne il LED all'inizio (Active Low)

  Serial.begin(115200);
  
  // Pausa per stabilizzazione tensione batteria/condensatore
  delay(2000); 

  // 1. Inizializza I2C (SDA=8, SCL=9) 
  Wire.begin(8, 9);
  
  // 2. Inizializza SPI e LoRa
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);
  LoRa.setPins(SS_PIN, RST_LORA, DIO0_LORA);
  
  if (!LoRa.begin(433E6)) {
    Serial.println("Errore LoRa!");
    // In caso di errore LoRa, il LED rimane fisso acceso (LOW)
    digitalWrite(BOARD_LED, LOW);
  }

  // 3. Inizializza Sensori
  bmp.begin(0x76);
  mpu.begin(0x68);

  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL, 
                  Adafruit_BMP280::SAMPLING_X2, 
                  Adafruit_BMP280::SAMPLING_X16, 
                  Adafruit_BMP280::FILTER_X16, 
                  Adafruit_BMP280::STANDBY_MS_500);

  Serial.println("SISTEMA PRONTO");

  // Lampeggio di conferma avvio
  for(int i=0; i<10; i++){
    digitalWrite(BOARD_LED, !digitalRead(BOARD_LED)); 
    delay(50);
  }
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  float alt = bmp.readAltitude(1013.25);
  float accY = a.acceleration.y / 9.81;

  // Stringa dati per la GUI
  String data = String(packetCounter) + "," + String(alt) + "," + String(accY);

  // Trasmissione LoRa
  LoRa.beginPacket();
  LoRa.print(data);
  LoRa.endPacket();

  // Feedback visivo: il LED lampeggia rapido ad ogni invio
  digitalWrite(BOARD_LED, LOW); // Accende LED (Active Low)
  delay(20);
  digitalWrite(BOARD_LED, HIGH); // Spegne LED
  
  packetCounter++;
  delay(130); // Circa 150ms totali di intervallo
}
