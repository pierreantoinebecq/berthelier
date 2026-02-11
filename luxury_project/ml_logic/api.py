import requests
import pandas as pd

def get_exchange_rates(base_currency="EUR"):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(url)
    
    if response.status_code == 200:
        rates = response.json().get("rates", {})
        # On transforme ça en DataFrame propre
        df = pd.DataFrame(list(rates.items()), columns=['currency', 'rate'])
        return df
    else:
        print("❌ Erreur API")
        return None
    

