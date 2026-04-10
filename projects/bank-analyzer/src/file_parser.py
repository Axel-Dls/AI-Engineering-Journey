from ofxparse import OfxParser
from quiffen import Qif
import pandas as pd
import codecs
import tempfile
import os

from io import BytesIO
from src.analyzer import validate_and_clean_transactions

def parse_ofx(filepath) -> pd.DataFrame:
    content = BytesIO(filepath.read())
    ofx = OfxParser.parse(content)
    account = ofx.account
    statement = account.statement

    lst_transaction = []

    for trans in statement.transactions:
        lst_transaction.append({'date': trans.date, 'libelle': trans.memo, 'montant': trans.amount})

    return validate_and_clean_transactions(pd.DataFrame(lst_transaction))

def parse_qif(filepath) -> pd.DataFrame:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.qif') as tmp:
        tmp.write(filepath.read())
        tmp_path = tmp.name

    qif = Qif.parse(tmp_path, day_first=False)
    os.unlink(tmp_path)

    acc = list(qif.accounts.values())[0]
    lst_transaction = []
    for tr in list(acc.transactions.values())[0]:
        lst_transaction.append({'date': tr.date, 'libelle': tr.payee, 'montant': tr.amount})

    return validate_and_clean_transactions(pd.DataFrame(lst_transaction))