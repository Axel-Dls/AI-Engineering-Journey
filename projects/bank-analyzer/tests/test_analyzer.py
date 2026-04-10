# Stdlib
import io

# Third-party
import pandas as pd
import pytest

# Local (conftest.py ajoute src/ au sys.path)
from analyzer import categorize_transaction, get_financial_summary, load_transactions, validate_and_clean_transactions


def test_categorize_transaction():
    # Vérifie que le mot-clé "CARREFOUR" déclenche bien la catégorie "Courses"
    assert categorize_transaction("CARREFOUR MARKET") == "Courses"


def test_categorize_transaction_unknown():
    # Vérifie que tout libellé non reconnu retourne "Autre"
    assert categorize_transaction("TRUC INCONNU") == "Autre"


def test_load_transaction_without_mt():
    # Un CSV sans les colonnes obligatoires doit lever une ValueError
    with pytest.raises(ValueError):
        faux_csv = io.StringIO("col1,col2\n1,2\n3,4")
        df = load_transactions(faux_csv)


def test_clean_transactions():
    # Les valeurs manquantes doivent être nettoyées : libellé → "INCONNU", lignes sans montant/date supprimées
    df = pd.DataFrame({
        'date': ['2024-01-01', None],
        'montant': [100.0, None],
        'libelle': ['CARREFOUR', None]
    })
    assert validate_and_clean_transactions(df).isnull().values.any() == False


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
    # Vérification des clés et des valeurs calculées
    assert set(keys) == set(mon_dict.keys())
    assert mon_dict["income"] == pytest.approx(2800.0)
    assert mon_dict["expenses"] == pytest.approx(-915.0)
    assert mon_dict["savings_rate"] == pytest.approx(67.32, abs=0.1)
