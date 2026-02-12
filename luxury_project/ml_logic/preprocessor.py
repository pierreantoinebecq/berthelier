import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import OneHotEncoder

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoyage Drastique :
    1. Retire les lignes sans prix.
    2. Retire les items "Unknown" ou "Other" qui ne sont pas des sacs.
    """
    initial_count = len(df)
    
    # 1. On vire les NaN sur le prix
    df = df.dropna(subset=['price'])
    
    if 'material' in df.columns and 'type' in df.columns:
        # On supprime ce qui n'a ni matière ni type identifié (ce sont souvent des accessoires mal parsés)
        # Condition : Garder si (Material OU Type est connu)
        df = df[
            (df['material'] != 'Unknown') | 
            (df['type'] != 'Other')
        ]
        
    final_count = len(df)
    print(f"🧹 Nettoyage : {initial_count} -> {final_count} lignes ({initial_count - final_count} supprimées)")
    
    return df

def extract_features_from_url(url):
    """
    Extrait les informations cachées dans l'URL.
    V2.0 : Ajout du support pour Accessoires, VVN, Montres et Bijoux.
    """
    # Sécurité
    if not isinstance(url, str):
        return {
            'sku': None, 'slug_clean': None,
            'material': 'Unknown', 'size': 'No Size', 'type': 'Other'
        }

    features = {
        'sku': None, 'slug_clean': None,
        'material': 'Unknown', 'size': 'No Size', 'type': 'Other'
    }

    try:
        # 1. Nettoyage du slug
        base_slug = url.split('/')[-1].split('#')[0]
        slug = re.sub(r'-nvprod\w+', '', base_slug)
        slug = re.sub(r'-\d+$', '', slug)
        features['slug_clean'] = slug
        
        # On travaille en minuscule pour faciliter les recherches
        slug_lower = str(slug).lower()

        # 2. Extraction SKU (Code produit)
        # Pattern élargi pour attraper J00109, M12345, Q12345, R12345
        sku_pattern = r'([A-Z][A-Z0-9]{5}|[0-9]{6})$'
        
        # On regarde dans le fragment (#) ou la fin de l'URL
        suffix = url.split('#')[-1] if '#' in url else url.split('/')[-1]
        
        match = re.search(sku_pattern, suffix)
        if match:
            features['sku'] = match.group(0)

        # ---------------------------------------------------------
        # 3. LOGIQUE MATIÈRE (Élargie)
        # ---------------------------------------------------------
        if 'vvn' in slug_lower:
            features['material'] = 'Natural Cowhide (VVN)'
        elif 'monogram' in slug_lower:
            if 'empreinte' in slug_lower: features['material'] = 'Empreinte Leather'
            elif 'shadow' in slug_lower: features['material'] = 'Shadow Leather'
            elif 'eclipse' in slug_lower: features['material'] = 'Monogram Eclipse'
            elif 'reverse' in slug_lower: features['material'] = 'Monogram Reverse'
            elif 'vernis' in slug_lower: features['material'] = 'Vernis Leather'
            else: features['material'] = 'Monogram Canvas'
        elif 'damier' in slug_lower:
            if 'azur' in slug_lower: features['material'] = 'Damier Azur'
            elif 'graphite' in slug_lower: features['material'] = 'Damier Graphite'
            elif 'infini' in slug_lower: features['material'] = 'Damier Infini'
            else: features['material'] = 'Damier Ebene' # Default Damier
        elif 'epi' in slug_lower:
            features['material'] = 'Epi Leather'
        elif 'taurillon' in slug_lower:
            features['material'] = 'Taurillon Leather'
        elif 'aerogram' in slug_lower:
            features['material'] = 'Aerogram Leather'
        elif 'alligator' in slug_lower or 'crocodil' in slug_lower or 'python' in slug_lower:
            features['material'] = 'Exotic Leather'
        elif 'gold' in slug_lower or 'silver' in slug_lower or 'titanium' in slug_lower:
            features['material'] = 'Metal/Precious'
        
        # ---------------------------------------------------------
        # 4. LOGIQUE TYPE 
        # ---------------------------------------------------------
        if 'backpack' in slug_lower: features['type'] = 'Backpack'
        elif 'tote' in slug_lower or 'neverfull' in slug_lower or 'onthego' in slug_lower: features['type'] = 'Tote'
        elif 'messenger' in slug_lower or 'district' in slug_lower: features['type'] = 'Messenger'
        elif 'keepall' in slug_lower or 'duffle' in slug_lower: features['type'] = 'Travel/Keepall'
        elif 'speedy' in slug_lower: features['type'] = 'Handbag (Speedy)'
        elif 'capucines' in slug_lower: features['type'] = 'Handbag (Capucines)'
        elif 'wallet' in slug_lower or 'pocket' in slug_lower or 'porte-feuille' in slug_lower: features['type'] = 'Wallet/SLG'
        # Accessoires & Bijoux
        elif 'strap' in slug_lower or 'bandouliere' in slug_lower: features['type'] = 'Strap/Accessory'
        elif 'belt' in slug_lower or 'ceinture' in slug_lower: features['type'] = 'Belt'
        elif 'watch' in slug_lower or 'tambour' in slug_lower: features['type'] = 'Watch'
        elif 'bracelet' in slug_lower or 'ring' in slug_lower or 'earring' in slug_lower or 'pendant' in slug_lower: features['type'] = 'Jewelry'
        elif 'perfume' in slug_lower or 'parfum' in slug_lower: features['type'] = 'Perfume'
        
        # ---------------------------------------------------------
        # 5. LOGIQUE TAILLE
        # ---------------------------------------------------------
        if '-pm' in slug_lower: features['size'] = 'PM'
        elif '-mm' in slug_lower: features['size'] = 'MM'
        elif '-gm' in slug_lower: features['size'] = 'GM'
        elif '-bb' in slug_lower: features['size'] = 'BB'
        elif '25' in slug_lower: features['size'] = '25'
        elif '30' in slug_lower: features['size'] = '30'
        elif '35' in slug_lower: features['size'] = '35'
        elif '45' in slug_lower: features['size'] = '45'
        elif '50' in slug_lower: features['size'] = '50'
        elif '55' in slug_lower: features['size'] = '55'

    except Exception as e:
        print(f"⚠️ Erreur parsing URL: {url} -> {e}")

    return features

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction principale du pipeline ETL :
    1. Nettoie les données (clean_data)
    2. Enrichit via les URLs
    """
    print(f"🛠️ Début du pré-traitement sur {len(df)} lignes...")
    
    # 1. Nettoyage basique
    df = df.dropna(subset=['price'])

    # 2. Feature Engineering depuis l'URL
    if 'url' in df.columns:
        print("   -> Extraction des features depuis l'URL...")
        features_df = df['url'].apply(lambda x: pd.Series(extract_features_from_url(x)))
        df = pd.concat([df, features_df], axis=1)
        df['material'] = df['material'].fillna('Unknown')
    else:
        print("❌ Colonne 'url' manquante, pas d'enrichissement possible.")
    
    df = clean_data(df)

    print(f"✅ Pré-traitement terminé. Reste : {len(df)} lignes qualifiées.")
    return df

def preprocess_features(X: pd.DataFrame):
    """
    Fonction pour le Machine Learning (Encodage)
    À utiliser juste avant l'entraînement du modèle.
    """
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    X_encoded = encoder.fit_transform(X)
    return X_encoded, encoder