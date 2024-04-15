// MQTTManager.h
#ifndef MQTT_MANAGER_H
#define MQTT_MANAGER_H

#include <PubSubClient.h>
#include "Config.h" // Include MQTT credentials

// Function declaration
void setupMQTT(PubSubClient& client);
void handleMQTT(PubSubClient& client);
void reconnectMQTT(PubSubClient& client);
void publishSensorData(PubSubClient& client, const char* topic, float value);

#endif // MQTT_MANAGER_H
