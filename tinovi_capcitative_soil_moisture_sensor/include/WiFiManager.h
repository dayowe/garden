// WiFiManager.h
#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <WiFi.h> //Include WiFi library for ESP32
#include "Config.h" // Wi-Fi credentials stored in a separate file

void setupWiFi();
void handleWiFi();

#endif // WIFI_MANAGER_H
