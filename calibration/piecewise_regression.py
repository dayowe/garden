"""
piecewise_regression.py

This script conducts a piecewise linear regression analysis on a set of data points. It determines the optimal breakpoint
that minimizes the Bayesian Information Criterion (BIC) for the two resulting linear segments of the dataset. The dataset
is sourced from environment variables 'HUMIDITY_VALS' and 'VWC_VALS', which should contain comma-separated numerical values
for humidity and Volumetric Water Content (VWC) respectively.

The script outputs the optimal breakpoint and the coefficients of the two linear models. It also saves these results to a
text file named 'coefficients.txt'.

Pre-requisites:
- Set 'HUMIDITY_VALS' and 'VWC_VALS' in your environment variables with valid numerical values.
- Install required Python packages: statsmodels, scikit-learn, python-dotenv, numpy

Usage:
1. Ensure that the necessary environment variables are set.
2. Run this script in a Python environment with the required packages.
3. Review the outputted optimal breakpoint and coefficients, or check the 'coefficients.txt' file.
"""

import os
import numpy as np
import statsmodels.api as sm
from statsmodels.tools.tools import add_constant
from sklearn.metrics import mean_squared_error
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Fetch environment variables and convert them to numpy arrays
humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(','), dtype=float)
vwc_vals = np.array(os.getenv('VWC_VALS').split(','), dtype=float)

# Function to find the best breakpoint using BIC
def find_best_breakpoint(humidity, vwc, min_segment_size=10):
    best_breakpoint = None
    lowest_bic = float('inf')

    # Only consider breakpoints where each segment has at least `min_segment_size` observations
    for i in range(min_segment_size, len(humidity) - min_segment_size):
        potential_breakpoint = humidity[i]

        # Segments
        s1 = humidity[:i]
        s2 = humidity[i:]
        vwc_s1 = vwc[:i]
        vwc_s2 = vwc[i:]

        # Fit models
        model1 = sm.OLS(vwc_s1, add_constant(s1)).fit()
        model2 = sm.OLS(vwc_s2, add_constant(s2)).fit()

        # Combined BIC
        combined_bic = model1.bic + model2.bic

        # Check if we have a new best BIC
        if combined_bic < lowest_bic:
            lowest_bic = combined_bic
            best_breakpoint = potential_breakpoint

    return best_breakpoint

# Find the optimal breakpoint
optimal_breakpoint = find_best_breakpoint(humidity_vals, vwc_vals)

# Output the breakpoint
print(f"Optimal Breakpoint: {optimal_breakpoint}")

# Split the data at the optimal breakpoint
breakpoint_index = np.where(humidity_vals == optimal_breakpoint)[0][0]
segment1 = humidity_vals[:breakpoint_index]
segment2 = humidity_vals[breakpoint_index:]
vwc_segment1 = vwc_vals[:breakpoint_index]
vwc_segment2 = vwc_vals[breakpoint_index:]

# Fit the linear models to both segments
model1 = sm.OLS(vwc_segment1, add_constant(segment1)).fit()
model2 = sm.OLS(vwc_segment2, add_constant(segment2)).fit()

# Print or save the coefficients
print(f"Segment 1 Coefficients: Intercept = {model1.params[0]}, Slope = {model1.params[1]}")
print(f"Segment 2 Coefficients: Intercept = {model2.params[0]}, Slope = {model2.params[1]}")

# Optionally, save to a text file
with open('coefficients.txt', 'w') as file:
    file.write(f"Optimal Breakpoint: {optimal_breakpoint}\n")
    file.write(f"Segment 1 Coefficients: Intercept = {model1.params[0]}, Slope = {model1.params[1]}\n")
    file.write(f"Segment 2 Coefficients: Intercept = {model2.params[0]}, Slope = {model2.params[1]}\n")
