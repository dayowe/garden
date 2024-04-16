#include <Wire.h>
#include "M5AtomS3.h"
#include <PubSubClient.h>
#include <ModbusMaster.h>
#include <WiFi.h>
#include "MQTTManager.h"
#include "WiFiManager.h"
#include "vcs3i2c.h" // Library for the I2C soil sensor

// Create a WiFiClient instance for the PubSubClient to use
WiFiClient espClient;

// Initialize the MQTT client with the WiFi client
PubSubClient mqttClient(espClient);

SVCS3 vcs; // Assuming this is the correct type for your sensor object.

// Instantiate the ModbusMaster object for Modbus RTU over RS485
ModbusMaster sensor;

#define RS485Serial Serial2  // Use Serial2 for RS485 communication

String message = ""; // Holds the message to be displayed

const long interval = 4000; // Interval at which to read sensors (in milliseconds)
unsigned long previousMillis = 0; // Last update time stamp

bool toggle = false;

enum CalibrationState {
    REGULAR,
    CALIBRATE_AIR_PROMPT,
    CALIBRATE_WATER_PROMPT,
    CALIBRATE_EC_PROMPT
};

CalibrationState state = REGULAR;

unsigned long buttonPressTime = 0; // Track how long the button is pressed
bool inCalibrationMode = false; // Flag to check if currently in calibration mode


// THC-S sensor stuff
const int maxSensors = 2; // Maximum number of Modbus sensors
int displaySensorID = 1;   // Sensor ID to display (and poll)
bool activeSensors[maxSensors] = {false}; // Array to keep track of active sensors

void setDefaultDisplayProperties() {
    // Set text size and color for the display
    AtomS3.Display.fillScreen(BLACK);
    // Set cursor to top left corner
    AtomS3.Display.setCursor(0, 0);
    AtomS3.Display.setTextSize(1);
    AtomS3.Display.setTextColor(WHITE); // Set text color
    AtomS3.Display.setTextWrap(true);
}

void displayError() {
    setDefaultDisplayProperties();
    AtomS3.Display.fillScreen(BLACK);
    AtomS3.Display.setCursor(0, 0);
    AtomS3.Display.println(message);
}

