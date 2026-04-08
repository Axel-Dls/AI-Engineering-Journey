from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).parent.parent

# La logique : si le libellé CONTIENT un de ces mots → cette catégorie
categories_rules = {
    "Remboursements": ["REMBOURSEMENT"],
    "Courses": ["CARREFOUR", "LECLERC", "LIDL", "AUCHAN", "INTERMARCHE", "MONOPRIX", "COURSES"],
    "Abonnements": ["NETFLIX", "SPOTIFY", "DISNEY", "CANAL", "AMAZON PRIME"],
    "Loyer": ["LOYER"],
    "Salaire": ["SALAIRE"],
    "Restaurant": ["MCDONALDS", "PIZZA", "BURGER", "RESTAU", "BISTROT", "RESTO", "BOULANGERIE"],
    "Transport": ["SNCF", "PARKING", "ESSENCE", "TOTAL", "BP", "SHELL"],
    "Santé": ["PHARMACIE", "MUTUELLE", "CPAM"],
    "Shopping": ["ZARA", "H&M", "NIKE", "FNAC", "AMAZON", "IKEA", "VETEMENTS", "DECATHLON"],
    "Factures": ["EDF", "ORANGE"],
    "Assurances": ["ASSURANCE"],
    "Vacances": ["VOYAGE", "BILLET AVION", "HOTEL", "AIRBNB", "VACANCES", "ACTIVITE", "SOUVENIRS"],
    "Loisirs":  ["CINEMA", "BOWLING", "GLACES"],
    "Auto": ["REPARATION", "AUTO", "VOITURE", "CONTROLE TECHNIQUE"],
    "Virements": ["VIREMENT"]
}

def load_transactions(filepath) -> pd.DataFrame:
    return pd.read_csv(filepath)

def categorize_transaction(libelle: str) -> str:
    for key, val in categories_rules.items():
        if any(categ in libelle for categ in val):
            return key
    return "Autre" 

def create_barplot(mt_by_categ: pd.Series) -> None:
    df_plot = mt_by_categ.reset_index()
    couleurs = ["green" if x > 0 else "red" for x in mt_by_categ.values]
    sns.barplot(data=df_plot, x="categorie", y="montant", hue="categorie", palette=couleurs, legend=False)
    plt.title("Bilan financier annuel par catégorie")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

def get_stats(df: pd.DataFrame) -> pd.Series:
    return df.groupby(["categorie"])["montant"].sum().sort_values(ascending=False)



def main() -> None:
    filepath = BASE_DIR / "data" / "sample_transactions.csv"
    df = load_transactions(filepath)
    df['categorie'] = df['libelle'].apply(categorize_transaction)
    create_barplot(get_stats(df))
    plt.show()

if __name__ == "__main__":
    main()
    