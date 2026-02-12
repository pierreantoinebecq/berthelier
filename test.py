from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os
from google.cloud import bigquery

def run_test():
    print("Démarrage du test...")

    # On vérifie juste si Docker a bien fait son boulot
    # (Docker a injecté la variable GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json)
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        print("ERREUR CRITIQUE : La variable d'environnement manque !")
        return

    try:
        client = bigquery.Client()
        print(f"Connecté au projet : {client.project}")
        
        query = """
            SELECT brand, count(*) as count
            FROM `edhec-01.luxurydata2502.price-monitoring-2022`
            GROUP BY brand
            LIMIT 5
        """
        df = client.query(query).to_dataframe()
        print(df)
        
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    run_test()
