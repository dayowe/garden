"""
advanced_polynomial_fitting.py

This script employs SciPy's curve_fit function to perform polynomial fitting, which allows 
for a more sophisticated analysis than standard polynomial fitting methods. It is capable of 
handling more complex models and provides advanced features like custom initial parameter guesses 
and optimization control.

The script is designed for users who require a more nuanced approach to data modeling, such as 
fitting non-linear relationships or dealing with data that requires a more refined fitting algorithm.

Prerequisites:
- NumPy: For handling numerical operations.
- SciPy: For advanced curve fitting capabilities.
- Matplotlib: For plotting the fitted polynomial against the data.
- Python-dotenv: For loading environmental variables from a .env file.
These dependencies can be installed via pip using the following command:
`pip install numpy scipy matplotlib python-dotenv`

Usage:
1. Prepare a .env file with the humidity and VWC data points stored in the environment variables 
   `HUMIDITY_VALS` and `VWC_VALS`, separated by commas.
2. Run the script, specifying the degree of the polynomial to fit.

Example:
`python advanced_polynomial_fitting.py --degree 3`

This command would fit a cubic polynomial to the data provided in the `HUMIDITY_VALS` and `VWC_VALS` 
environment variables, using a more advanced fitting technique.
"""

import numpy as np
from scipy.optimize import curve_fit
from dotenv import load_dotenv
import os
import argparse
import matplotlib.pyplot as plt

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Fit a polynomial model of specified degree to data.')
parser.add_argument('-d', '--degree', type=int, help='Degree of the polynomial model to fit.', required=True)
args = parser.parse_args()

# Load environment variables from .env file
load_dotenv()

# Retrieve data from environment variables
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(','), dtype=np.float64)
vwc_vals = np.array(os.getenv('VWC_VALS').split(','), dtype=np.float64)

# Define the form of the polynomial function you want to fit dynamically based on the degree
def polynomial_function(x, *params):
    return sum(p * x**i for i, p in enumerate(params))

# Initial guess for the parameters -- a list of ones with the length of degree + 1
initial_guess = [1] * (args.degree + 1)

# Perform the curve fitting
params, _ = curve_fit(polynomial_function, humidity_vals, vwc_vals, p0=initial_guess)

# Define the fitted polynomial function using the fitted parameters
def fitted_polynomial(x):
    return sum(p * x**i for i, p in enumerate(params))

# Output the derived coefficients in descending order (highest degree first)
print("Derived coefficients: ", end="")
# Coefficients are in ascending order, so we use [::-1] to reverse them for printing
print(", ".join(f"a{args.degree-i} = {param:.14f}" for i, param in enumerate(params[::-1])))

print("")

# Print the coefficients with reasonable precision in descending order (highest degree first)
print("Fitted Polynomial Model Coefficients:")
# We use [::-1] to reverse the params for printing in descending order
for i in range(args.degree, -1, -1):
    print(f"a{i} = {params[::-1][args.degree-i]:.8f}")

# Generate x values for plotting the fitted curve
x_plot = np.linspace(min(humidity_vals), max(humidity_vals), 200)

# Plot the original data and the fitted curve
plt.figure(figsize=(10, 5))
plt.scatter(humidity_vals, vwc_vals, label='Observed Data')
plt.plot(x_plot, fitted_polynomial(x_plot), 'r-', label=f'Fitted Polynomial (degree={args.degree})')
plt.xlabel('Humidity Values')
plt.ylabel('VWC Values')
plt.title('Polynomial Fit to Humidity Data')
plt.legend()
plt.grid(True)
plt.show()