from pathlib import Path
from babel import Locale

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

def get_month(df: pd.DataFrame, lang: str = "en") -> tuple[pd.Series, list]:
    locale = Locale(lang)
    months = locale.months['format']['wide']
    ordre_mois = [months[i] for i in range(1, 13)]
    return df['date'].dt.month.map(months), ordre_mois

def create_barplot(serie: pd.Series, x_col: str, title: str, color=None, ax=None) -> None:
    df_plot = serie.reset_index()
    sns.barplot(data=df_plot, x=x_col, y="montant", hue=x_col, palette=color, legend=False, ax=ax)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

def get_stats(df: pd.DataFrame) -> pd.Series:
    return df.groupby(["categorie"])["montant"].sum().sort_values(ascending=False)

def get_monthly_stats(df: pd.DataFrame, ordre_mois: list) -> pd.Series:
    return df.groupby(df['mois'])["montant"].sum().reindex(ordre_mois)

def get_financial_summary(df: pd.DataFrame) -> dict:
    income = df[df['montant'] > 0]['montant'].sum()
    expenses = df[df['montant'] < 0]['montant'].sum()
    savings_rate = ((income + expenses) / income) * 100
    top_five_expenses = df[df['montant'] < 0][['libelle', 'montant']].sort_values(by='montant', ascending=True).head()
    average_monthly_spending = df.groupby(df['mois'])["montant"].sum().mean()
    top_categ_expense = df.groupby(["categorie"])["montant"].sum().sort_values(ascending=True).head(1)

    return {
        "income": income,
        "expenses": expenses,
        "savings_rate": savings_rate,
        "top_five_expenses": top_five_expenses,
        "average_monthly_spending": average_monthly_spending, 
        "top_categ_expense": top_categ_expense
    }

'''
def main() -> None:
    filepath = BASE_DIR / "data" / "sample_transactions.csv"
    df = load_transactions(filepath)
    df['categorie'] = df['libelle'].apply(categorize_transaction)

    
    df['mois'], ordre_mois = get_month(df, "en")
    
    
    plt.figure()
    create_barplot(get_stats(df),"categorie", "Bilan financier annuelle par catégories", couleurs)
    plt.figure()
    create_barplot(get_monthly_stats(df),"mois", "Bilan financier par mois")
    plt.show()
    get_financial_summary(df)
'''
    
'''
if __name__ == "__main__":
    main()
'''