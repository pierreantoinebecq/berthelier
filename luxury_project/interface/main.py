import pandas as pd
from luxury_project.ml_logic.data import get_data, load_data_to_bq
from luxury_project.ml_logic.api import get_exchange_rates
from luxury_project.params import brand

def etl_pipeline():
    print(f"Démarrage du pipeline ETL pour la marque : {brand}...")

    # ---------------------------------------------------------
    # 1. EXTRACTION (Données existantes BigQuery)
    # ---------------------------------------------------------
    print("--- 1. Extraction des données Luxe ---")
    df_luxury = get_data(brand=brand)
    
    if df_luxury.empty:
        print("❌ Aucune donnée trouvée dans la source. Arrêt du pipeline.")
        return

    # ---------------------------------------------------------
    # 2. ENRICHISSEMENT (API Taux de change)
    # ---------------------------------------------------------
    print("--- 2. Récupération des taux de change (Base EUR) ---")
    # On récupère les taux : 1 EUR = X Devise
    df_rates = get_exchange_rates(base_currency="EUR")
    
    # ---------------------------------------------------------
    # 3. TRANSFORMATION (Fusion & Calculs)
    # ---------------------------------------------------------
    print("--- 3. Transformation & Nettoyage ---")
    
    if df_rates is not None:
        # On fusionne les données luxe avec les taux sur la colonne 'currency'
        # 'left' join pour garder toutes les lignes luxe même si on n'a pas le taux
        df_merged = df_luxury.merge(df_rates, on='currency', how='left')
        
        # Calcul : Convertir le prix local en Euros
        # Formule : Prix EUR = Prix Local / Taux (car 1 EUR = Taux * Devise)
        df_merged['price_eur'] = df_merged['price'] / df_merged['rate']
        
        # Arrondir pour faire propre
        df_merged['price_eur'] = df_merged['price_eur'].round(2)
        
        print(f"✅ Fusion réussie. {len(df_merged)} lignes traitées.")
    else:
        print("⚠️ API indisponible. On continue avec les données brutes.")
        df_merged = df_luxury

    # Petit nettoyage : on garde une copie propre
    df_cleaned = df_merged.copy()

    # ---------------------------------------------------------
    # 4. CHARGEMENT (Vers TON BigQuery)
    # ---------------------------------------------------------
    print(f"--- 4. Chargement dans BigQuery pour {brand} ---")
    
    # On crée un nom de table propre (ex: "louis_vuitton_processed")
    target_table_name = f"{brand.lower().replace(' ', '_')}_processed"
    
    # On sauvegarde (replace=True écrase la table pour éviter les doublons à chaque test)
    load_data_to_bq(df_cleaned, table_name=target_table_name, replace=True)
    
    print("🏁 Pipeline terminé avec succès !")

if __name__ == '__main__':
    try:
        etl_pipeline()
    except Exception as e:
        print(f"❌ Erreur critique dans le pipeline : {e}")