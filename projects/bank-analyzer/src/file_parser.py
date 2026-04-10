# Stdlib
import os
import tempfile
from io import BytesIO

# Third-party
import pandas as pd
from ofxparse import OfxParser
from quiffen import Qif

# Local
from src.analyzer import validate_and_clean_transactions


def parse_ofx(filepath) -> pd.DataFrame:
    # Lecture du contenu en mémoire pour compatibilité avec les objets UploadedFile de Streamlit
    content = BytesIO(filepath.read())
    ofx = OfxParser.parse(content)
    account = ofx.account
    statement = account.statement

    lst_transaction = [
        {'date': t.date, 'libelle': t.memo, 'montant': t.amount}
        for t in statement.transactions
    ]

    return validate_and_clean_transactions(pd.DataFrame(lst_transaction))


def parse_qif(filepath) -> pd.DataFrame:
    # quiffen nécessite un fichier sur disque : on crée un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.qif') as tmp:
        tmp.write(filepath.read())
        tmp_path = tmp.name

    qif = Qif.parse(tmp_path, day_first=False)
    os.unlink(tmp_path)

    # Vérification de la présence d'au moins un compte et d'une liste de transactions
    if not qif.accounts:
        raise ValueError("Le fichier QIF ne contient aucun compte.")

    acc = list(qif.accounts.values())[0]

    if not acc.transactions:
        raise ValueError("Le fichier QIF ne contient aucune transaction.")

    lst_transaction = [
        {'date': tr.date, 'libelle': tr.payee, 'montant': tr.amount}
        for tr in list(acc.transactions.values())[0]
    ]

    return validate_and_clean_transactions(pd.DataFrame(lst_transaction))
