"""
linear_gam_predictor.py

This script implements a Linear Generalized Additive Model (GAM) to predict an output variable from a single predictor variable.
It is specifically configured to predict Volumetric Water Content (VWC) from humidity readings. The script retrieves data from
environment variables, fits a Linear GAM to the data, and allows the user to input new readings for prediction.

Ensure that the 'HUMIDITY_VALS' and 'VWC_VALS' environment variables are set with comma-separated humidity and VWC values, respectively.
Before running, also make sure that all required Python packages are installed in your environment.

Usage:
1. Set 'HUMIDITY_VALS' and 'VWC_VALS' environment variables with your dataset.
2. Run the script in an environment with the required dependencies.
3. Input a new humidity reading when prompted to get the VWC prediction.
"""

import os
import numpy as np
from dotenv import load_dotenv
from pygam import LinearGAM
from sklearn.model_selection import train_test_split

# Load the environment variables
load_dotenv()

# Retrieve data from environment variables
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(', '), dtype=np.float64)
vwc_vals = np.array(os.getenv('VWC_VALS').split(', '), dtype=np.float64)

# Reshape data for model fitting
X = humidity_vals.reshape(-1, 1)
y = vwc_vals

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Generalized Additive Model
gam = LinearGAM().fit(X_train, y_train)

# Function to make a prediction based on sensor readings
def predict_vwc(sensor_reading):
    sensor_reading = np.array([sensor_reading]).reshape(-1, 1)
    predicted_vwc = gam.predict(sensor_reading)
    return predicted_vwc[0]

# Main program to accept sensor input and make a prediction
if __name__ == "__main__":
    # Ask for a new sensor reading
    sensor_input = float(input("Enter the sensor humidity reading: "))
    predicted_vwc = predict_vwc(sensor_input)
    print(f"The predicted VWC for a humidity reading of {sensor_input} is {predicted_vwc}")
