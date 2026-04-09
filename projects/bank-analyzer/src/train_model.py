from pathlib import Path
from analyzer import load_transactions, categorize_transaction, get_my_model

import joblib

BASE_DIR = Path(__file__).parent.parent  # remonte à bank-analyzer/
DATA_PATH = BASE_DIR / "data" / "sample_transactions.csv"

# Charger et préparer les données
df = load_transactions(DATA_PATH)
df['categorie'] = df['libelle'].apply(categorize_transaction)

# Entraîner le modèle
model = get_my_model(df)

# Sauvegarder
joblib.dump(model, BASE_DIR / "model.joblib")
print("✅ Modèle entraîné et sauvegardé !")