void displayMessage(String msg) {
    setDefaultDisplayProperties();
    AtomS3.Display.fillScreen(BLACK);
    AtomS3.Display.setCursor(0, 0);
    AtomS3.Display.println(msg);
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

void readAndPublishSensorData(int sensorID) {
  sensor.begin(sensorID, RS485Serial);
  uint8_t result = sensor.readHoldingRegisters(0x0000, 3); // Attempt to read three registers from the sensor
  setDefaultDisplayProperties();
  // Clear and setup the display
  AtomS3.Display.clearDisplay();
  AtomS3.Display.setTextSize(1);
  AtomS3.Display.setCursor(0,0);

  AtomS3.Display.print("THC-S Sensor ID: ");
  AtomS3.Display.println(sensorID);

  AtomS3.Display.println(F("\n"));

  if (result == sensor.ku8MBSuccess) {
    // If read succeeds, process and display the data
    float humidity = sensor.getResponseBuffer(0) / 10.0; // Convert to actual value
    float vwc = -0.0020844495456097786 * humidity * humidity + 0.8758395803818368 * humidity -0.007765958483453483;
    float temperature = sensor.getResponseBuffer(1) / 10.0; // Convert to actual value
    float conductivity = sensor.getResponseBuffer(2); // 1000.0; // Convert to actual value
    
    // Additional calculation for Pore Water EC using Hilhorst model
    float epsilon_b = 1.3088 + 0.1439 * humidity + 0.0076 * pow(humidity, 2);
    float poreWaterEC = calculatePoreWaterEC(conductivity, epsilon_b, temperature, 4.1); // 4.1 is esb_0 for coco coir

    AtomS3.Display.print("RAW: ");
    AtomS3.Display.print(humidity);
    AtomS3.Display.println("%");
    AtomS3.Display.println(F(""));
    AtomS3.Display.print("VWC: ");
    AtomS3.Display.print(vwc);
    AtomS3.Display.println("%");
    AtomS3.Display.println(F(""));
    AtomS3.Display.print("Temp: ");
    AtomS3.Display.print(temperature);
    AtomS3.Display.println(" C");
    AtomS3.Display.println(F(""));
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
  delay(2000);
}


void displaySensorValues() {
    vcs.newReading(); 
    float e25 = vcs.getE25();
    float ec = vcs.getEC();
    float temp = vcs.getTemp();
    float vwc = vcs.getVWC();

    // Create specific topics for each sensor value
    char e25Topic[100], ecTopic[100], tempTopic[100], vwcTopic[100];
    snprintf(e25Topic, sizeof(e25Topic), "%sE25", BASE_TOPIC);
    snprintf(ecTopic, sizeof(ecTopic), "%sEC", BASE_TOPIC);
    snprintf(tempTopic, sizeof(tempTopic), "%sTemp", BASE_TOPIC);
    snprintf(vwcTopic, sizeof(vwcTopic), "%sVWC", BASE_TOPIC);

    // Publish each sensor value to its specific topic
    publishSensorData(mqttClient, e25Topic, e25);
    publishSensorData(mqttClient, ecTopic, ec);
    publishSensorData(mqttClient, tempTopic, temp);
    publishSensorData(mqttClient, vwcTopic, vwc);
    
    // Clear the display
    setDefaultDisplayProperties();

    AtomS3.Display.println(F("Tinovi\n"));
    AtomS3.Display.println(F(""));
    // Display the values
    AtomS3.Display.printf("E25: %.2f\n", e25);
    AtomS3.Display.println(F(""));
    AtomS3.Display.printf("EC: %.2f mS/m\n", ec);
    AtomS3.Display.println(F(""));
    AtomS3.Display.printf("Temp: %.2f C\n", temp);
    AtomS3.Display.println(F(""));
    AtomS3.Display.printf("VWC: %.2f %%", vwc);
}

void displayCalibrationPrompt() {
    // Clear the display
    setDefaultDisplayProperties();
    
    // Adjust message based on the state
    switch (state) {
        case CALIBRATE_AIR_PROMPT:
            AtomS3.Display.print("Calibrate Air\nLong Press to Calibrate");
            break;
        case CALIBRATE_WATER_PROMPT:
            AtomS3.Display.print("Calibrate Water\nLong Press to Calibrate");
            break;
        case CALIBRATE_EC_PROMPT:
            AtomS3.Display.print("Calibrate EC\nLong Press to Calibrate");
            break;
        default:
            break;
    }
}

void setup() {
    auto cfg = M5.config();
    AtomS3.begin(cfg);
    Serial.begin(115200);
    Wire.begin(38, 39); // Initialize custom I2C pins for Project 1 sensor

    pinMode(41, INPUT_PULLUP); // Initialize the button on GPIO 41 for Project 1

    // Initialize WiFi
    setupWiFi(); // Make sure to call this before checking WiFi status

    // Initialize MQTT
    setupMQTT(mqttClient);

    // Try to initialize the sensor from Project 1
    if (vcs.init(0x63, &Wire) != 0) {
        Serial.println("Sensor init failed from Project 1!");
    } else {
        Serial.println("Sensor from Project 1 initialized.");
    }

    // Begin RS485 communication for Project 2
    RS485Serial.begin(4800, SERIAL_8N1, 1, 2);

    // Set default display properties (assuming both projects use the same display settings)
    setDefaultDisplayProperties();

    // Detect Modbus sensors from Project 2
    detectSensors();

    // Check WiFi connection status and display IP address
    if (WiFi.status() == WL_CONNECTED) {
        setDefaultDisplayProperties();
        AtomS3.Display.println("WiFi connected");
        AtomS3.Display.printf("IP: %s", WiFi.localIP().toString().c_str());
    } else {
        AtomS3.Display.println("WiFi NOT connected");
        // Handle failed connection if necessary
    }

    // Additional setup for Project 2 if needed
    // If your RS485 transceiver has DE/RE pins, initialize them here
    // pinMode(DEREPin, OUTPUT);
    // digitalWrite(DEREPin, LOW);

    delay(2000); // Give some time for the user to see the messages
}

// Add an additional state to your CalibrationState enum
enum DisplayState {
    DISPLAY_SENSOR_VALUES,
    DISPLAY_READINGS,
    DISPLAY_ERROR,
    DISPLAY_CALIBRATION,
    // other states as necessary
};

// Add a global variable to track the display state
DisplayState displayState = DISPLAY_SENSOR_VALUES;


void loop() {
    // Handle WiFi and MQTT for both projects
    handleWiFi();
    if (!mqttClient.connected()) {
        bool result = reconnectMQTT(mqttClient);
        if (result) {
            message = "MQTT connected";
            if (state == REGULAR) {
                displayState = DISPLAY_SENSOR_VALUES; // Only set this if we are in REGULAR state
            }
        } else {
            message = "MQTT NOT connected";
            displayState = DISPLAY_ERROR; // Switch to error display if MQTT is not connected
        }
        displayMessage(message); // Show the current MQTT status on the display
    } else {
        message = "MQTT connected";
        handleMQTT(mqttClient);
    }

    AtomS3.update();

    // Button press handling
    if (digitalRead(41) == LOW) {
        if (buttonPressTime == 0) {
            buttonPressTime = millis();
        } else if (millis() - buttonPressTime > 3000) {
            switch (state) {
                case CALIBRATE_AIR_PROMPT:
                    vcs.calibrationAir();
                    displayState = DISPLAY_CALIBRATION;
                    displayMessage("Calibrating Air...");
                    delay(2000);
                    state = REGULAR;
                    break;
                case CALIBRATE_WATER_PROMPT:
                    vcs.calibrationWater();
                    displayState = DISPLAY_CALIBRATION;
                    displayMessage("Calibrating Water...");
                    delay(2000);
                    state = REGULAR;
                    break;
                case CALIBRATE_EC_PROMPT:
                    vcs.calibrationEC(1413);
                    displayState = DISPLAY_CALIBRATION;
                    displayMessage("Calibrating EC...");
                    delay(2000);
                    state = REGULAR;
                    break;
                default:
                    state = CALIBRATE_AIR_PROMPT;
                    break;
            }
            inCalibrationMode = true;
            buttonPressTime = 0;
        }
    } else {
        if (buttonPressTime > 0 && millis() - buttonPressTime < 3000) {
            if (!inCalibrationMode) {
                switch (state) {
                    case CALIBRATE_AIR_PROMPT:
                        state = CALIBRATE_WATER_PROMPT;
                        break;
                    case CALIBRATE_WATER_PROMPT:
                        state = CALIBRATE_EC_PROMPT;
                        break;
                    case CALIBRATE_EC_PROMPT:
                        state = REGULAR;
                        displayState = DISPLAY_SENSOR_VALUES; // Set the display state back to sensor values
                        break;
                    default:
                        state = CALIBRATE_AIR_PROMPT;
                        break;
                }
            } else {
                inCalibrationMode = false;
            }
        }
        buttonPressTime = 0;
    }

    // Timing for sensor reading and display toggling
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        if (activeSensors[displaySensorID - 1]) {
            if (toggle) {
                displayState = DISPLAY_READINGS;
            } else {
                displayState = DISPLAY_SENSOR_VALUES;
            }
            toggle = !toggle; // Toggle the state
        }
    }


    // Update the display based on the current state
    switch (displayState) {
        case DISPLAY_READINGS:
            if (!toggle) { // Only display sensor values when toggle is false
                displaySensorValues();
            }
            break;
        case DISPLAY_SENSOR_VALUES:
            readAndPublishSensorData(displaySensorID);
            // Cycle through sensors for the next reading
            do {
                displaySensorID++;
                if (displaySensorID > maxSensors) displaySensorID = 1;
            } while (!activeSensors[displaySensorID - 1]);
            displayState = DISPLAY_SENSOR_VALUES; // Once data is read, prepare to display sensor values next
            break;
        case DISPLAY_CALIBRATION:
            displayCalibrationPrompt();
            break;
        case DISPLAY_ERROR:
            displayError();
            break;
        default:
            break;
    }

    // Add a small delay to reduce workload on the ESP32
    delay(100); // This delay is a compromise between the delays of both projects
}