from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from babel import Locale

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from pandas.api.types import is_numeric_dtype

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

def get_my_model(df: pd.DataFrame) -> Pipeline:
    X = df['libelle']
    y = df['categorie']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression())
    ])

    model.fit(X_train, y_train)

    return model

def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    if df.isnull().values.any():
        df['libelle'] = df['libelle'].fillna("INCONNU")
        df = df.dropna(subset=['montant', 'date'])
        return df
    return df

def load_transactions(filepath) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    if df.columns.isin(['date', 'montant', 'libelle']).all():
        df['date'] = pd.to_datetime(df['date'])
        if is_numeric_dtype(df['montant']):
            df = clean_transactions(df)
            return df
        else:
            raise ValueError("Le format du montant n'est pas numérique")
    else:
        raise ValueError("Le CSV n'a pas le format souhaité.")

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

def get_monthly_stats(df: pd.DataFrame, mois_selectionnes: list) -> pd.Series:
    return df.groupby(df['mois'])["montant"].sum().reindex(mois_selectionnes)

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
