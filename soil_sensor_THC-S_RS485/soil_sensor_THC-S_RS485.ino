#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <PubSubClient.h>
#include <ModbusMaster.h>
#include <WiFi.h>    //Include WiFi library for ESP32
#include "WiFiCredentials.h" // Wi-Fi credentials stored in a separate file
#include "mqttCredentials.h" // MQTT credentials stored in a separate file

// Base topic for MQTT publications
const char* baseTopic = "soil/";

// Instantiate the ModbusMaster object for Modbus RTU over RS485
ModbusMaster sensor;

#define RS485Serial Serial2  // Use Serial2 for RS485 communication
#define SCREEN_WIDTH 128  // OLED display width
#define SCREEN_HEIGHT 64  // OLED display height

// Declaration for an SSD1306 display connected to I2C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire);

WiFiClient espClient; // Create an ESPClient object
PubSubClient client(espClient); // Pass the ESPClient to PubSubClient for MQTT

const int maxSensors = 8; // Maximum number of Modbus sensors
int displaySensorID = 1;   // Sensor ID to display (and poll)
bool activeSensors[maxSensors] = {false}; // Array to keep track of active sensors

unsigned long previousMillis = 0; // Last update time stamp
const long interval = 4000; // Interval at which to read sensors (in milliseconds)

// Optional DE/RE pins for RS485 transceivers that require direction control
// Uncomment the following line if your RS485 transceiver requires DE/RE pin control
//const int DEREPin = xx; // DE/RE pin connected to the ESP32 (replace xx with the actual pin number)

// Function prototypes for calculating Pore Water EC
float calculatePoreWaterEC(float sb, float epsilon_b, float Tsoil, float esb_0);
float calculateRealPermittivityOfSoilPoreWater(float Tsoil);

// Callbacks for Modbus transmission
void preTransmission() {
  // Optional DE/RE control. Uncomment the line below if using DE/RE pins
  // digitalWrite(DEREPin, HIGH); // Enable Driver (DE) for transmission 
}
void postTransmission() {
  // Optional DE/RE control. Uncomment the line below if using DE/RE pins
  // digitalWrite(DEREPin, LOW); // Disable Driver (RE) - Enable Receiver
}

void setup() {
  WiFi.begin(ssid, password); // Connect to Wi-Fi using credentials from "WiFiCredentials.h"
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to WiFi");

  client.setServer(mqttServer, mqttPort); // Set the MQTT broker details from "mqttCredentials.h"

  Serial.begin(115200);
  RS485Serial.begin(4800, SERIAL_8N1, 16, 17); // Initialize RS485 communication

  sensor.preTransmission(preTransmission);
  sensor.postTransmission(postTransmission);

  // Initialize OLED display
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Infinite loop
  }
  display.display();     // Display splash screen
  delay(2000);           // Wait before clearing display
  display.clearDisplay(); // Clear the display buffer

  // Detect Sensors: Scans and identifies active sensors
  detectSensors();

  // Find and set the first active sensor to display after detection
  for (int i = 0; i < maxSensors; i++) {
    if (activeSensors[i]) {
      displaySensorID = i + 1; // Adjust displaySensorID to the first active sensor
      break;
    }
  }
  
  // If no sensors are active, consider handling this scenario
  if (displaySensorID == -1) {
    Serial.println("No sensors detected.");
    // Additional handling here if needed
  }
}

void detectSensors() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println(F("Detecting Sensors..."));
  display.display();

  int detectedSensors = 0; // Initialize detected sensor count

  for (int sensorID = 1; sensorID <= maxSensors; sensorID++) {
    sensor.begin(sensorID, RS485Serial); // Initialize sensor with its ID
    uint8_t result = sensor.readHoldingRegisters(0x0000, 1); // Read a register to check for sensor presence
    if (result == sensor.ku8MBSuccess) { // If read is successful, sensor is present
      activeSensors[sensorID - 1] = true;
      Serial.print("Sensor detected: ID ");
      Serial.println(sensorID);
      detectedSensors++;
    }
    delay(20); // Short delay to ensure stable RS485 communication
  }

  // Display the completion message with detected sensor count
  display.clearDisplay();
  display.setCursor(0,0);
  display.print("Detection complete. \n\nDetected ");
  display.print(detectedSensors);
  display.println(" sensor(s).");
  display.display();

  delay(2000); // Short delay before the next action
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client", mqttUser, mqttPassword)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000); // Wait 5 seconds before retrying
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect(); // Ensure a constant connection to the MQTT broker
  }
  client.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    // Read and publish only if the sensor is active
    if (activeSensors[displaySensorID - 1]) {
      readAndPublishSensorData(displaySensorID);

      // Move to the next sensor, skip inactive ones
      do {
        displaySensorID++;
        if (displaySensorID > maxSensors) displaySensorID = 1;
      } while (!activeSensors[displaySensorID - 1]);
    }
  }
}

