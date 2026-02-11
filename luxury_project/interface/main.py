import pandas as pd
from luxury_project.ml_logic.data import get_data, load_data_to_bq
from luxury_project.ml_logic.api import get_exchange_rates
from luxury_project.params import brand
from luxury_project.ml_logic.preprocessor import preprocess_data, preprocess_features
from luxury_project.ml_logic.model import initialize_model, train_model, evaluate_model, get_coefficients

def run_full_pipeline():
    print(f"🚀 Démarrage du pipeline complet pour : {brand}")

    # ---------------------------------------------------------
    # 1. EXTRACTION & PRÉ-TRAITEMENT (URL + Cleaning)
    # ---------------------------------------------------------
    print("\n--- 1. Extraction & Feature Engineering ---")
    df = get_data(brand=brand)
    
    if df.empty:
        print("❌ Stop : Aucune donnée.")
        return

    # On applique ton extracteur d'URL (Matière, Taille, Type...)
    df = preprocess_data(df)

    # ---------------------------------------------------------
    # 2. CONVERSION MONÉTAIRE AVEC L'API
    # ---------------------------------------------------------
    print("\n--- 2. Conversion des Devises (Target) ---")
    df_rates = get_exchange_rates(base_currency="EUR")
    
    if df_rates is not None:
        df = df.merge(df_rates, on='currency', how='left')
        df['price_eur'] = df['price'] / df['rate']
        df['price_eur'] = df['price_eur'].round(2)
    else:
        print("⚠️ Attention : Pas de taux de change. On suppose que price = EUR (Risqué).")
        df['price_eur'] = df['price']

    # On retire les lignes où le prix ou la conversion a échoué
    df = df.dropna(subset=['price_eur'])
    print(f"✅ Données prêtes : {len(df)} lignes avec Prix en EUR.")

    # ---------------------------------------------------------
    # 3. MACHINE LEARNING (Entraînement)
    # ---------------------------------------------------------
    print("\n--- 3. Entraînement du Modèle ---")
    
    # Sélection des features business
    features_list = ['material', 'size', 'type', 'currency']
    
    # On remplit les trous pour éviter que le modèle plante (ex: collection manquante)
    X = df[features_list].fillna('Unknown')
    y = df['price_eur']

    # Encodage (Catégories -> Chiffres)
    X_processed, encoder = preprocess_features(X)

    # Entraînement
    model = initialize_model(model_type="linear") 
    model = train_model(model, X_processed, y)
    
    # Évaluation (RMSE, R2)
    evaluate_model(model, X_processed, y)

    # ---------------------------------------------------------
    # 4. BUSINESS INTELLIGENCE 
    # ---------------------------------------------------------
    print("\n--- 4. Extraction des Drivers de Prix ---")
    df_coefficients = get_coefficients(model, encoder)
    df_coefficients['brand'] = brand 
    
    # Petit aperçu console
    print("💰 Top 3 Facteurs de Hausse de Prix :")
    print(df_coefficients.head(3))

    # ---------------------------------------------------------
    # 5. SAUVEGARDE BIGQUERY 
    # ---------------------------------------------------------
    print("\n--- 5. Sauvegarde des résultats ---")
    
    # A. Sauvegarde des Prédictions (Table d'Analyse)
    # On ajoute la prédiction au DF original pour voir les "bonnes affaires" (Undervalued)
    df['predicted_price'] = model.predict(X_processed)
    df['valuation_gap'] = df['price_eur'] - df['predicted_price'] # Positif = Cher, Négatif = Bon plan
    
    table_analysis = f"{brand.lower().replace(' ', '_')}_data_analysis"
    load_data_to_bq(df, table_analysis)

    # B. Sauvegarde des Coefficients (Table des Drivers)
    table_drivers = f"{brand.lower().replace(' ', '_')}_price_drivers"
    load_data_to_bq(df_coefficients, table_drivers)

    print("🏁 Pipeline terminé avec succès !")

if __name__ == '__main__':
    try:
        run_full_pipeline()
    except Exception as e:
        print(f"❌ Erreur critique : {e}")