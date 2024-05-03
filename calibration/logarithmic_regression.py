import numpy as np
from scipy.optimize import curve_fit
from dotenv import load_dotenv
import os

load_dotenv()

humidity_vals = np.array(os.getenv('HUMIDITY_VALS').split(', '), dtype=np.float64)
vwc_vals = np.array(os.getenv('VWC_VALS').split(', '), dtype=np.float64)

# Logarithmic function may not fit well if there are zero or negative values in humidity_vals
def logarithmic_function(x, a, b):
    return a + b * np.log(x)

initial_guess = [1, 1]

# Ensuring there are no zero or negative values for the logarithmic function
humidity_vals_positive = humidity_vals[humidity_vals > 0]
vwc_vals_positive = vwc_vals[humidity_vals > 0]

params, _ = curve_fit(logarithmic_function, humidity_vals_positive, vwc_vals_positive, p0=initial_guess)

print(f"The fitted parameters for the logarithmic regression are: {params}")

