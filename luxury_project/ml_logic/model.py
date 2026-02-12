from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
import pandas as pd
import numpy as np

def initialize_model(model_type="linear"):
    """
    Initialize the model.
    """
    if model_type == "linear":
        model = LinearRegression()
    else:
        # Ridge is better if we have collinearity (highly correlated features)
        model = Ridge(alpha=1.0)
    
    return model

def train_model(model, X, y):
    model.fit(X, y)
    print("Model trained")
    return model

def evaluate_model(model, X, y):
    y_pred = model.predict(X)
    
    # Metrics
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y, y_pred)
    mape = mean_absolute_percentage_error(y, y_pred)

    r2 = r2_score(y, y_pred)
    
    print(f"Évaluation Globale :")
    print(f"   - RMSE (Sensible aux extrêmes): {rmse:.0f} €")
    print(f"   - MAE (Erreur moyenne réelle): {mae:.0f} €")
    print(f"   - MAPE (Erreur en %): {mape*100:.1f} %")
    print(f"   - R2: {r2:.4f}")

    # --- ANALYSE DE SEGMENT ---
    # On crée un petit DF temporaire pour analyser les erreurs
    df_results = pd.DataFrame({'Actual': y, 'Predicted': y_pred})
    df_results['Error'] = df_results['Actual'] - df_results['Predicted']
    
    # On regarde uniquement les produits "normaux" (< 5000 €)
    mask_normal = df_results['Actual'] < 5000
    if mask_normal.sum() > 0:
        mae_normal = mean_absolute_error(df_results[mask_normal]['Actual'], df_results[mask_normal]['Predicted'])
        print(f"\n Focus sur les prix 'normaux' (< 5 000 €) :")
        print(f"   - Sur ces {mask_normal.sum()} produits, l'erreur moyenne est de : {mae_normal:.0f} €")
    
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
