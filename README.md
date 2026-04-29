# Seeker-II

I designed and built a fully custom model rocket system, combining aerodynamics, structural design, and onboard electronics. The project started with simulation using OpenRocket to optimize stability, center of pressure, and flight profile. I then scaled and refined the design, creating a full CAD model in Fusion 360, including the airframe, nose cone, and internal structure. Parts were manufactured and assembled, with particular attention to weight distribution and structural integrity. I designed and built a parachute recovery system, ensuring safe deployment and descent. Multiple iterations were considered to improve reliability and protect the payload. In addition, I developed a custom avionics system with onboard telemetry, capable of collecting and transmitting flight data. I also created a  GUI to visualize and analyze the data, making the system more usable and complete. This project required integrating physics simulation, mechanical design, prototyping, and electronics, along with testing and iteration to improve performance and reliability.
- 
Here you can find the OpenRocket simulation: Seeker-II.ork 

The cad model is downloadable on https://www.thingiverse.com/thing:7338519 

Hardware Components & Wiring
The Seeker-II flight computer is built around the ESP32-C3 Super Mini, chosen for its RISC-V architecture and compact footprint. The system utilizes LoRa technology for long-range telemetry and high-precision sensors for flight data acquisition.
1. component list:
   - Microcontroller: ESP32-C3 Super Mini.
   - LoRa Module: SX1276 / RFM95W (operating at 433MHz).
   - Altimeter/Barometer: Adafruit BMP280 (I2C interface).
   - Inertial Measurement Unit (IMU): MPU6050 (6-DOF Accelerometer & Gyroscope).
   - Power Supply: 3.7V Li-ion Battery / 3.7V LiPo Battery (1S).
   - Decoupling Capacitor: 100µF - 470µF Electrolytic Capacitor (connected across LoRa VCC/GND to handle transmission current spikes and prevent brownouts).
2. Technical Specifications:
   - Total Launch Mass: ~364g (300g airframe + 64g motor).
   - Propulsion: Tsp E20-6.
   - Max G-Load: Configured for up to 16G (MPU6050 range).
   - Sampling Rate: ~7Hz (150ms loop interval)
3. Wiring: 
Component,Pin_Component,ESP32_C3_Pin,Function
- LoRa Module,SCK,GPIO 4,SPI Clock
- LoRa Module,MISO,GPIO 5,SPI Data Out
- LoRa Module,MOSI,GPIO 6,SPI Data In
- LoRa Module,NSS / CS,GPIO 7,Chip Select
- LoRa Module,RST,GPIO 10,Reset
- LoRa Module,DIO0,GPIO 3,Interrupt
- Sensors (BMP/MPU),SDA,GPIO 8,I2C Data
- Sensors (BMP/MPU),SCL,GPIO 9,I2C Clock
- Status LED,Anode (+),GPIO 8,Onboard LED
- BMP280,VCC,3V3,Power
- MPU6050,VCC,3V3,Power
- LoRa Module,VCC,3V3,Power
- Capacitor,Positive (+),3V3,Buffer
- Capacitor,Negative (-),GND,Buffer
- Common Rail,GND,GND,Ground
4. You can find the code for the lora sender (code to upload in the esp32 c3 on the rocket) and the lora receiver (code to upload on the esp32 wired with lora functioning as a ground base)
5. The code for the gui is listed as a python file
<img width="826" height="633" alt="ewfki43jewifjoqi34jfwoiqj43ew" src="https://github.com/user-attachments/assets/f7c15cac-6107-43cc-a8ad-ed3e2c9ba807" />

