import pandas as pd
from luxury_project.ml_logic.preprocessor import preprocess_data

# 1. On crée un faux dataset avec tes URLs exemples
data = {
    'url': [
        "https://uk.louisvuitton.com/eng-gb/products/neverfull-mm-tote-bag-monogram-empreinte-nvprod3400016v#M46039",
        "https://uk.louisvuitton.com/eng-gb/products/keepall-xs-bag-monogram-other-nvprod3130155v",
        "https://uk.louisvuitton.com/eng-gb/products/coussin-pm-bag-h27-nvprod2750001v#M57790"
    ],
    'price': [2000, 1500, 3000] # Prix bidons pour l'exemple
}

df = pd.DataFrame(data)

# 2. On lance la fonction
print("--- AVANT ---")
print(df.columns)

df_enriched = preprocess_data(df)

# 3. On regarde le résultat
print("\n--- APRÈS ---")
print(df_enriched[['url', 'sku', 'material', 'size']].to_string())