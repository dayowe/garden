#include <Wire.h>
#include "M5AtomS3.h"
#include <PubSubClient.h>
#include <ModbusMaster.h>
#include <WiFi.h>    //Include WiFi library for ESP32
#include "MQTTManager.h"
#include "WiFiManager.h"

// Instantiate the ModbusMaster object for Modbus RTU over RS485
ModbusMaster sensor;

#define RS485Serial Serial2  // Use Serial2 for RS485 communication

WiFiClient espClient; // Create an ESPClient object
PubSubClient mqttClient(espClient);

const int maxSensors = 2; // Maximum number of Modbus sensors
int displaySensorID = 1;   // Sensor ID to display (and poll)
bool activeSensors[maxSensors] = {false}; // Array to keep track of active sensors

unsigned long previousMillis = 0; // Last update time stamp

// Optional DE/RE pins for RS485 transceivers that require direction control
// Uncomment the following line if your RS485 transceiver requires DE/RE pin control
//const int DEREPin = xx; // DE/RE pin connected to the ESP32 (replace xx with the actual pin number)

// Function prototypes for calculating Pore Water EC
float calculatePoreWaterEC(float sb, float epsilon_b, float Tsoil, float esb_0);
float calculateRealPermittivityOfSoilPoreWater(float Tsoil);

void setDefaultDisplayProperties() {
    // Set text size and color for the display
    AtomS3.Display.fillScreen(BLACK);
    // Set cursor to top left corner
    AtomS3.Display.setCursor(0, 0);
    AtomS3.Display.setTextSize(1);
    AtomS3.Display.setTextColor(WHITE); // Set text color
    AtomS3.Display.setTextWrap(true);
}

void detectSensors() {
  setDefaultDisplayProperties();
  AtomS3.Display.println(F("Detecting Sensors..."));
  delay(1000);
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

// Clear the display and show the detection results
  setDefaultDisplayProperties();
  AtomS3.Display.print("Detection complete. Detected ");
  AtomS3.Display.print(detectedSensors);
  AtomS3.Display.println(" sensor(s).");
}

void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqttClient.connect("ESP32Client", MQTT_USER, MQTT_PASSWORD)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000); // Wait 5 seconds before retrying
    }
  }
}

void setup() {
  auto cfg = M5.config();
  AtomS3.begin(cfg);
  Serial.begin(115200);

  // Initialize WiFi
  setupWiFi(); // Make sure to call this before checking WiFi status

  // Clear the display
  setDefaultDisplayProperties();
  // Check WiFi connection status
  if (WiFi.status() == WL_CONNECTED) {
      AtomS3.Display.println("WiFi connected");
      AtomS3.Display.printf("IP: %s", WiFi.localIP().toString().c_str());
  } else {
      AtomS3.Display.println("WiFi NOT connected");
      // At this point, you may want to handle the failed connection
  }
  delay(1000); // Give some time for the user to see the message

  // Display a simple message
    AtomS3.Display.fillScreen(BLACK); // Clear the screen
    AtomS3.Display.setCursor(0, 0);   // Reset cursor position
    AtomS3.Display.println("Hello World");

  // Initialize MQTT and display status
  setupMQTT(mqttClient);
  //reconnectMQTT(mqttClient); // Ensure you're connected to MQTT and update display accordingly

  RS485Serial.begin(4800, SERIAL_8N1, 1, 2); // Initialize RS485 communication

  AtomS3.Display.fillScreen(BLACK); // Clear the screen
  AtomS3.Display.setCursor(0, 0);   // Reset cursor position
  // Now detect Sensors: Scans and identifies active sensors
  AtomS3.Display.fillScreen(BLACK);
  AtomS3.Display.setCursor(0, 0);
  AtomS3.Display.println(F("Detecting Sensors..."));
  delay(1000);
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

// Clear the display and show the detection results
  setDefaultDisplayProperties();
  AtomS3.Display.print("Detection complete. Detected ");
  AtomS3.Display.print(detectedSensors);
  AtomS3.Display.println(" sensor(s).");

    // Find and set the first active sensor to display after detection
    displaySensorID = -1; // Initialize with an invalid sensor ID
    for (int i = 0; i < maxSensors; i++) {
      if (activeSensors[i]) {
        displaySensorID = i + 1; // Adjust displaySensorID to the first active sensor
        break;
      }
    }
  
    // If no sensors are active, consider handling this scenario
    if (displaySensorID == -1) {
      AtomS3.Display.println("No sensors detected.");
    } else {
      // If sensors are detected, you can display the sensor information here
    }

  // Find and set the first active sensor to display after detection
  for (int i = 0; i < maxSensors; i++) {
    if (activeSensors[i]) {
      displaySensorID = i + 1; // Adjust displaySensorID to the first active sensor
      break;
    }
  }
  
  // If no sensors are active, consider handling this scenario
  if (displaySensorID == -1) {
    AtomS3.Display.print("No sensors detected.");
  }
}

