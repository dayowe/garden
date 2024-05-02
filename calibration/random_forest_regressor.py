import os
import numpy as np
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Load environment variables
load_dotenv()

# Retrieve data from environment variables
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(', '), dtype=np.float64)
vwc_vals = np.array(os.getenv('VWC_VALS').split(', '), dtype=np.float64)

# Reshape data for model fitting
X = humidity_vals.reshape(-1, 1)
y = vwc_vals

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Random Forest Regressor
rf_regressor = RandomForestRegressor(random_state=42)
rf_regressor.fit(X_train, y_train)

# Function to make a prediction based on sensor readings
def predict_vwc(sensor_reading):
    sensor_reading = np.array([sensor_reading]).reshape(-1, 1)
    predicted_vwc = rf_regressor.predict(sensor_reading)
    return predicted_vwc[0]

# Main program to accept sensor input and make a prediction
if __name__ == "__main__":
    # Ask for a new sensor reading
    sensor_input = float(input("Enter the sensor humidity reading: "))
    predicted_vwc = predict_vwc(sensor_input)
    print(f"The predicted VWC for a humidity reading of {sensor_input} is {predicted_vwc}")

