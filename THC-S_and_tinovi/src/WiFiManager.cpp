#include "WiFiManager.h"
#include "Config.h"

void connectToWiFi() {
    Serial.print("Connecting to Wi-Fi");
    WiFi.begin(SSID_NAME, SSID_PASSWORD);
    unsigned long startAttemptTime = millis();

    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
        // Wait 10 seconds for the Wi-Fi to connect
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Failed to connect to Wi-Fi. Please check your credentials");
    } else {
        Serial.println();
        Serial.println("Connected to Wi-Fi");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    }
}

void setupWiFi() {
    connectToWiFi();
}

void handleWiFi() {
    if (WiFi.status() != WL_CONNECTED) {
        static unsigned long lastAttemptTime = 0;
        unsigned long currentMillis = millis();
        
        // Try to reconnect every 30 seconds if not connected
        if (currentMillis - lastAttemptTime > 30000) {
            lastAttemptTime = currentMillis;
            connectToWiFi();
        }
    }
}