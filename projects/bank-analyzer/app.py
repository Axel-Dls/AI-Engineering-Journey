import streamlit as st
import matplotlib.pyplot as plt

from pathlib import Path
from src.analyzer import (
    load_transactions,
    categorize_transaction,
    get_stats,
    get_monthly_stats,
    get_financial_summary,
    create_barplot,
    get_month
)

st.title("Bank Analyzer 🏦")

BASE_DIR = Path(__file__).parent
filepath = BASE_DIR / "data" / "sample_transactions.csv"
uploaded_file = st.file_uploader("Importe ton relevé bancaire 📂", type="csv")

if uploaded_file is not None:
    df = load_transactions(uploaded_file)
else:
    df = load_transactions(filepath)

df['categorie'] = df['libelle'].apply(categorize_transaction)
couleurs = ["green" if x > 0 else "red" for x in get_stats(df).values]

df['mois'], ordre_mois = get_month(df, "fr")

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
create_barplot(get_stats(df), "categorie", "Bilan par catégorie", couleurs, ax=ax)
st.pyplot(fig)

st.header("📊 Bilan financier par mois")
fig2, ax2 = plt.subplots()
create_barplot(get_monthly_stats(df, ordre_mois), "mois", "Bilan financier par mois", ax=ax2)
st.pyplot(fig2)