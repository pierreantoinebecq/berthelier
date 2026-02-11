import pandas as pd
from google.cloud import bigquery
from pathlib import Path

# On importe les variables de configuration 
from luxury_project.params import PROJECT_ID, DATASET_ID, TABLE_ID, brand

def get_data(brand=brand):
    """
    On récupère les données depuis la table Source 
    """
    print(f"Chargement des données pour {brand}...")
    
    # 1. Utilisation des variables params.py 
    query = f"""
        SELECT *
        FROM `edhec-01.luxurydata2502.price-monitoring-2022`
        WHERE brand = '{brand}'
    """
    
    # 2. Connexion auto 
    try:
        client = bigquery.Client()
        df = client.query(query).to_dataframe()
        print(f"{len(df)} lignes chargées depuis BigQuery.")
        return df
        
    except Exception as e:
        print("Erreur de connexion BigQuery.")
        raise e

def load_data_to_bq(df, table_name, replace=True):
    """
    On sauvegarde le DataFrame dans notre projet BigQuery
    """
    print(f"Préparation de la sauvegarde vers {table_name}...")

    # On utilise notre projet (défini dans .env -> docker -> params.py)
    client = bigquery.Client(project=PROJECT_ID)
    
    # La cible 
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    
    # Si replace=True, on écrase la table existante (WRITE_TRUNCATE)
    write_mode = "WRITE_TRUNCATE" if replace else "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
    
    try:
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()  # On attend que ça finisse
        print(f"Sauvegarde terminée avec succès dans {table_ref}.")
        
    except Exception as e:
        print(f"Erreur lors de l'écriture dans BigQuery : {e}")
        raise e

if __name__ == "__main__":
    # Petit test rapide si on lance ce fichier seul
    try:
        df = get_data("Cartier")
        print(df.head())
    except:
        pass
