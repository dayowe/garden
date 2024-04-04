#include "M5AtomS3.h"
#include "vcs3i2c.h" // Library for the I2C soil sensor

String message = ""; // Holds the message to be displayed

// Initialize the soil sensor object
SVCS3 vcs;

enum CalibrationState {
    REGULAR,
    CALIBRATE_AIR_PROMPT,
    CALIBRATE_WATER_PROMPT,
    CALIBRATE_EC_PROMPT
};

CalibrationState state = REGULAR;
unsigned long buttonPressTime = 0; // Track how long the button is pressed
bool inCalibrationMode = false; // Flag to check if currently in calibration mode

void setup() {
    auto cfg = M5.config();
    AtomS3.begin(cfg);
    Wire.begin(38, 39); // Initialize custom I2C pins

    pinMode(41, INPUT_PULLUP); // Initialize the button on GPIO 41

    int textSize = AtomS3.Display.height() / 60; // Adjust for readability
    AtomS3.Display.setTextSize(textSize);
    AtomS3.Display.fillScreen(BLACK); // Clear the screen
    AtomS3.Display.setCursor(0, 0); // Set cursor to top-left
    AtomS3.Display.setTextColor(WHITE); // Set text color
    AtomS3.Display.setTextWrap(true);

    // Attempt to initialize the sensor with the specified I2C address and Wire instance
    if (vcs.init(0x63, &Wire) != 0) { // Assuming '!= 0' indicates failure based on your context
        message = "Sensor init failed!";
    } else {
        message = "Sensor initialized.";
    }
}

void loop() {
    if (digitalRead(41) == LOW) { // Button is pressed
        if (buttonPressTime == 0) { // Start timer if not already started
            buttonPressTime = millis();
        } else if (millis() - buttonPressTime > 3000) { // Check if button is pressed for more than 3 seconds
            // Long press actions
            switch (state) {
                case CALIBRATE_AIR_PROMPT:
                    vcs.calibrationAir();
                    displayMessage("Calibrating Air...");
                    delay(2000); // Simulate time taken for calibration
                    state = REGULAR;
                    break;
                case CALIBRATE_WATER_PROMPT:
                    vcs.calibrationWater();
                    displayMessage("Calibrating Water...");
                    delay(2000); // Simulate time taken for calibration
                    state = REGULAR;
                    break;
                case CALIBRATE_EC_PROMPT:
                    vcs.calibrationEC(1413);
                    displayMessage("Calibrating EC...");
                    delay(2000); // Simulate time taken for calibration
                    state = REGULAR;
                    break;
                default:
                    // Cycle through calibration UI without acting on regular state
                    state = CALIBRATE_AIR_PROMPT;
                    break;
            }
            inCalibrationMode = true; // Exiting calibration so set to false outside of this block
            buttonPressTime = 0; // Reset button timer
        }
    } else {
        if (buttonPressTime > 0 && millis() - buttonPressTime < 3000) { // Short press detected
            // Actions for short press, change state unless we're coming back from calibration
            if (!inCalibrationMode) {
                switch (state) {
                    case CALIBRATE_AIR_PROMPT:
                        state = CALIBRATE_WATER_PROMPT;
                        break;
                    case CALIBRATE_WATER_PROMPT:
                        state = CALIBRATE_EC_PROMPT;
                        break;
                    case CALIBRATE_EC_PROMPT:
                        state = REGULAR; // Go back to regular display after cycling through calibrations
                        break;
                    default:
                        state = CALIBRATE_AIR_PROMPT; // Default to start of calibration options
                        break;
                }
            } else {
                inCalibrationMode = false; // Reset calibration flag as we've handled the post-calibration press
            }
        }
        buttonPressTime = 0; // Reset button timer if the button is released
    }

    // State-based display
    if (state == REGULAR && message == "Sensor initialized.") {
        displaySensorValues();
    } else if (state != REGULAR) {
        displayCalibrationPrompt();
    } else {
        displayError();
    }

    delay(100); // Small delay to reduce button debounce issues
}

void displaySensorValues() {
    vcs.newReading(); 
    float e25 = vcs.getE25();
    float ec = vcs.getEC();
    float temp = vcs.getTemp();
    float vwc = vcs.getVWC();
    
    // Clear the display
    AtomS3.Display.fillScreen(BLACK);
    // Set cursor to top left corner
    AtomS3.Display.setCursor(0, 0);
    // Display the values
    AtomS3.Display.printf("E25: %.2f\n", e25);
    AtomS3.Display.printf("EC: %.2f mS/m\n", ec);
    AtomS3.Display.printf("Temp: %.2f C\n", temp);
    AtomS3.Display.printf("VWC: %.2f %%", vwc);
}

void displayCalibrationPrompt() {
    // Clear the display
    AtomS3.Display.fillScreen(BLACK);
    AtomS3.Display.setCursor(0, 0);
    
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

void displayError() {
    AtomS3.Display.fillScreen(BLACK);
    AtomS3.Display.setCursor(0, 0);
    AtomS3.Display.println(message);
}

void displayMessage(String msg) {
    AtomS3.Display.fillScreen(BLACK);
    AtomS3.Display.setCursor(0, 0);
    AtomS3.Display.println(msg);
}