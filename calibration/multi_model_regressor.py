"""
multi_model_regressor.py

This script is designed to fit various regression models to a given dataset and evaluate their performance using the mean squared error (MSE) metric. Lower MSE values indicate a better fit to the test data, while higher MSE values suggest a poorer fit. It is important to consider the possibility of overfitting, the assumptions of each model, the nature of the data, the need for hyperparameter tuning, and the choice of validation strategy when interpreting these MSE values.

Usage:
Run the script with the --predictor-var (-p) and --response-var (-r) arguments to specify the names of the predictor and response variables stored in the environment variables.

Example:
`python multi_model_regressor.py -p HUMIDITY_VALS -r VWC_VALS`

Please ensure the data is preprocessed appropriately, and that the necessary Python packages are installed and available in your environment.

The script will output the test MSE for each model, providing a quick comparison of their performance on the provided dataset.
"""

import os
import argparse
import numpy as np
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from pygam import LinearGAM
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

# Set up command-line arguments
parser = argparse.ArgumentParser(description='Fit various regression models to data specified in environment variables.')
parser.add_argument('-p', '--predictor-var', type=str, help='Environment variable name for the predictor variable data.', required=True)
parser.add_argument('-r', '--response-var', type=str, help='Environment variable name for the response variable data.', required=True)
args = parser.parse_args()

# Load environment variables
load_dotenv()

# Retrieve and validate data from environment variables
predictor_var_string = os.getenv(args.predictor_var)
response_var_string = os.getenv(args.response_var)

if predictor_var_string is None or response_var_string is None:
    raise ValueError(f"Data not found. Please ensure the environment variables '{args.predictor_var}' and '{args.response_var}' are set.")

predictor_vals = np.array(predictor_var_string.split(', '), dtype=np.float64).reshape(-1, 1)
response_vals = np.array(response_var_string.split(', '), dtype=np.float64)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(predictor_vals, response_vals, test_size=0.2, random_state=42)

# Define models
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(),
    'Lasso Regression': Lasso(),
    'Elastic Net Regression': ElasticNet(),
    '1st Degree Polynomial Regression': make_pipeline(PolynomialFeatures(degree=1), LinearRegression()),
    '2nd Degree Polynomial Regression': make_pipeline(PolynomialFeatures(degree=2), LinearRegression()),
    '3rd Degree Polynomial Regression': make_pipeline(PolynomialFeatures(degree=3), LinearRegression()),
    '4th Degree Polynomial Regression': make_pipeline(PolynomialFeatures(degree=4), LinearRegression()),
    'GAM': LinearGAM(),
    'Random Forest': RandomForestRegressor(random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(random_state=42),
    'XGBoost': XGBRegressor(random_state=42),
    'LightGBM': LGBMRegressor(random_state=42, verbose=-1),
    'CatBoost': CatBoostRegressor(random_state=42, verbose=0),
    'SVR': SVR(),
    'KNN': KNeighborsRegressor(),
    'Gaussian Processes': GaussianProcessRegressor(random_state=42),
}

# Train and evaluate models, and store results in a dictionary
mse_results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    mse_results[name] = mse

# Sort models by MSE in ascending order
sorted_mse_results = sorted(mse_results.items(), key=lambda item: item[1])

# Print sorted results
print("Model performance sorted from best to worst (by Test MSE):")
for name, mse in sorted_mse_results:
    print(f'{name} Test MSE: {mse}')
