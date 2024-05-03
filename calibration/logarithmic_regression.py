"""
logarithmic_regression.py

This script fits a logarithmic regression model to a dataset of humidity and Volumetric Water Content (VWC) values.
The data is sourced from environment variables 'HUMIDITY_VALS' and 'VWC_VALS', which should contain comma-separated
numerical values. The script assumes there are no zero or negative values in the humidity data, as these are incompatible
with the logarithmic function used for fitting.

The fitted parameters of the logarithmic function are outputted, which can be used to predict VWC from new humidity readings.

Pre-requisites:
- Ensure that 'HUMIDITY_VALS' and 'VWC_VALS' are set in your environment variables with valid, positive numerical values.
- Required Python packages: numpy, scipy

Usage:
1. Set the required environment variables with your data.
2. Run this script in a Python environment where the necessary packages are installed.
3. Check the console output for the fitted parameters.
"""

import numpy as np
from scipy.optimize import curve_fit
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve and format data from environment variables
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(', '), dtype=np.float64)
vwc_vals = np.array(os.getenv('VWC_VALS').split(', '), dtype=np.float64)

# Define the logarithmic function to fit
# Note: Logarithmic functions are undefined for non-positive values
def logarithmic_function(x, a, b):
    return a + b * np.log(x)

# Provide an initial guess for the parameters a and b
initial_guess = [1, 1]

# Filter out non-positive humidity values to avoid errors with the logarithmic function
pos_indices = humidity_vals > 0
humidity_vals_positive = humidity_vals[pos_indices]
vwc_vals_positive = vwc_vals[pos_indices]

# Perform the curve fitting
params, _ = curve_fit(logarithmic_function, humidity_vals_positive, vwc_vals_positive, p0=initial_guess)

# Output the fitted parameters
print(f"The fitted parameters for the logarithmic regression are: {params}")
