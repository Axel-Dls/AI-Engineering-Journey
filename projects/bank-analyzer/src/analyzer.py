from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from google import genai

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

def validate_and_clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    if not df.columns.isin(['date', 'montant', 'libelle']).all():
        raise ValueError("Le CSV n'a pas le format souhaité.")

    df['montant'] = pd.to_numeric(df['montant'], errors='raise')
    if not is_numeric_dtype(df['montant']):
        raise ValueError("Le format du montant n'est pas numérique")
    
    if df.isnull().values.any():
        df['libelle'] = df['libelle'].fillna("INCONNU")
        df = df.dropna(subset=['montant', 'date'])
    
    df['date'] = pd.to_datetime(df['date'])

    return df

def load_transactions(filepath) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df = validate_and_clean_transactions(df)
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

def get_llm_categories_batch(libelles: list) -> list:
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    categories = list(categories_rules.keys())
    
    libelles_numerotes = "\n".join(
        [f"{i+1}. {libelle}" for i, libelle in enumerate(libelles)]
    )
    
    prompt_text = (
        f"Tu es un assistant qui catégorise des transactions bancaires françaises. "
        f"Voici les catégories disponibles : {', '.join(categories)}. "
        f"Pour chaque libellé numéroté, réponds uniquement avec le numéro et la catégorie exacte. "
        f"Format attendu : '1. Catégorie'\n\n"
        f"Libellés :\n{libelles_numerotes}"
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt_text
        )
        
        raw = response.text
        return [line.split(". ")[1] for line in raw.split('\n') if line.strip()]
    except Exception:
        return ["Autre"]*len(libelles)
