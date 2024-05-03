"""
This script is designed for conducting polynomial regression analysis on any set of sensor data. It can be utilized for a broad range of applications, including but not limited to estimating Volumetric Water Content (VWC), Dielectric Permittivity (DP), or other variables of interest that can be modeled through a polynomial relationship. The user can specify the degree of the polynomial, which allows for the flexibility to fit data with varying levels of complexity and behavior.

Upon execution, the script fits a polynomial model to the supplied data, computes the model coefficients, and visualizes both the data points and the polynomial fit. This analysis can be particularly useful for researchers, engineers, and data scientists who work with sensor data and require an empirical model to understand and predict the behavior of physical phenomena.

Features:
- Customizable polynomial degree for data fitting.
- Easy data input through environment variables.
- Data visualization to compare the original data points with the polynomial fit.

Prerequisites for running the script:
Make sure these packages are installed:
- numpy: For the core polynomial fitting functionality.
- matplotlib: For plotting the original data and the regression curve.
- python-dotenv: For loading environmental variables from a .env file.

These dependencies can be installed using the command:
`pip install numpy matplotlib python-dotenv`

Usage Instructions:
1. Prepare a .env file with the independent (predictor) and dependent (response) variables stored as comma-separated values, assigned to respective environment variable names.
2. Run this script with appropriate command-line arguments specifying the degree of the polynomial and the names of the environment variables for the data.

Example:
To fit a second-degree polynomial, you might use the following command:
`python polynomial_regression.py --degree 2 --independent-var SENSOR_READINGS --dependent-var RESPONSE_VARIABLE`

This will generate a quadratic model that fits the relationship between the sensor readings and the response variable.
"""

import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import argparse

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Fit a polynomial model of specified degree to sensor data.')
parser.add_argument('-d', '--degree', type=int, help='Degree of the polynomial model to fit.', required=True)
parser.add_argument('-i', '--independent-var', type=str, help='Environment variable name for the independent variable data.', required=True)
parser.add_argument('-e', '--dependent-var', type=str, help='Environment variable name for the dependent variable data.', required=True)
args = parser.parse_args()

# Load environment variables from .env file
load_dotenv()

# Retrieve the data values from the .env file based on the provided variable names
independent_var_string = os.getenv(args.independent_var)
dependent_var_string = os.getenv(args.dependent_var)

# Check if the data is available
if independent_var_string is None or dependent_var_string is None:
    raise ValueError(f"Please ensure both environment variables '{args.independent_var}' and '{args.dependent_var}' are set.")

# Convert the string values to numpy arrays, assuming they are comma-separated
independent_vals = np.array(list(map(float, independent_var_string.split(','))))
dependent_vals = np.array(list(map(float, dependent_var_string.split(','))))

# Fit a polynomial model to your data of the specified degree
degree = args.degree
coefficients = np.polyfit(independent_vals, dependent_vals, degree)

# Generate a polynomial function using the fitted coefficients
polynomial_model = np.poly1d(coefficients)

# Print the coefficients in the derived format
print("Derived coefficients: ", end="")
print(", ".join(f"a{degree-i} = {coeff:.14f}" for i, coeff in enumerate(coefficients)))

print("")

# Print the coefficients with reasonable precision in descending order
print("Fitted Polynomial Model Coefficients:")
for i in range(args.degree, -1, -1):
    print(f"a{i} = {coefficients[args.degree-i]:.8f}")

# Use a finer grid for plotting the fitted curve
independent_vals_for_curve = np.linspace(min(independent_vals), max(independent_vals), 200)
fitted_values_for_curve = polynomial_model(independent_vals_for_curve)

# Plot the original data and the fitted curve
plt.figure(figsize=(10, 5))
plt.scatter(independent_vals, dependent_vals, color='blue', label='Data Points')
plt.plot(independent_vals_for_curve, fitted_values_for_curve, 'r-', label=f'Fitted Polynomial Model (degree={degree})')
plt.xlabel(args.independent_var)
plt.ylabel(args.dependent_var)
plt.title('Polynomial Model Fit to Data')
plt.legend()
plt.grid(True)
plt.show()