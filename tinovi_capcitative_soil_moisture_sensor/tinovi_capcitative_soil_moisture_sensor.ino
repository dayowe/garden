#include "M5AtomS3.h"
#include "vcs3i2c.h" // library for the I2C soil sensor

String message = ""; // Holds the message to be displayed

// Initialize the soil sensor object
SVCS3 vcs;

void setup() {
    auto cfg = M5.config();
    AtomS3.begin(cfg);
    Wire.begin(38, 39); // Initialize custom I2C pins

    // Attempt to initialize the sensor with the specified I2C address and Wire instance
    if (vcs.init(0x63, &Wire) != 0) { // Assuming '!= 0' indicates failure based on your context
        message = "Sensor init failed!";
    } else {
        message = "Sensor initialized.";
    }

    // Set display configurations
    int textSize = AtomS3.Display.height() / 60; // Adjust for readability
    AtomS3.Display.setTextSize(textSize);
    AtomS3.Display.fillScreen(BLACK); // Clear the screen
    AtomS3.Display.setCursor(0, 0); // Set cursor to top-left
    AtomS3.Display.setTextColor(WHITE); // Set text color
    AtomS3.Display.setTextWrap(true);
}

void displayValues(float e25, float ec, float temp, float vwc){
  // First, clear the display
  AtomS3.Display.fillScreen(BLACK);
  
  // Set cursor to top left corner
  AtomS3.Display.setCursor(0, 0);
  
  // Display each of the sensor values
  AtomS3.Display.printf("E25: %.2f\n", e25);
  AtomS3.Display.printf("EC: %.2f mS/m\n", ec);
  AtomS3.Display.printf("Temp: %.2f C\n", temp);
  AtomS3.Display.printf("VWC: %.2f %%", vwc);
}

void loop() {
    // Only proceed if sensor initialization was successful
    if(message == "Sensor initialized."){
        // Gather new readings from the sensor
        vcs.newReading(); 
    
        // Get values from soil sensor and display them
        float e25 = vcs.getE25();
        float ec = vcs.getEC();
        float temp = vcs.getTemp();
        float vwc = vcs.getVWC();
    
        // Display the sensor values on AtomS3 screen
        displayValues(e25, ec, temp, vwc);
    } else {
        // If sensor initialization failed, show error message
        AtomS3.Display.fillScreen(BLACK);
        AtomS3.Display.setCursor(0, 0);
        AtomS3.Display.println(message);
    }

    delay(5000); // Update every 5 seconds to make it readable
}