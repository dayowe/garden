#include <Wire.h>  // Include Wire library for I2C
#include <Adafruit_GFX.h> // Include Adafruit graphics library
#include <Adafruit_SSD1306.h> // Include Adafruit SSD1306 library
#include <PubSubClient.h>
#include <ModbusMaster.h>
#include <WiFi.h>  // Include the WiFi library
#include "WiFiCredentials.h"
#include "mqttCredentials.h"

// MQTT Topics
const char* temperatureTopic = "sensor/soil/thcs1/temperature";
const char* moistureTopic = "sensor/soil/thcs1/moisture";
const char* conductivityTopic = "sensor/soil/thcs1/conductivity";

// Instantiate ModbusMaster object
ModbusMaster sensor;

// Use Serial2 for RS485 communication on ESP32
#define RS485Serial Serial2
// RS485 Transmit Enable Pin - Not used since converter does automatic switching
// Adjust pins according to your wiring if needed
#define RXD2 16
#define TXD2 17

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire);

void preTransmission() {
  // Not needed for automatic RS485 control
}

void postTransmission() {
  // Not needed for automatic RS485 control
}

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to WiFi");

  // Set MQTT server
  client.setServer(mqttServer, mqttPort);

  // Begin Serial Communication with Computer for debugging
  Serial.begin(115200);

  // Begin Serial2 Communication for RS485 on pins 16 & 17 (RX: 16, TX: 17) adjust if needed
  RS485Serial.begin(4800, SERIAL_8N1, 16, 17);
  
  // Modbus communication setup
  sensor.begin(1, RS485Serial); // Slave ID: 1
  sensor.preTransmission(preTransmission);
  sensor.postTransmission(postTransmission);

  Serial.println("Reading Soil Sensor Data:");

  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  
  // Clear the buffer.
  display.clearDisplay();

  // add here any additional display setup you want to do initially
  
  // Display static text (just as an example, can be removed if not needed)
  display.setTextSize(1);    // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE); // Draw white text
  display.setCursor(0,0);   // Start at top-left corner
  display.println(F("Soil Sensor Data:"));
  
  // Show the display buffer on the screen
  display.display();
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP32Client", mqttUser, mqttPassword)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  uint8_t result;
  float humidity, temperature, conductivity;
  
  // Read 3 registers starting at 0x0000
  result = sensor.readHoldingRegisters(0x0000, 3);
  
  if (result == sensor.ku8MBSuccess) {
    humidity = sensor.getResponseBuffer(0) / 10.0; // sensor returns dat aas 0.1%RH, so divide by 10
    temperature = sensor.getResponseBuffer(1) / 10.0; // sensor returns data as 0.1°C, so divide by 10
    conductivity = sensor.getResponseBuffer(2) / 1000.0; // Ensure division by a floating-point number for accurate calculation

    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println("% RH");

    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println("°C");

    Serial.print("Conductivity: ");
    Serial.print(conductivity);
    Serial.println("us/cm");
  } else {
    Serial.println("Failed to read from sensor, check wiring");
  }
  
  delay(1000); // Poll every second

  if (result == sensor.ku8MBSuccess) {
    // Clear previous content
    display.clearDisplay();
    
    // Set cursor to column 0, row 0
    display.setCursor(0, 0);
    display.setTextSize(1); // Normal 1:1 pixel scale
    display.setTextColor(SSD1306_WHITE); // Draw white text
    display.println(F("Soil Sensor Data:"));
    display.println(F(""));
    display.print(F("Temp:     "));
    display.print(temperature);
    display.println(" C");

    display.println(F(""));

    display.print(F("Moisture: "));
    display.print(humidity);
    display.println(" %");

    display.println(F(""));
    
    display.print(F("EC:       "));
    display.print(conductivity);
    display.println(" mS/cm");
    
    // Refresh the OLED display with new data
    display.display();
  } else {
    // Handle failed read, maybe clear screen and show error?
  }
  // Convert float to string for publishing
  char messageBuffer[20];

  if (result == sensor.ku8MBSuccess) {
    // Publish temperature
    dtostrf(temperature, 1, 2, messageBuffer);
    client.publish(temperatureTopic, messageBuffer);

    // Publish moisture
    dtostrf(humidity, 1, 2, messageBuffer);
    client.publish(moistureTopic, messageBuffer);

    // Publish conductivity
    dtostrf(conductivity, 6, 3, messageBuffer); // Adjusted precision to 3 decimal places for mS/cm.
    client.publish(conductivityTopic, messageBuffer);
  }

  delay(2000); // Consider longer delay for readability
}