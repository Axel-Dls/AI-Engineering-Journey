# Stdlib
import logging
import os
import re
from pathlib import Path

# Third-party
from babel import Locale
from dotenv import load_dotenv
from google import genai
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

# Chargement des variables d'environnement au démarrage du module
load_dotenv()

# Client Gemini créé une seule fois pour éviter de recréer une connexion HTTP à chaque appel
_gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Règles de catégorisation basées sur des mots-clés dans le libellé de la transaction
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
    # Séparation des features (libellé) et de la cible (catégorie)
    X = df['libelle']
    y = df['categorie']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Pipeline TF-IDF + régression logistique pour la classification de texte
    model = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression())
    ])

    model.fit(X_train, y_train)

    return model


def validate_and_clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    # Vérification que les colonnes obligatoires sont présentes (tolère les colonnes supplémentaires)
    required = {'date', 'montant', 'libelle'}
    if not required.issubset(df.columns):
        raise ValueError("Le CSV n'a pas le format souhaité.")

    # La conversion lève une ValueError si une valeur n'est pas numérique
    df['montant'] = pd.to_numeric(df['montant'], errors='raise')

    # Nettoyage des valeurs manquantes : libellé inconnu, lignes sans montant/date supprimées
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
    # Parcours des règles : retourne la première catégorie dont un mot-clé est présent dans le libellé
    for key, val in categories_rules.items():
        if any(categ in libelle for categ in val):
            return key
    return "Autre"


def get_month(df: pd.DataFrame, lang: str = "en") -> tuple[pd.Series, list]:
    # Conversion du numéro de mois en nom localisé (ex: 1 → "janvier" en français)
    locale = Locale(lang)
    months = locale.months['format']['wide']
    ordre_mois = [months[i] for i in range(1, 13)]
    return df['date'].dt.month.map(months), ordre_mois


def create_barplot(serie: pd.Series, x_col: str, title: str, color=None, ax=None) -> None:
    df_plot = serie.reset_index()
    sns.barplot(data=df_plot, x=x_col, y="montant", hue=x_col, palette=color, legend=False, ax=ax)
    # Utilisation de l'objet ax directement pour éviter d'affecter d'autres figures ouvertes
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=45)
    ax.figure.tight_layout()


def get_stats(df: pd.DataFrame) -> pd.Series:
    # Somme des montants par catégorie, triée du plus élevé au plus faible
    return df.groupby(["categorie"])["montant"].sum().sort_values(ascending=False)


def get_monthly_stats(df: pd.DataFrame, mois_selectionnes: list) -> pd.Series:
    # Somme mensuelle réindexée sur les mois sélectionnés pour conserver l'ordre
    return df.groupby(df['mois'])["montant"].sum().reindex(mois_selectionnes)


def get_financial_summary(df: pd.DataFrame) -> dict:
    income = df[df['montant'] > 0]['montant'].sum()
    expenses = df[df['montant'] < 0]['montant'].sum()
    # Protection contre la division par zéro si aucun revenu n'est présent
    savings_rate = ((income + expenses) / income * 100) if income != 0 else 0.0
    top_five_expenses = (
        df[df['montant'] < 0][['libelle', 'montant']]
        .sort_values(by='montant', ascending=True)
        .head()
    )
    average_monthly_spending = df.groupby(df['mois'])["montant"].sum().mean()
    top_categ_expense = (
        df.groupby(["categorie"])["montant"].sum()
        .sort_values(ascending=True)
        .head(1)
    )

    return {
        "income": income,
        "expenses": expenses,
        "savings_rate": savings_rate,
        "top_five_expenses": top_five_expenses,
        "average_monthly_spending": average_monthly_spending,
        "top_categ_expense": top_categ_expense,
    }


def get_llm_categories_batch(libelles: list) -> list:
    categories = list(categories_rules.keys())

    # Numérotation des libellés pour que le LLM puisse répondre ligne par ligne
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
        response = _gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt_text
        )

        raw = response.text
        # Extraction des réponses numérotées via regex pour gérer les lignes parasites du LLM
        results = {}
        for line in raw.split('\n'):
            m = re.match(r'^(\d+)\.\s+(.+)', line.strip())
            if m:
                results[int(m.group(1))] = m.group(2).strip()
        # Si une ligne est absente de la réponse, on retombe sur "Autre"
        return [results.get(i + 1, "Autre") for i in range(len(libelles))]
    except Exception as e:
        logger.warning("LLM categorization failed: %s", e)
        return ["Autre"] * len(libelles)
