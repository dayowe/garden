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

To use this script, you will need to have a .env file with the humidity and VWC data points stored in the environment variables `HUMIDITY_VALS` and `VWC_VALS`. The values should be listed as comma-separated strings.

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

load_dotenv()

# Retrieve humidity and VWC values from environment variables and convert them to NumPy arrays
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(', '), dtype=np.float64)
vwc_vals = np.array(os.getenv('VWC_VALS').split(', '), dtype=np.float64)

# Define the power function for curve fitting
def power_function(x, a, b, c):
    return a * np.power(x, b) + c

# Initial guesses for the power function parameters
initial_guess = [1, 0.5, 1]

# Perform the curve fitting using the power function and initial parameter guesses
params, _ = curve_fit(power_function, humidity_vals, vwc_vals, p0=initial_guess)

# Print the fitted parameters for the power regression model, each on its own line
print("The fitted parameters for the power regression are:")
print(f"a (pre-exponential factor): {params[0]}")
print(f"b (exponent): {params[1]}")
print(f"c (vertical offset): {params[2]}")