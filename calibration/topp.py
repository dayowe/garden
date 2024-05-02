"""
# Soil Moisture Data Modeling Script

This script uses the Topp equation to model the relationship between soil volumetric
water content (VWC) and dielectric permittivity (DP). It loads data from environment
variables, fits the Topp polynomial equation to the data, and plots the results for
visualization. The script outputs the optimized coefficients of the model.

Dependencies: numpy, matplotlib, scipy, python-dotenv
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the values from the .env file
DP_vals_string = os.getenv('DP_VALS')
VWC_vals_string = os.getenv('HUMIDITY_VALS')

# Convert the string values to numpy arrays
DP_vals = np.array([float(x) for x in DP_vals_string.split(',')])
VWC_vals = np.array([float(x) for x in VWC_vals_string.split(',')])

# Define the Topp equation model function
def topp_equation(VWC, a0, a1, a2, a3):
        return a0 + a1*VWC + a2*VWC**2 + a3*VWC**3

# Provide initial guesses for the parameters
initial_guesses = [1, 1, 1, 1]  # Adjust these as needed based on your data

# Fit the Topp equation to your data
params, covariance = curve_fit(topp_equation, VWC_vals, DP_vals, p0=initial_guesses)

# Extract the fitted parameters
a0_fitted, a1_fitted, a2_fitted, a3_fitted = params

# Print the fitted parameters in the desired format
print(f"Fitted Topp Equation Coefficients: a0 = {a0_fitted}, a1 = {a1_fitted}, a2 = {a2_fitted}, a3 = {a3_fitted}")
print(f"a0={a0_fitted}\na1={a1_fitted}\na2={a2_fitted}\na3={a3_fitted}")

# Generate VWC values for plotting the fitted curve
VWC_values_for_curve = np.linspace(min(VWC_vals), max(VWC_vals), 100)

# Calculate the fitted curve using the Topp equation with the fitted parameters
fitted_curve = topp_equation(VWC_values_for_curve, a0_fitted, a1_fitted, a2_fitted, a3_fitted)

# Plot the original data and the fitted curve
plt.figure(figsize=(10, 5))
plt.scatter(VWC_vals, DP_vals, label='Observed Data')
plt.plot(VWC_values_for_curve, fitted_curve, 'r-', label='Fitted Topp Equation')
plt.xlabel('Volumetric Water Content (VWC)')
plt.ylabel('Dielectric Permittivity (DP)')
plt.title('Fit of Topp Equation to Empirical Data')
plt.legend()
plt.grid(True)
plt.show()
