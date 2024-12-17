"""
power_curve_fitting.py

This script is designed to perform non-linear regression using a power function model. It fits the specified power function to the provided data points for humidity and volumetric water content (VWC) values.

The power function used for fitting is of the form:
    f(x) = a * x^b + c
where 'a', 'b', and 'c' are parameters to be determined by the curve fitting algorithm, 'x' represents the independent variable (humidity), and 'f(x)' is the dependent variable (VWC).

Prerequisites:
- NumPy: For handling numerical operations and data manipulation.
- SciPy: For utilizing the curve_fit function to perform non-linear regression.
- Python-dotenv: For loading environmental variables from a .env file, which contains the dataset.

To use this script, you will need to have a .env file with the humidity and VWC data points stored in the environment variables `RAW` and `TRUE_VWC`. The values should be listed as comma-separated strings.

The script performs the following steps:
1. Load the environmental variables from the .env file.
2. Parse the string of values into NumPy arrays.
3. Define the power function that models the relationship between humidity and VWC.
4. Use SciPy's curve_fit function to fit the power function to the data, providing an initial guess for the parameters.
5. Print the fitted parameters that best model the data according to the power function.

Example usage of the script:
`python power_curve_fitting.py`

After running the script, the fitted parameters for the power regression will be printed in the console.
"""

import numpy as np
from scipy.optimize import curve_fit
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt

load_dotenv()

# Retrieve humidity and VWC values from environment variables and convert them to NumPy arrays
RAW = np.array(os.getenv('RAW').split(', '), dtype=np.float64)
TRUE_VWC = np.array(os.getenv('VWC').split(', '), dtype=np.float64)

# Define the power function for curve fitting
def power_function(x, a, b, c):
    return a * np.power(x, b) + c

# Initial guesses for the power function parameters
initial_guess = [1, 0.5, 1]

# Perform the curve fitting using the power function and initial parameter guesses
params, _ = curve_fit(power_function, RAW, TRUE_VWC, p0=initial_guess, maxfev=10000)

# Print the fitted parameters for the power regression model, each on its own line
print("The fitted parameters for the power regression are:")
print(f"a (pre-exponential factor): {params[0]}")
print(f"b (exponent): {params[1]}")
print(f"c (vertical offset): {params[2]}")

# Use a finer grid for plotting the fitted power curve
RAW_for_curve = np.linspace(min(RAW), max(RAW), 200)
fitted_values_for_curve = power_function(RAW_for_curve, *params)

# Predict the VWC values using the power function model
predicted_VWC = power_function(RAW, *params)

# Calculate residuals
residuals = TRUE_VWC - predicted_VWC

# Calculate Mean Squared Error and Root Mean Squared Error
MSE = np.mean(residuals**2)
RMSE = np.sqrt(MSE)
SEM = np.std(residuals) / np.sqrt(len(residuals))

print(f"MSE: {MSE:.8f}")
print(f"RMSE: {RMSE:.8f}")
print(f"SEM: {SEM:.8f}")

# Plot the original data and the fitted power curve, and residuals
plt.figure(figsize=(15, 7))

# Original Data and Power Fit Plot
plt.subplot(1, 3, 1)
plt.scatter(RAW, TRUE_VWC, color='blue', label='Actual VWC')
plt.plot(RAW_for_curve, fitted_values_for_curve, 'r-', label=f'Power Fit: $f(x) = {params[0]:.2f}x^{params[1]:.2f} + {params[2]:.2f}$')
plt.xlabel('Sensor Readings')
plt.ylabel('Volumetric Water Content (VWC)')
plt.title('Sensor Readings vs. VWC')
plt.legend()

# Predicted VWC vs. Actual VWC
plt.subplot(1, 3, 2)
plt.scatter(TRUE_VWC, predicted_VWC, color='green', label='Predicted VWC')
plt.plot([TRUE_VWC.min(), TRUE_VWC.max()], [TRUE_VWC.min(), TRUE_VWC.max()], 'k--', lw=2, label='Perfect Prediction')
plt.xlabel('Actual VWC')
plt.ylabel('Predicted VWC')
plt.title('Actual vs. Predicted VWC')
plt.legend()

# Residuals vs Predicted VWC
plt.subplot(1, 3, 3)
plt.scatter(predicted_VWC, residuals, color='purple')
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted VWC')
plt.ylabel('Residuals')
plt.title(f'Residuals vs. Predicted VWC\nMSE: {MSE:.8f} | RMSE: {RMSE:.8f} | SEM: {SEM:.8f}')

plt.tight_layout()
plt.show()
