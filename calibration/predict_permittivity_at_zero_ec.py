"""
This script performs calibration of a sensor for measuring volumetric water content (VWC)
using empirical data. It loads environmental variables for humidity, true VWC, bulk electrical
conductivity (EC), and temperature from a .env file and ensures they have the same data length.
It defines a model function for calibration, fits the model to the data to find the permittivity
at zero EC, and prints out the result. This calibrated value can be saved for subsequent EC
calculations.

To run this script, the following Python packages must be installed:
- numpy: Used for numerical operations on arrays.
- scipy: Provides the curve fitting functionality.
- python-dotenv: Enables loading of environment variables from a .env file.

You can install these packages using pip with the following command:
`pip install numpy scipy python-dotenv`
"""

import os
import numpy as np
from scipy.optimize import curve_fit
from dotenv import load_dotenv

load_dotenv()

# Load environment variables and convert them to numpy arrays
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(','), dtype=float)
vwc_vals = np.array(os.getenv('VWC_VALS').split(','), dtype=float)
bulk_ec = np.array(os.getenv('BULK_EC').split(','), dtype=float)
temperature = np.array(os.getenv('TEMPERATURE').split(','), dtype=float)

# Check if the lengths of the arrays are the same
if not (len(humidity_vals) == len(vwc_vals) == len(bulk_ec) == len(temperature)):
    raise ValueError("All input data lists must be of the same length.")

# Define the model function for calibration; this needs to be adjusted based on the calibration method
# For example, a simple linear function might be used initially
def calibration_model(vwc, permittivity_at_zero_ec):
    return vwc * permittivity_at_zero_ec

# Perform the curve fitting
params, covariance = curve_fit(calibration_model, vwc_vals, bulk_ec)

# Extract the permittivity when bulk EC is zero
epsilon_sigma_b_0 = params[0]

print(f"Estimated dielectric permittivity when bulk EC is zero: {epsilon_sigma_b_0}")

# Save the calibrated value to .env or another file if needed
# with open('.env', 'a') as f:
#     f.write(f"\nEPSILON_SIGMA_B_0={epsilon_sigma_b_0}")

# Further code to use epsilon_sigma_b_0 in your EC calculations...
