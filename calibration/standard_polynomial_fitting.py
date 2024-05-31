import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import argparse

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Fit a polynomial model of specified degree to sensor data.')
parser.add_argument('-d', '--degree', type=int, help='Degree of the polynomial model to fit.', required=True)
parser.add_argument('-p', '--predictor-var', type=str, help='Environment variable name for the predictor variable data.', required=True)
parser.add_argument('-r', '--response-var', type=str, help='Environment variable name for the response variable data.', required=True)
args = parser.parse_args()

# Load environment variables from .env file
load_dotenv()

# Retrieve the data values from the .env file based on the provided variable names
predictor_var_string = os.getenv(args.predictor_var)
response_var_string = os.getenv(args.response_var)

# Check if the data is available
if predictor_var_string is None or response_var_string is None:
    raise ValueError(f"Please ensure both environment variables '{args.predictor_var}' and '{args.response_var}' are set.")

# Convert the string values to numpy arrays, assuming they are comma-separated
predictor_vals = np.array(list(map(float, predictor_var_string.split(','))))
response_vals = np.array(list(map(float, response_var_string.split(','))))

# Fit a polynomial model to your data of the specified degree
degree = args.degree
coefficients = np.polyfit(predictor_vals, response_vals, degree)

# Generate a polynomial function using the fitted coefficients
polynomial_model = np.poly1d(coefficients)

# Print the coefficients in the derived format
print("Derived coefficients: ", end="")
print(", ".join(f"a{degree-i} = {coeff:.14f}" for i, coeff in enumerate(coefficients)))

print("")

# Print the coefficients with reasonable precision in descending order
print("Fitted Polynomial Model Coefficients:")
for i in range(degree, -1, -1):
    print(f"{coefficients[degree-i]:.8f}")

# Use a finer grid for plotting the fitted curve
predictor_vals_for_curve = np.linspace(min(predictor_vals), max(predictor_vals), 200)
fitted_values_for_curve = polynomial_model(predictor_vals_for_curve)

# Predict the VWC values using the polynomial model
predicted_VWC = polynomial_model(predictor_vals)

# Calculate residuals
residuals = response_vals - predicted_VWC

# Calculate Mean Squared Error and Root Mean Squared Error
MSE = np.mean(residuals**2)
RMSE = np.sqrt(MSE)
SEM = np.std(residuals) / np.sqrt(len(residuals))

print(f"MSE: {MSE:.8f}")
print(f"RMSE: {RMSE:.8f}")
print(f"SEM: {SEM:.8f}")

# Plot the original data and the fitted curve, and residuals
plt.figure(figsize=(15, 7))

# Original Data and Polynomial Fit Plot
plt.subplot(1, 3, 1)
plt.scatter(predictor_vals, response_vals, color='blue', label='Actual VWC')
plt.plot(predictor_vals_for_curve, fitted_values_for_curve, 'r-', label=f'Polynomial Fit (degree={degree})')
plt.xlabel('Sensor Readings')
plt.ylabel('Volumetric Water Content (VWC)')
plt.title('Sensor Readings vs. VWC')
plt.legend()

# Predicted VWC vs. Actual VWC
plt.subplot(1, 3, 2)
plt.scatter(response_vals, predicted_VWC, color='green', label='Predicted VWC')
plt.plot([response_vals.min(), response_vals.max()], [response_vals.min(), response_vals.max()], 'k--', lw=2, label='Perfect Prediction')
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