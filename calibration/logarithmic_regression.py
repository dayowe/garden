"""
logarithmic_regression.py

This script fits a logarithmic regression model to a dataset of humidity and Volumetric Water Content (VWC) values.
The data is sourced from environment variables 'HUMIDITY_VALS' and 'VWC_VALS', which should contain comma-separated
numerical values. The script assumes there are no zero or negative values in the humidity data, as these are incompatible
with the logarithmic function used for fitting.

The fitted parameters of the logarithmic function are outputted, which can be used to predict VWC from new humidity readings.

Pre-requisites:
- Ensure that 'HUMIDITY_VALS' and 'VWC_VALS' are set in your environment variables with valid, positive numerical values.
- Required Python packages: numpy, scipy, matplotlib, python-dotenv

Usage:
1. Set the required environment variables with your data.
2. Run this script in a Python environment where the necessary packages are installed.
3. Check the console output for the fitted parameters.
"""

import numpy as np
from scipy.optimize import curve_fit
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Retrieve and format data from environment variables
raw = np.array(os.getenv('RAW').split(', '), dtype=np.float64)
true_vwc = np.array(os.getenv('VWC').split(', '), dtype=np.float64)

# Define the logarithmic function to fit
# Note: Logarithmic functions are undefined for non-positive values
def logarithmic_function(x, a, b):
    return a + b * np.log(x)

# Provide an initial guess for the parameters a and b
initial_guess = [1, 1]

# Filter out non-positive humidity values to avoid errors with the logarithmic function
pos_indices = raw > 0
raw_positive = raw[pos_indices]
true_vwc_positive = true_vwc[pos_indices]

# Perform the curve fitting
params, _ = curve_fit(logarithmic_function, raw_positive, true_vwc_positive, p0=initial_guess)

# Output the fitted parameters
print(f"The fitted parameters for the logarithmic regression are: {params}")

# Use a finer grid for plotting the fitted logarithmic curve
raw_for_curve = np.linspace(min(raw_positive), max(raw_positive), 200)
fitted_values_for_curve = logarithmic_function(raw_for_curve, *params)

# Predict the VWC values using the logarithmic function model
predicted_vwc = logarithmic_function(raw_positive, *params)

# Calculate residuals
residuals = true_vwc_positive - predicted_vwc

# Calculate Mean Squared Error and Root Mean Squared Error
mse = np.mean(residuals**2)
rmse = np.sqrt(mse)
sem = np.std(residuals) / np.sqrt(len(residuals))

print(f"MSE: {mse:.8f}")
print(f"RMSE: {rmse:.8f}")
print(f"SEM: {sem:.8f}")

# Plot the original data and the fitted logarithmic curve, and residuals
plt.figure(figsize=(15, 7))

# Original Data and Logarithmic Fit Plot
plt.subplot(1, 3, 1)
plt.scatter(raw_positive, true_vwc_positive, color='blue', label='Actual VWC')
plt.plot(raw_for_curve, fitted_values_for_curve, 'r-', label=f'Logarithmic Fit: $f(x) = {params[0]:.2f} + {params[1]:.2f} \log(x)$')
plt.xlabel('Sensor Readings')
plt.ylabel('Volumetric Water Content (VWC)')
plt.title('Sensor Readings vs. VWC')
plt.legend()

# Predicted VWC vs. Actual VWC
plt.subplot(1, 3, 2)
plt.scatter(true_vwc_positive, predicted_vwc, color='green', label='Predicted VWC')
plt.plot([true_vwc_positive.min(), true_vwc_positive.max()], [true_vwc_positive.min(), true_vwc_positive.max()], 'k--', lw=2, label='Perfect Prediction')
plt.xlabel('Actual VWC')
plt.ylabel('Predicted VWC')
plt.title('Actual vs. Predicted VWC')
plt.legend()

# Residuals vs Predicted VWC
plt.subplot(1, 3, 3)
plt.scatter(predicted_vwc, residuals, color='purple')
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted VWC')
plt.ylabel('Residuals')
plt.title(f'Residuals vs. Predicted VWC\nMSE: {mse:.8f} | RMSE: {rmse:.8f} | SEM: {sem:.8f}')

plt.tight_layout()
plt.show()
