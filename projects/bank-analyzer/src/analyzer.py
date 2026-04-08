from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).parent.parent
sample_transactions = pd.read_csv(BASE_DIR / "data" / "sample_transactions.csv")

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

def categorize_transaction(libelle: str) -> str:
    for key, val in categories_rules.items():
        if any(categ in libelle for categ in val):
            return key
    return "Autre" 

def add_categ(row):
    return categorize_transaction(row['libelle'])

def create_barplot(mt_by_categ):
    df_plot = mt_by_categ.reset_index()
    couleurs = ["green" if x > 0 else "red" for x in mt_by_categ.values]
    sns.barplot(data=df_plot, x="categorie", y="montant", hue="categorie", palette=couleurs, legend=False)
    plt.title("Bilan financier annuel par catégorie")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

if __name__ == "__main__":
    sample_transactions['categorie'] = sample_transactions.apply(add_categ, axis=1)
    #print(sample_transactions[sample_transactions['categorie'] == "Autre"]["libelle"].unique())
    mt_by_categ = sample_transactions.groupby(["categorie"])["montant"].sum().sort_values(ascending=False)
    create_barplot(mt_by_categ)
    plt.show()