void readAndPublishSensorData(int sensorID) {
  sensor.begin(sensorID, RS485Serial);
  uint8_t result = sensor.readHoldingRegisters(0x0000, 3); // Attempt to read three registers from the sensor
  
  // Clear and setup the display
  AtomS3.Display.clearDisplay();
  AtomS3.Display.setTextSize(1);
  AtomS3.Display.setCursor(0,0);

  AtomS3.Display.print("Sensor ID: ");
  AtomS3.Display.println(sensorID);

  AtomS3.Display.println(F(""));

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

    //AtomS3.Display.print("Hum: ");
    //AtomS3.Display.print(humidity);
    //AtomS3.Display.println("%");
    AtomS3.Display.print("VWC: ");
    AtomS3.Display.print(vwc);
    AtomS3.Display.println("%");
    AtomS3.Display.println(F(""));
    AtomS3.Display.print("Temp: ");
    AtomS3.Display.print(temperature);
    AtomS3.Display.println(" C");
    AtomS3.Display.println(F(""));
    //AtomS3.Display.print("Cond: ");
    //AtomS3.Display.print(conductivity);
    //AtomS3.Display.println(" uS/cm");
    AtomS3.Display.print("pwEC: ");
    AtomS3.Display.print(poreWaterEC);
    AtomS3.Display.println(" uS/cm");

    // Prepare MQTT topics and messages
    char topic[100];
    char messageBuffer[20];

    snprintf(topic, sizeof(topic), "%sthcs%d/temperature", BASE_TOPIC, sensorID);
    dtostrf(temperature, 1, 2, messageBuffer);
    mqttClient.publish(topic, messageBuffer);
    
    snprintf(topic, sizeof(topic), "%sthcs%d/moisture", BASE_TOPIC, sensorID);
    dtostrf(humidity, 1, 2, messageBuffer);
    mqttClient.publish(topic, messageBuffer);

    snprintf(topic, sizeof(topic), "%sthcs%d/conductivity", BASE_TOPIC, sensorID);
    dtostrf(conductivity, 6, 3, messageBuffer);
    mqttClient.publish(topic, messageBuffer);

    // Publish Pore Water EC as well
    snprintf(topic, sizeof(topic), "%sthcs%d/poreWaterEC", BASE_TOPIC, sensorID);
    dtostrf(poreWaterEC, 6, 3, messageBuffer); // Pore Water EC topic and message
    mqttClient.publish(topic, messageBuffer);
  } else {
    // Handle failed sensor read
    Serial.print("Failed to read from sensor ");
    Serial.println(sensorID);
    AtomS3.Display.println("Read failed!");
  }
}


// Calculate the real portion of the dielectric permittivity of soil pore water
float calculateRealPermittivityOfSoilPoreWater(float Tsoil) {
    Serial.print("calculateRealPermittivityOfSoilPoreWater: ");
    Serial.print(80.3 - 0.37 * (Tsoil - 20));
    Serial.println("");
    // Adapted from the Hilhorst model
    return 80.3 - 0.37 * (Tsoil - 20);
}

// Calculate the Pore Water Electrical Conductivity
float calculatePoreWaterEC(float sb, float epsilon_b, float Tsoil, float esb_0) {
    float ew = calculateRealPermittivityOfSoilPoreWater(Tsoil);
    Serial.print("calculatePoreWaterEC: ");
    Serial.print((ew * sb) / (epsilon_b - esb_0));
    Serial.println("");
    // Apply the Hilhorst model formula
    return (ew * sb) / (epsilon_b - esb_0);
}



void loop() {
  handleWiFi();
  handleMQTT(mqttClient);

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
  delay(3000);
}
