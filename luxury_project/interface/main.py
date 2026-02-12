import pandas as pd
from luxury_project.ml_logic.data import get_data, load_data_to_bq
from luxury_project.ml_logic.api import get_exchange_rates
from luxury_project.params import brand
from luxury_project.ml_logic.preprocessor import preprocess_data, preprocess_features
from luxury_project.ml_logic.model import initialize_model, train_model, evaluate_model, get_coefficients

def run_full_pipeline():
    print(f"Starting full pipeline for: {brand}")

# ---------------------------------------------------------
# 1. EXTRACTION & PREPROCESSING (URL + Cleaning)
# ---------------------------------------------------------
print("\n--- 1. Data Extraction & Feature Engineering ---")
df = get_data(brand=brand)

if df.empty:
    print("Stop: No data found.")
    return

# Apply our URL extractor (Material, Size, Type...)
df = preprocess_data(df)

# ---------------------------------------------------------
# 2. CURRENCY CONVERSION USING THE API
# ---------------------------------------------------------
print("\n--- 2. Currency Conversion (Target) ---")
df_rates = get_exchange_rates(base_currency="EUR")

if df_rates is not None:
    df = df.merge(df_rates, on='currency', how='left')
    df['price_eur'] = df['price'] / df['rate']
    df['price_eur'] = df['price_eur'].round(2)
else:
    print("Warning: No exchange rates available. Assuming price is already in EUR (Risky).")
    df['price_eur'] = df['price']

# Remove rows where the price or conversion failed
df = df.dropna(subset=['price_eur'])
print(f"Data ready: {len(df)} rows with price in EUR.")

    # ---------------------------------------------------------
    # 3. MACHINE LEARNING (Entraînement)
    # ---------------------------------------------------------
    print("\n--- 3. Entraînement du Modèle ---")
    
    # Sélection des features business
    features_list = ['material', 'size', 'type', 'currency']
    
    # On remplit les trous pour éviter que le modèle plante (ex: collection manquante)
    X = df[features_list].fillna('Unknown')
    y = df['price_eur']

# Encoding (Categories -> Numbers)
X_processed, encoder = preprocess_features(X)

# Training
model = initialize_model(model_type="linear")
model = train_model(model, X_processed, y)

# Evaluation (RMSE, R2)
evaluate_model(model, X_processed, y)

# ---------------------------------------------------------
# 4. BUSINESS INTELLIGENCE
# ---------------------------------------------------------
print("\n--- 4. Extracting Price Drivers ---")
df_coefficients = get_coefficients(model, encoder)
df_coefficients['brand'] = brand

# Small console preview
print("Top 3 Factors Increasing Price:")
print(df_coefficients.head(3))

# ---------------------------------------------------------
# 5. BIGQUERY STORAGE
# ---------------------------------------------------------
print("\n--- 5. Saving Results ---")

# A. Save Predictions (Analysis Table)
# Add prediction to the original DF to identify "good deals" (Undervalued items)
df['predicted_price'] = model.predict(X_processed)
df['valuation_gap'] = df['price_eur'] - df['predicted_price']  # Positive = Expensive, Negative = Good deal

table_analysis = f"{brand.lower().replace(' ', '_')}_data_analysis"
load_data_to_bq(df, table_analysis)

# B. Save Coefficients (Drivers Table)
table_drivers = f"{brand.lower().replace(' ', '_')}_price_drivers"
load_data_to_bq(df_coefficients, table_drivers)

print("Pipeline completed successfully!")

if __name__ == '__main__':
    try:
        run_full_pipeline()
    except Exception as e:
        print(f"Critical error: {e}")

