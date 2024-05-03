"""
This script fits a least squares univariate spline to humidity and VWC data. It allows the user to specify
knots via command-line arguments. If no knots are provided, a default value is used. The script sorts the
data, validates the provided knots, fits the spline, and prints the linear coefficients for each segment
between knots.

To run this script, the following command can be used:
`python fit_lsq_spline_with_user_knots.py --knot <knot_values>`

Required packages:
- numpy: For numerical operations.
- scipy: For the LSQUnivariateSpline fitting.
- python-dotenv: To load environment variables.
- argparse: For parsing command-line arguments.

Install the packages using:
`pip install numpy scipy python-dotenv`
"""

import os
import numpy as np
from scipy.interpolate import LSQUnivariateSpline
from dotenv import load_dotenv
import argparse

# Set up argument parser to accept a knot value
parser = argparse.ArgumentParser(description='Fit a LSQ Univariate Spline to humidity and VWC data.')
parser.add_argument('-k', '--knot', type=float, nargs='+', help='The knot value(s) for the spline.')
args = parser.parse_args()

# Load the environment variables from .env file
load_dotenv()

# Fetch environment variables and convert them to numpy arrays
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(','), dtype=float)
vwc_vals = np.array(os.getenv('VWC_VALS').split(','), dtype=float)

# Sort the data by humidity_vals, required for LSQUnivariateSpline
sorted_indices = np.argsort(humidity_vals)
humidity_vals_sorted = humidity_vals[sorted_indices]
vwc_vals_sorted = vwc_vals[sorted_indices]

# Ensure there are enough points around each knot and knots are within interior
def validate_knots(h_vals, knots):
    valid_knots = []
    for knot in knots:
        if h_vals[0] < knot < h_vals[-1]:  # Check if knot is in the interior
            idx = np.searchsorted(h_vals, knot)
            if idx > 1 and idx < len(h_vals) - 1:  # Ensure enough points around the knot
                valid_knots.append(knot)
    return valid_knots

# Use the provided knot value(s) if given, otherwise default to [28]
provided_knots = args.knot if args.knot is not None else [28]
knots = validate_knots(humidity_vals_sorted, provided_knots)

# Check if there are valid knots after validation
if not knots:
    raise ValueError("No valid knots provided. Knots must be within the data range and not too close to the edges.")

# Create the LSQ Univariate Spline for linear fit
spline = LSQUnivariateSpline(humidity_vals_sorted, vwc_vals_sorted, t=knots, k=1)

# Get coefficients for each segment
coefficients = []
for i in range(len(knots) + 1):
    if i == 0:
        x = humidity_vals_sorted[humidity_vals_sorted <= knots[0]]
        y = vwc_vals_sorted[:len(x)]
    elif i == len(knots):
        x = humidity_vals_sorted[humidity_vals_sorted > knots[-1]]
        y = vwc_vals_sorted[-len(x):]
    else:
        x = humidity_vals_sorted[(humidity_vals_sorted > knots[i-1]) & (humidity_vals_sorted <= knots[i])]
        y = vwc_vals_sorted[(humidity_vals_sorted > knots[i-1]) & (humidity_vals_sorted <= knots[i])]
    
    # Fit a new linear model for each segment to get coefficients
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    coefficients.append((m, c))

# Print the coefficients for each linear segment
for i, (m, c) in enumerate(coefficients):
    print(f"Segment {i+1} Coefficients: Slope = {m}, Intercept = {c}")
