// MQTTManager.cpp
#include "M5AtomS3.h"
#include "MQTTManager.h"
#include "Config.h"

void setupMQTT(PubSubClient& client) {
  client.setServer(MQTT_SERVER, MQTT_PORT); // Set the MQTT broker details from "mqttCredentials.h"
}

void handleMQTT(PubSubClient& client) {
    if (!client.connected()) {
        reconnectMQTT(client);
    }
    client.loop(); // This needs to be called regularly to allow MQTT client to process incoming messages and maintain its connection to the server
}

void reconnectMQTT(PubSubClient& client) {
  // If we're already connected, just exit the function
  if (client.connected()) {
    return;
  }

  Serial.print("Attempting MQTT connection...");

  // Attempt to connect with a unique client ID
  String clientId = "ESP32Client-" + String(random(0xffff), HEX);
  if (client.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
    Serial.println("MQTT connected");
    // Once connected, you might want to subscribe to a topic
    // client.subscribe("your/subscribe/topic");

    // Display MQTT connection status on the device
    AtomS3.Display.fillScreen(BLACK);
    AtomS3.Display.setCursor(0, 0);
    AtomS3.Display.println("MQTT connected");
    delay(2000);
  } else {
    Serial.print("MQTT connection failed, rc=");
    Serial.print(client.state());
    Serial.println(" try again in 5 seconds");

    // Display MQTT connection failure on the device
    AtomS3.Display.fillScreen(BLACK);
    AtomS3.Display.setCursor(0, 0);
    AtomS3.Display.println("MQTT NOT connected");

    // Wait 5 seconds before retrying
    delay(5000);
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
    Serial.println("Publish failed.");
    // The following line will print the numeric reason for failure if available
    Serial.println(client.state());
  }
}