// Calculate the real portion of the dielectric permittivity of soil pore water
float calculateRealPermittivityOfSoilPoreWater(float Tsoil) {
    Serial.print("calculateRealPermittivityOfSoilPoreWater: ");
    Serial.print(80.3 - 0.37 * (Tsoil - 20));
    // Adapted from the Hilhorst model
    return 80.3 - 0.37 * (Tsoil - 20);
}

// Calculate the Pore Water Electrical Conductivity
float calculatePoreWaterEC(float sb, float epsilon_b, float Tsoil, float esb_0) {
    float ew = calculateRealPermittivityOfSoilPoreWater(Tsoil);
    Serial.print("calculatePoreWaterEC: ");
    Serial.print((ew * sb) / (epsilon_b - esb_0));
    // Apply the Hilhorst model formula
    return (ew * sb) / (epsilon_b - esb_0);
}

void readAndPublishSensorData(int sensorID) {
  sensor.begin(sensorID, RS485Serial);
  uint8_t result = sensor.readHoldingRegisters(0x0000, 3); // Attempt to read three registers from the sensor
  
  // Clear and setup the display
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);

  display.print("Sensor ID: ");
  display.println(sensorID);

  display.println(F(""));

  if (result == sensor.ku8MBSuccess) {
    // If read succeeds, process and display the data
    float humidity = sensor.getResponseBuffer(0) / 10.0; // Convert to actual value
    float vwc = -0.0020844495456097786 * humidity * humidity + 0.8758395803818368 * humidity -0.007765958483453483;
    float temperature = sensor.getResponseBuffer(1) / 10.0; // Convert to actual value
    float conductivity = sensor.getResponseBuffer(2); // 1000.0; // Convert to actual value
    
    // Additional calculation for Pore Water EC using Hilhorst model
    float epsilon_b = 1.3088 + 0.1439 * humidity + 0.0076 * pow(humidity, 2);
    float poreWaterEC = calculatePoreWaterEC(conductivity, epsilon_b, temperature, 4.1); // 4.1 is esb_0 for coco coir

    // Log and display sensor data for debugging and info
    //Serial.print("Humidity: ");
    //Serial.print(humidity);
    //Serial.println("% RH");
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println("°C");
    Serial.print("Conductivity: ");
    Serial.print(conductivity);
    Serial.println(" uS/cm");
    Serial.print("pwEC: ");
    Serial.print(poreWaterEC);
    Serial.println(" uS/cm");

    Serial.print("Temperature: "); Serial.print(tempC); Serial.println("*C");
    Serial.print("Capacitive: "); Serial.println(capread);

    //display.print("Hum: ");
    //display.print(humidity);
    //display.println("%");
    display.print("VWC: ");
    display.print(vwc);
    display.println("%");
    display.println(F(""));
    display.print("Temp: ");
    display.print(temperature);
    display.println(" C");
    display.println(F(""));
    //display.print("Cond: ");
    //display.print(conductivity);
    //display.println(" uS/cm");
    display.print("pwEC: ");
    display.print(poreWaterEC);
    display.println(" uS/cm");

    // Prepare MQTT topics and messages
    char topic[100];
    char messageBuffer[20];

    snprintf(topic, sizeof(topic), "%sthcs%d/temperature", baseTopic, sensorID);
    dtostrf(temperature, 1, 2, messageBuffer);
    client.publish(topic, messageBuffer);
    
    snprintf(topic, sizeof(topic), "%sthcs%d/moisture", baseTopic, sensorID);
    dtostrf(humidity, 1, 2, messageBuffer);
    client.publish(topic, messageBuffer);

    snprintf(topic, sizeof(topic), "%sthcs%d/conductivity", baseTopic, sensorID);
    dtostrf(conductivity, 6, 3, messageBuffer);
    client.publish(topic, messageBuffer);

    // Publish Pore Water EC as well
    snprintf(topic, sizeof(topic), "%sthcs%d/poreWaterEC", baseTopic, sensorID);
    dtostrf(poreWaterEC, 6, 3, messageBuffer); // Pore Water EC topic and message
    client.publish(topic, messageBuffer);
  } else {
    // Handle failed sensor read
    Serial.print("Failed to read from sensor ");
    Serial.println(sensorID);
    display.println("Read failed!");
  }
  display.display(); // Display the updated sensor data on the OLED screen
}