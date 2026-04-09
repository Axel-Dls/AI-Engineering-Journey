import io
import pytest
import pandas as pd
import numpy as np

from analyzer import categorize_transaction, load_transactions, clean_transactions, get_financial_summary

def test_categorize_transaction():
    assert categorize_transaction("CARREFOUR MARKET") == "Courses"

def test_categorize_transaction_unknown():
    assert categorize_transaction("TRUC INCONNU") == "Autre"

def test_load_transaction_without_mt():
    with pytest.raises(ValueError):
        faux_csv = io.StringIO("col1,col2\n1,2\n3,4")
        df = load_transactions(faux_csv)

def test_clean_transactions():
    df = pd.DataFrame({
        'date': ['2024-01-01', None],
        'montant': [100.0, None],
        'libelle': ['CARREFOUR', None]
    })
    assert clean_transactions(df).isnull().values.any() == False

def test_get_financial_summary():
    df = pd.DataFrame({
        "date": ['2024-01-01', '2024-01-02', '2024-01-03'],
        "montant": [2800.00, -850.00, -65.00],
        "libelle": ['VIREMENT SALAIRE JANVIER', 'VIREMENT LOYER JANVIER', 'CARREFOUR MARKET'],
        "mois": ['janvier', 'janvier', 'janvier'],
        "categorie": ['Salaire', 'Loyer', 'Courses']
    })

    mon_dict = get_financial_summary(df)
    keys = ["income", "expenses", "savings_rate", "top_five_expenses", "average_monthly_spending", "top_categ_expense"]
    assert set(keys) == set(mon_dict.keys())