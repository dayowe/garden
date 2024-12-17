"""
This script fits a least squares univariate spline to humidity and VWC data. It allows the user to specify
knots via command-line arguments. If no knots are provided, a default value is used. The script sorts the
data, validates the provided knots, fits the spline, and prints the linear coefficients for each segment
between knots. It also plots the fitted spline, actual vs. predicted VWC, and residuals.

To run this script, the following command can be used:
`python fit_lsq_spline_with_user_knots.py --knot <knot_values>`

Required packages:
- numpy: For numerical operations.
- scipy: For the LSQUnivariateSpline fitting.
- python-dotenv: To load environment variables.
- argparse: For parsing command-line arguments.
- matplotlib: For plotting the results.

Install the packages using:
`pip install numpy scipy python-dotenv matplotlib`
"""

import os
import numpy as np
from scipy.interpolate import LSQUnivariateSpline
from dotenv import load_dotenv
import argparse
import matplotlib.pyplot as plt

# Set up argument parser to accept multiple knot values
parser = argparse.ArgumentParser(description='Fit a LSQ Univariate Spline to humidity and VWC data.')
parser.add_argument('-k', '--knot', type=float, action='append', help='The knot value(s) for the spline.')
args = parser.parse_args()

# Load the environment variables from .env file
load_dotenv()

# Fetch environment variables and convert them to numpy arrays
raw = np.array(os.getenv('RAW').split(','), dtype=float)
true_vwc = np.array(os.getenv('VWC').split(','), dtype=float)

# Sort the data by raw, required for LSQUnivariateSpline
sorted_indices = np.argsort(raw)
raw_sorted = raw[sorted_indices]
true_vwc_sorted = true_vwc[sorted_indices]

# Ensure there are enough points around each knot and knots are within interior
def validate_knots(h_vals, knots):
    if not knots:
        return []
    valid_knots = []
    for knot in knots:
        if h_vals[0] < knot < h_vals[-1]:  # Check if knot is in the interior
            idx = np.searchsorted(h_vals, knot)
            # Ensure at least two points in each segment for k=1
            if idx > 0 and idx < len(h_vals) - 1:
                valid_knots.append(knot)
    return valid_knots

# Use the provided knot value(s) if given, otherwise default to [28]
provided_knots = args.knot if args.knot is not None else [28]
knots = validate_knots(raw_sorted, provided_knots)

# Sort the validated knots
knots.sort()

# Check if there are valid knots after validation
if not knots:
    raise ValueError("No valid knots provided. Knots must be within the data range and not too close to the edges.")

# Additional debugging information
print(f"Raw data sorted: {raw_sorted}")
print(f"True VWC sorted: {true_vwc_sorted}")
print(f"Provided knots: {provided_knots}")
print(f"Validated knots: {knots}")

# Create the LSQ Univariate Spline for linear fit
try:
    spline = LSQUnivariateSpline(raw_sorted, true_vwc_sorted, t=knots, k=1)
except ValueError as e:
    print(f"Error creating spline: {e}")
    print("Ensure that the knots satisfy the Schoenberg-Whitney conditions.")
    exit(1)

# Get coefficients for each segment
coefficients = []
for i in range(len(knots) + 1):
    if i == 0:
        x = raw_sorted[raw_sorted <= knots[0]]
        y = true_vwc_sorted[:len(x)]
    elif i == len(knots):
        x = raw_sorted[raw_sorted > knots[-1]]
        y = true_vwc_sorted[-len(x):]
    else:
        x = raw_sorted[(raw_sorted > knots[i-1]) & (raw_sorted <= knots[i])]
        y = true_vwc_sorted[(raw_sorted > knots[i-1]) & (raw_sorted <= knots[i])]

    # Fit a new linear model for each segment to get coefficients
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    coefficients.append((m, c))

# Print the coefficients for each linear segment
for i, (m, c) in enumerate(coefficients):
    print(f"Segment {i+1} Coefficients: Slope = {m}, Intercept = {c}")

# Plotting section
# Use a finer grid for plotting the fitted spline
raw_vals_for_curve = np.linspace(min(raw_sorted), max(raw_sorted), 200)
fitted_values_for_curve = spline(raw_vals_for_curve)

# Predict the VWC values using the spline model
predicted_VWC = spline(raw_sorted)

# Calculate residuals
residuals = true_vwc_sorted - predicted_VWC

# Calculate Mean Squared Error and Root Mean Squared Error
MSE = np.mean(residuals**2)
RMSE = np.sqrt(MSE)
SEM = np.std(residuals) / np.sqrt(len(residuals))

print(f"MSE: {MSE:.8f}")
print(f"RMSE: {RMSE:.8f}")
print(f"SEM: {SEM:.8f}")

# Plot the original data and the fitted curve, and residuals
plt.figure(figsize=(15, 7))

# Original Data and Spline Fit Plot
plt.subplot(1, 3, 1)
plt.scatter(raw_sorted, true_vwc_sorted, color='blue', label='Actual VWC')
plt.plot(raw_vals_for_curve, fitted_values_for_curve, 'r-', label=f'Spline Fit with knots at {knots}')
plt.xlabel('Sensor Readings')
plt.ylabel('Volumetric Water Content (VWC)')
plt.title('Sensor Readings vs. VWC')
plt.legend()

# Predicted VWC vs. Actual VWC
plt.subplot(1, 3, 2)
plt.scatter(true_vwc_sorted, predicted_VWC, color='green', label='Predicted VWC')
plt.plot([true_vwc_sorted.min(), true_vwc_sorted.max()], [true_vwc_sorted.min(), true_vwc_sorted.max()], 'k--', lw=2, label='Perfect Prediction')
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
