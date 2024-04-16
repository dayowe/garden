// MQTTManager.cpp
#include "M5AtomS3.h"
#include "MQTTManager.h"
#include "Config.h"

// Forward declaration for the callback function
void mqttCallback(char* topic, byte* payload, unsigned int length);

void setupMQTT(PubSubClient& client) {
  client.setServer(MQTT_SERVER, MQTT_PORT); // Set the MQTT broker details from Config.h
  client.setCallback(mqttCallback); // Set the callback function
}

void handleMQTT(PubSubClient& client) {
    if (!client.connected()) {
        bool reconnected = reconnectMQTT(client);
        if (reconnected) {
            // If we just reconnected, resubscribe to the necessary topics here
            // client.subscribe("your/subscribe/topic");
        }
    }
    client.loop(); // This allows the client to process incoming messages and maintain its connection to the server
}

bool reconnectMQTT(PubSubClient& client) {
  if (client.connected()) {
    return true; // Already connected
  }

  Serial.print("Attempting MQTT connection...");

  String clientId = "ESP32Client-" + String(random(0xffff), HEX);
  if (client.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
    Serial.println("MQTT connected");
    // Subscribe to topics here if needed
    // client.subscribe("your/subscribe/topic");
    return true; // Successfully connected
  } else {
    Serial.print("MQTT connection failed, rc=");
    Serial.print(client.state());
    Serial.println(" try again in 5 seconds");
    // Note: It's generally a bad idea to use delay in a non-blocking loop; consider a non-blocking retry mechanism
    //delay(5000);
    return false; // Connection failed
  }
}

void publishSensorData(PubSubClient& client, const char* topic, float value) {
  char messageBuffer[20];
  dtostrf(value, 6, 3, messageBuffer); // Convert float to string
  boolean pubResult = client.publish(topic, messageBuffer);
  if (pubResult) {
    Serial.println("Publish successful:");
    Serial.println(topic);
    Serial.println(messageBuffer);
  } else {
    Serial.println("Publish failed:");
    // The following line will print the numeric reason for failure if available
    Serial.println(client.state());
  }
}

// Define the callback function
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Handle message arrived
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

