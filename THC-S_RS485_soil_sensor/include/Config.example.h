// Config.h
#ifndef CONFIG_H
#define CONFIG_H

#define SSID_NAME "SSID_NAME"
#define SSID_PASSWORD "SSID_PASSWORD"
#define MQTT_SERVER "x.x.x.x"
#define MQTT_PORT 1883
#define MQTT_USER "mqtt"
#define MQTT_PASSWORD "MQTT_PASSWORD"

#define BASE_TOPIC "soil/"
#define BUTTON_PIN 41

const long interval = 4000; // Interval at which to read sensors (in milliseconds)

#define SCREEN_WIDTH 128  // OLED display width
#define SCREEN_HEIGHT 64  // OLED display height

// ... any other configuration settings ...

#endif // CONFIG_H