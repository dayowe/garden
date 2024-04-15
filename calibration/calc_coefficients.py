import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Fetch and process data from .env file
humidity_vals = list(map(float, os.getenv("HUMIDITY_VALS").split(',')))
vwc_vals = list(map(float, os.getenv("VWC_VALS").split(',')))

# Perform quadratic regression to find the coefficients
coefficients = np.polyfit(humidity_vals, vwc_vals, 2)

# coefficients[0] will be 'a', coefficients[1] will be 'b', and coefficients[2] will be 'c'
a, b, c = coefficients

print(f"Derived coefficients: a = {a}, b = {b}, c = {c}")

# Optional: Plotting to visualize the fit
plt.scatter(humidity_vals, vwc_vals, label='Observed data')
plt.plot(np.sort(humidity_vals), np.polyval(coefficients, np.sort(humidity_vals)), color='red', label='Fitted quadratic model')
plt.xlabel('Humidity')
plt.ylabel('VWC')
plt.legend()
plt.show()