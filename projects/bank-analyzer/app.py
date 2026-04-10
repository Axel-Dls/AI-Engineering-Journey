# Stdlib
from pathlib import Path

# Third-party
import joblib
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv

# Local
from src.analyzer import (
    create_barplot,
    get_financial_summary,
    get_llm_categories_batch,
    get_month,
    get_monthly_stats,
    get_stats,
    load_transactions,
)
from src.file_parser import parse_ofx, parse_qif
from src.pdf_report import generate_pdf_report

# Chargement des variables d'environnement (clé API Gemini, etc.)
load_dotenv()

# Locale utilisée pour l'affichage des noms de mois
LOCALE = "fr"

st.title("Bank Analyzer 🏦")

BASE_DIR = Path(__file__).parent
filepath = BASE_DIR / "data" / "sample_transactions.csv"

# Chargement du fichier importé par l'utilisateur ou du fichier de démo par défaut
uploaded_file = st.file_uploader("Importe ton relevé bancaire 📂 (CSV, OFX, QIF)", type=None)
try:
    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix
        if suffix == ".csv":
            df = load_transactions(uploaded_file)
        elif suffix == ".qif":
            df = parse_qif(uploaded_file)
        elif suffix == ".ofx":
            df = parse_ofx(uploaded_file)
        else:
            st.error(f"Erreur : Format de fichier non supporté.")
            st.stop()
    else:
        df = load_transactions(filepath)
except ValueError as e:
    st.error(f"Erreur : {e}")
    st.stop()


@st.cache_resource
def load_model():
    # Mise en cache du modèle ML pour éviter de le recharger à chaque interaction Streamlit
    return joblib.load(BASE_DIR / "model.joblib")


model = load_model()

# Prédiction de la catégorie pour chaque transaction via le modèle ML
df['categorie'] = model.predict(df['libelle'])

# Pour les transactions catégorisées "Autre" par le modèle ML, on sollicite le LLM
mask = df['categorie'] == "Autre"
libelles_autres = df.loc[mask, 'libelle'].tolist()
if libelles_autres:
    df.loc[mask, 'categorie'] = get_llm_categories_batch(libelles_autres)

# Calcul des stats une seule fois pour éviter un double groupby
stats = get_stats(df)
couleurs = ["green" if x > 0 else "red" for x in stats.values]

df['mois'], ordre_mois = get_month(df, LOCALE)

summary = get_financial_summary(df)

st.header("📊 Bilan financier")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Revenus totaux", f"{summary['income']:.0f} €")
with col2:
    st.metric("Dépenses totales", f"{summary['expenses']:.0f} €")
with col3:
    st.metric("Taux d'épargne", f"{summary['savings_rate']:.1f} %")

st.header("📋 Transactions")
df_display = df.copy()
df_display['date'] = df_display['date'].dt.strftime('%d/%m/%Y')
st.dataframe(
    df_display,
    column_config={
        "date": st.column_config.TextColumn("Date"),
        "montant": st.column_config.NumberColumn(
            "Montant",
            format="%.2f €"
        ),
        "libelle": st.column_config.TextColumn("Libellé"),
        "categorie": st.column_config.TextColumn("Catégorie"),
        "mois": None,
    },
    hide_index=True
)

st.header("📊 Dépenses par catégorie")
fig, ax = plt.subplots()
create_barplot(stats, "categorie", "Bilan par catégorie", couleurs, ax=ax)
st.pyplot(fig)

st.header("📊 Bilan financier par mois")
mois_selectionnes = st.multiselect(
    "Sélectionne les mois à afficher",
    options=ordre_mois,
    default=ordre_mois  # tous sélectionnés par défaut
)
fig2, ax2 = plt.subplots()
create_barplot(get_monthly_stats(df, mois_selectionnes), "mois", "Bilan financier par mois", ax=ax2)
st.pyplot(fig2)

# Génération du rapport PDF avec le résumé déjà calculé (pas de double appel)
pdf_bytes = generate_pdf_report(df, summary)
st.download_button(
    label="📄 Télécharger le rapport PDF",
    data=pdf_bytes,
    file_name="rapport_financier.pdf",
    mime="application/pdf"
)
