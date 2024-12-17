"""
This script fits a least squares univariate spline to humidity and VWC data by automatically determining
the positions of knots. Knots are placed where the second derivative of the spline, an estimate of the
data's curvature, exceeds twice the standard deviation. It sorts the data, calculates curvature, identifies
knots based on curvature threshold, fits the spline, and prints the linear coefficients for each data segment.

Required packages:
- numpy: For numerical operations.
- scipy: For the LSQUnivariateSpline fitting.
- python-dotenv: To load environment variables.

Install the packages using:
`pip install numpy scipy python-dotenv`
"""

import os
import numpy as np
from scipy.interpolate import LSQUnivariateSpline
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Load the environment variables from .env file
load_dotenv()

# Fetch environment variables and convert them to numpy arrays
raw = np.array(os.getenv('RAW').split(','), dtype=float)
true_vwc = np.array(os.getenv('VWC').split(','), dtype=float)

# Sort the data by raw, required for LSQUnivariateSpline
sorted_indices = np.argsort(raw)
raw_sorted = raw[sorted_indices]
true_vwc_sorted = true_vwc[sorted_indices]

# Function to estimate second derivative
def estimate_curvature(x, y):
    dy = np.diff(y) / np.diff(x)  # First derivative
    ddy = np.diff(dy) / np.diff(x[:-1])  # Second derivative
    return ddy

# Estimate the curvature
curvature = estimate_curvature(raw_sorted, true_vwc_sorted)

# Determine threshold for curvature to place a knot
curvature_threshold = np.std(curvature) * 2  # for example, two standard deviations above the mean

# Identify where curvature is above the threshold
knot_indices = np.where(abs(curvature) > curvature_threshold)[0] + 1  # +1 for the offset from np.diff

# Ensure knots are within the interior of the data domain
knot_indices = knot_indices[(knot_indices > 0) & (knot_indices < len(raw_sorted) - 1)]
knots = raw_sorted[knot_indices]

# Create the LSQ Univariate Spline for linear fit
spline = LSQUnivariateSpline(raw_sorted, true_vwc_sorted, t=knots, k=1)

# Get coefficients for each segment
coefficients = []
for i in range(len(knots) + 1):
    if i == 0:
        x = raw_sorted[raw_sorted <= knots[0]]
        y = true_vwc_sorted[:len(x)]
    elif i == len(knots):
        x = raw_sorted[raw_sorted >= knots[-1]]
        y = true_vwc_sorted[-len(x):]
    else:
        x = raw_sorted[(raw_sorted > knots[i-1]) & (raw_sorted <= knots[i])]
        y = true_vwc_sorted[(raw_sorted > knots[i-1]) & (raw_sorted <= knots[i])]
    
    # Fit a new linear model for each segment to get coefficients
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    coefficients.append((m, c))

# Print the knots
print("Knots:", ",".join(map(str, knots)))

# Print the coefficients for each linear segment
for i, (m, c) in enumerate(coefficients):
    print(f"Segment {i+1} Coefficients: Slope = {m}, Intercept = {c}")

# Plotting code
# Use a finer grid for plotting the fitted spline
raw_for_curve = np.linspace(min(raw_sorted), max(raw_sorted), 200)
fitted_values_for_curve = spline(raw_for_curve)

# Predict the VWC values using the spline model
predicted_vwc = spline(raw_sorted)

# Calculate residuals
residuals = true_vwc_sorted - predicted_vwc

# Calculate Mean Squared Error and Root Mean Squared Error
mse = np.mean(residuals**2)
rmse = np.sqrt(mse)
sem = np.std(residuals) / np.sqrt(len(residuals))

print(f"MSE: {mse:.8f}")
print(f"RMSE: {rmse:.8f}")
print(f"SEM: {sem:.8f}")

# Plot the original data and the fitted spline, and residuals
plt.figure(figsize=(15, 7))

# Original Data and Spline Fit Plot
plt.subplot(1, 3, 1)
plt.scatter(raw_sorted, true_vwc_sorted, color='blue', label='Actual VWC')
plt.plot(raw_for_curve, fitted_values_for_curve, 'r-', label='Spline Fit')
plt.xlabel('Sensor Readings')
plt.ylabel('Volumetric Water Content (VWC)')
plt.title('Sensor Readings vs. VWC')
plt.legend()

# Predicted VWC vs. Actual VWC
plt.subplot(1, 3, 2)
plt.scatter(true_vwc_sorted, predicted_vwc, color='green', label='Predicted VWC')
plt.plot([true_vwc_sorted.min(), true_vwc_sorted.max()], [true_vwc_sorted.min(), true_vwc_sorted.max()], 'k--', lw=2, label='Perfect Prediction')
plt.xlabel('Actual VWC')
plt.ylabel('Predicted VWC')
plt.title('Actual vs. Predicted VWC')
plt.legend()

# Residuals vs Predicted VWC
plt.subplot(1, 3, 3)
plt.scatter(predicted_vwc, residuals, color='purple')
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted VWC')
plt.ylabel('Residuals')
plt.title(f'Residuals vs. Predicted VWC\nMSE: {mse:.8f} | RMSE: {rmse:.8f} | SEM: {sem:.8f}')

plt.tight_layout()
plt.show()
