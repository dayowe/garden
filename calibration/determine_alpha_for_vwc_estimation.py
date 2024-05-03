"""
This script is tailored for the determination of the alpha parameter, a crucial factor in the estimation of 
Volumetric Water Content (VWC) from dielectric permittivity readings. The alpha parameter defines the non-linearity
in the relationship between the dielectric permittivity of the soil and the VWC. It is used in the following equation:

    VWC = θs * ((ϵ - ϵs) / (ϵw - ϵs))^1/α

Where:
    - VWC is the Volumetric Water Content, the target variable for prediction.
    - θs is the saturated soil water content, or the maximum VWC when completely saturated.
    - ϵ is the measured dielectric permittivity of the soil.
    - ϵs is the dielectric permittivity of the dry soil.
    - ϵw is the dielectric permittivity of water.
    - α is the empirically determined parameter that this script aims to calculate.

By obtaining the alpha parameter through curve fitting of empirical data, we can create a model that 
allows for the estimation of soil moisture content based on permittivity measurements gathered in the field 
using soil moisture sensors. This script performs linear regression on VWC and dielectric permittivity data,
plots the results for visualization, and outputs the alpha value for use in the above equation.

Before executing this script, make sure to install the required packages:
- numpy: For numerical operations and array handling.
- matplotlib: For data visualization.
- scipy: For performing the curve fitting.

These packages can be installed with the following command:
`pip install numpy matplotlib scipy`

Usage:
Ensure that the .env file containing the 'VWC_VALS' and 'DP_VALS' is in the same directory as this script.
Then run the script using:
`python determine_alpha_for_vwc_estimation.py`
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Assuming the .env file has the VWC and DP data as comma-separated strings
VWC_vals_str = os.getenv("VWC_VALS")
DP_vals_str = os.getenv("DP_VALS")

# Convert the comma-separated strings into numpy arrays of floats
VWC = np.array([float(v) for v in VWC_vals_str.split(',')])
DP = np.array([float(d) for d in DP_vals_str.split(',')])

# Define the linear model function
def linear_model(VWC, alpha, beta):
        return alpha * VWC + beta

# Perform the curve fitting
params, covariance = curve_fit(linear_model, VWC, DP)

# Extract the fitted parameters (alpha and beta)
alpha_fitted, beta_fitted = params

# Generate VWC values for plotting the fitted curve
VWC_values_for_curve = np.linspace(min(VWC), max(VWC), 100)

# Calculate the fitted curve using the fitted parameters
fitted_curve = linear_model(VWC_values_for_curve, alpha_fitted, beta_fitted)

# Plot the original data and the fitted curve
plt.figure(figsize=(10, 5))
plt.scatter(VWC, DP, label='Observed Data')
plt.plot(VWC_values_for_curve, fitted_curve, 'r-', label=f'Fitted Line (alpha={alpha_fitted:.2f})')
plt.xlabel('Volumetric Water Content (VWC)')
plt.ylabel('Dielectric Permittivity (DP)')
plt.title('Linear Fit to Determine Alpha')
plt.legend()
plt.grid(True)
plt.show()

# Output the fitted alpha value
print(f"The fitted alpha value is: {alpha_fitted}")

