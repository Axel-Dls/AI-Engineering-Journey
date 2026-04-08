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
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df 

def categorize_transaction(libelle: str) -> str:
    for key, val in categories_rules.items():
        if any(categ in libelle for categ in val):
            return key
    return "Autre" 

def create_barplot(serie: pd.Series, x_col: str, title: str, color=None) -> None:
    df_plot = serie.reset_index()
    sns.barplot(data=df_plot, x=x_col, y="montant", hue=x_col, palette=color, legend=False)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

def get_stats(df: pd.DataFrame) -> pd.Series:
    return df.groupby(["categorie"])["montant"].sum().sort_values(ascending=False)

def get_monthly_stats(df: pd.DataFrame) -> pd.Series:
    ordre_mois = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    return df.groupby(df['mois'])["montant"].sum().reindex(ordre_mois)

def main() -> None:
    filepath = BASE_DIR / "data" / "sample_transactions.csv"
    
    df = load_transactions(filepath)
    df['categorie'] = df['libelle'].apply(categorize_transaction)
    df['mois'] = df['date'].dt.month_name()
    couleurs = ["green" if x > 0 else "red" for x in get_stats(df).values]
    

    plt.figure()
    create_barplot(get_stats(df),"categorie", "Bilan financier annuelle par catégories", couleurs)

    plt.figure()
    create_barplot(get_monthly_stats(df),"mois", "Bilan financier par mois")

    plt.show()

if __name__ == "__main__":
    main()
    