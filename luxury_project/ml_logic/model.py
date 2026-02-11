from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import numpy as np

def initialize_model(model_type="linear"):
    """
    Initialize the model.
    Using Ridge (Linear Regression with regularization) is often safer 
    to prevent huge coefficients if you have many variables.
    """
    if model_type == "linear":
        model = LinearRegression()
    else:
        # Ridge is better if you have collinearity (highly correlated features)
        model = Ridge(alpha=1.0)
    
    return model

def train_model(model, X, y):
    model.fit(X, y)
    print("✅ Model trained")
    return model

def evaluate_model(model, X, y):
    y_pred = model.predict(X)
    
    # Metrics
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, y_pred)
    
    print(f"✅ Model Evaluated:")
    print(f"   - RMSE: {rmse:.2f} (Average error in Price)")
    print(f"   - R2: {r2:.4f} (Explains {r2*100:.1f}% of variance)")
    
    return rmse, r2

def get_coefficients(model, encoder):
    """
    Extracts the 'Impact' of each feature on the price.
    Returns a DataFrame ready for PowerBI.
    """
    # 1. Get feature names from the OneHotEncoder
    feature_names = encoder.get_feature_names_out()
    
    # 2. Get coefficients (weights) from the model
    coefs = model.coef_
    
    # 3. Create a clean DataFrame
    df_coef = pd.DataFrame({
        'Feature': feature_names,
        'Price_Impact_EUR': coefs
    })
    
    # Sort by impact (highest to lowest)
    df_coef = df_coef.sort_values(by='Price_Impact_EUR', ascending=False)
    
    return df_coef