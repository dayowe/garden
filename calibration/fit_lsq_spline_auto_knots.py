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

# Load the environment variables from .env file
load_dotenv()

# Fetch environment variables and convert them to numpy arrays
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(','), dtype=float)
vwc_vals = np.array(os.getenv('VWC_VALS').split(','), dtype=float)

# Sort the data by humidity_vals, required for LSQUnivariateSpline
sorted_indices = np.argsort(humidity_vals)
humidity_vals_sorted = humidity_vals[sorted_indices]
vwc_vals_sorted = vwc_vals[sorted_indices]

# Function to estimate second derivative
def estimate_curvature(x, y):
    dy = np.diff(y) / np.diff(x)  # First derivative
    ddy = np.diff(dy) / np.diff(x[:-1])  # Second derivative
    return ddy

# Estimate the curvature
curvature = estimate_curvature(humidity_vals_sorted, vwc_vals_sorted)

# Determine threshold for curvature to place a knot
curvature_threshold = np.std(curvature) * 2  # for example, two standard deviations above the mean

# Identify where curvature is above the threshold
knot_indices = np.where(abs(curvature) > curvature_threshold)[0] + 1  # +1 for the offset from np.diff

# Ensure knots are within the interior of the data domain
knot_indices = knot_indices[(knot_indices > 0) & (knot_indices < len(humidity_vals_sorted) - 1)]
knots = humidity_vals_sorted[knot_indices]

# Create the LSQ Univariate Spline for linear fit
spline = LSQUnivariateSpline(humidity_vals_sorted, vwc_vals_sorted, t=knots, k=1)

# Get coefficients for each segment
coefficients = []
for i in range(len(knots) + 1):
    if i == 0:
        x = humidity_vals_sorted[humidity_vals_sorted <= knots[0]]
        y = vwc_vals_sorted[:len(x)]
    elif i == len(knots):
        x = humidity_vals_sorted[humidity_vals_sorted >= knots[-1]]
        y = vwc_vals_sorted[-len(x):]
    else:
        x = humidity_vals_sorted[(humidity_vals_sorted > knots[i-1]) & (humidity_vals_sorted <= knots[i])]
        y = vwc_vals_sorted[(humidity_vals_sorted > knots[i-1]) & (humidity_vals_sorted <= knots[i])]
    
    # Fit a new linear model for each segment to get coefficients
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    coefficients.append((m, c))

# Print the knots
print("Knots:", ",".join(map(str, knots)))

# Print the coefficients for each linear segment
for i, (m, c) in enumerate(coefficients):
    print(f"Segment {i+1} Coefficients: Slope = {m}, Intercept = {c}")
