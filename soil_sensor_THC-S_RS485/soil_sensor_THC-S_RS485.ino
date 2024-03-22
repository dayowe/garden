#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <PubSubClient.h>
#include <ModbusMaster.h>
#include <WiFi.h>
#include "WiFiCredentials.h"
#include "mqttCredentials.h"

// MQTT Topics base
const char* baseTopic = "soil/";

// Instantiate ModbusMaster object
ModbusMaster sensor;

#define RS485Serial Serial2
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire);

WiFiClient espClient;
PubSubClient client(espClient);

const int maxSensors = 8;
int displaySensorID = 1;
bool activeSensors[maxSensors] = {false};

unsigned long previousMillis = 0;
const long interval = 2000;

void preTransmission() {}
void postTransmission() {}

void setup() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to WiFi");
  client.setServer(mqttServer, mqttPort);

  Serial.begin(115200);
  RS485Serial.begin(4800, SERIAL_8N1, 16, 17);

  sensor.preTransmission(preTransmission);
  sensor.postTransmission(postTransmission);

  // Initialize OLED display
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  display.display(); // Show initial screen (blank or splash screen)
  delay(2000); // Short delay before clearing display

  // Detect Sensors
  detectSensors();
}

void detectSensors() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println(F("Detecting Sensors..."));
  display.display();

  int detectedSensors = 0;

  for (int sensorID = 1; sensorID <= maxSensors; sensorID++) {
    sensor.begin(sensorID, RS485Serial);
    uint8_t result = sensor.readHoldingRegisters(0x0000, 1);
    if (result == sensor.ku8MBSuccess) {
      activeSensors[sensorID - 1] = true;
      Serial.print("Sensor detected: ID ");
      Serial.println(sensorID);
      detectedSensors++; // Increment the count for each detected sensor
    }
    // without short delay only first sensor is detected
    delay(20);
  }

  // Move the completion message here, outside the loop, using detectedSensors variable
  display.clearDisplay();  // Clearing the display again for showing completion status
  display.setCursor(0,0);
  display.print("Detection complete. Detected ");
  display.print(detectedSensors); // Using detectedSensors variable here
  display.println(" sensors.");
  display.display(); 
  delay(2000);
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
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    // Only read and publish if the sensor is active
    if (activeSensors[displaySensorID - 1]) {
      readAndPublishSensorData(displaySensorID);

      // Moving to next sensor
      do {
        displaySensorID++;
        if (displaySensorID > maxSensors) {
          displaySensorID = 1;
        }
      } while (!activeSensors[displaySensorID - 1]);
    }
  }
}

void readAndPublishSensorData(int sensorID) {
  sensor.begin(sensorID, RS485Serial);
  uint8_t result = sensor.readHoldingRegisters(0x0000, 3);

  // Initialize display for new data presentation
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);

  // Always display the Sensor ID
  display.print("Sensor ID: ");
  display.println(sensorID);

  display.println(F(""));

  if (result == sensor.ku8MBSuccess) {
    float humidity = sensor.getResponseBuffer(0) / 10.0;
    float temperature = sensor.getResponseBuffer(1) / 10.0;
    float conductivity = sensor.getResponseBuffer(2) / 1000.0;

    // Log to serial for debug purposes
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println("% RH");
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println("°C");
    Serial.print("Conductivity: ");
    Serial.print(conductivity);
    Serial.println(" mS/cm");

    // Display sensor values on the OLED
    display.print("Hum: ");
    display.print(humidity);
    display.println("% RH");
    display.println(F(""));
    display.print("Temp: ");
    display.print(temperature);
    display.println(" C");
    display.println(F(""));
    display.print("Cond: ");
    display.print(conductivity);
    display.println(" mS/cm");

    // Construct MQTT topics and publish sensor data
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
  } else {
    Serial.print("Failed to read from sensor ");
    Serial.println(sensorID);
    // Optionally, you can also inform on the OLED screen about the failure
    display.println("Read failed!");
  }

  // Final step to actually show the data
  display.display();
}