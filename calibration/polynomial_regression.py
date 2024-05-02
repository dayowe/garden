# pip install numpy scipy python-dotenv matplotlib
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
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(', '), dtype=np.float64)
vwc_vals = np.array(os.getenv('VWC_VALS').split(', '), dtype=np.float64)

# Define the form of the polynomial function you want to fit dynamically based on the degree
def polynomial_function(x, *params):
    return sum(p * x**i for i, p in enumerate(params))

# Initial guess for the parameters -- a list of ones with the length of degree + 1
initial_guess = [1] * (args.degree + 1)

# Perform the curve fitting
params, _ = curve_fit(polynomial_function, humidity_vals, vwc_vals, p0=initial_guess)

# Output the fitted parameters with 8 decimal places
print("The fitted parameters for the polynomial regression are:")
for i, param in enumerate(params):
    print(f"a{i}: {param:.8f}")

# Function to calculate the polynomial with the fitted parameters
def fitted_polynomial(x):
    return polynomial_function(x, *params)

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
