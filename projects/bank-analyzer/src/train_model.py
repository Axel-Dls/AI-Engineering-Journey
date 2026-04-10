# Stdlib
import sys
from pathlib import Path

# Ajout du dossier racine au chemin pour permettre l'import de src.analyzer
# quel que soit le répertoire depuis lequel le script est exécuté
sys.path.insert(0, str(Path(__file__).parent.parent))

# Third-party
import joblib

# Local
from src.analyzer import categorize_transaction, get_my_model, load_transactions

BASE_DIR = Path(__file__).parent.parent  # remonte à bank-analyzer/
DATA_PATH = BASE_DIR / "data" / "sample_transactions.csv"

# Chargement et préparation des données d'entraînement
df = load_transactions(DATA_PATH)
df['categorie'] = df['libelle'].apply(categorize_transaction)

# Entraînement du modèle de classification
model = get_my_model(df)

# Sauvegarde du modèle entraîné sur disque
joblib.dump(model, BASE_DIR / "model.joblib")
print("✅ Modèle entraîné et sauvegardé !")
