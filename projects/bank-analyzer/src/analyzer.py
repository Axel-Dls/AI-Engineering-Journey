from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent.parent
sample_transactions = pd.read_csv(BASE_DIR / "data" / "sample_transactions.csv")

if __name__ == "__main__":
    print(sample_transactions.head())