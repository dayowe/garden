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
import matplotlib.pyplot as plt


# Load the environment variables from .env file
load_dotenv()

# Fetch environment variables and convert them to numpy arrays
humidity_vals = np.array(os.getenv('RAW').split(','), dtype=float)
vwc_vals = np.array(os.getenv('VWC').split(','), dtype=float)

# Function to find the best breakpoint using BIC
def find_best_breakpoint(humidity, vwc, min_segment_size=5):
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
print(f"Segment 1 Coefficients: Slope = {model1.params[1]}, Intercept = {model1.params[0]}")
print(f"Segment 2 Coefficients: Slope = {model2.params[1]}, Intercept = {model2.params[0]}")

# Optionally, save to a text file
with open('coefficients.txt', 'w') as file:
    file.write(f"Optimal Breakpoint: {optimal_breakpoint}\n")
    file.write(f"Segment 1 Coefficients: Slope = {model1.params[1]}, Intercept = {model1.params[0]}\n")
    file.write(f"Segment 2 Coefficients: Slope = {model2.params[1]}, Intercept = {model2.params[0]}\n")

# Use a finer grid for plotting the fitted segments
predictor_vals_for_curve = np.linspace(min(humidity_vals), max(humidity_vals), 200)

# Get the fitted values for each segment
fitted_values_segment1 = model1.predict(add_constant(segment1))
fitted_values_segment2 = model2.predict(add_constant(segment2))

# Predict the VWC values using the piecewise linear model
predicted_VWC = np.concatenate((fitted_values_segment1, fitted_values_segment2))

# Calculate residuals
residuals = vwc_vals - predicted_VWC

# Calculate Mean Squared Error and Root Mean Squared Error
MSE = mean_squared_error(vwc_vals, predicted_VWC)
RMSE = np.sqrt(MSE)
SEM = np.std(residuals) / np.sqrt(len(residuals))

print(f"MSE: {MSE:.8f}")
print(f"RMSE: {RMSE:.8f}")
print(f"SEM: {SEM:.8f}")

# Plot the original data and the fitted segments, and residuals
plt.figure(figsize=(15, 7))

# Original Data and Piecewise Fit Plot
plt.subplot(1, 3, 1)
plt.scatter(humidity_vals, vwc_vals, color='blue', label='Actual VWC')
plt.plot(segment1, fitted_values_segment1, 'r-', label='Piecewise Fit Segment 1')
plt.plot(segment2, fitted_values_segment2, 'g-', label='Piecewise Fit Segment 2')
plt.axvline(x=optimal_breakpoint, color='k', linestyle='--', label=f'Breakpoint at {optimal_breakpoint}')
plt.xlabel('Sensor Readings')
plt.ylabel('Volumetric Water Content (VWC)')
plt.title('Sensor Readings vs. VWC')
plt.legend()

# Predicted VWC vs. Actual VWC
plt.subplot(1, 3, 2)
plt.scatter(vwc_vals, predicted_VWC, color='green', label='Predicted VWC')
plt.plot([vwc_vals.min(), vwc_vals.max()], [vwc_vals.min(), vwc_vals.max()], 'k--', lw=2, label='Perfect Prediction')
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