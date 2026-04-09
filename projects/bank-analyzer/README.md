# Bank Analyzer 🏦

Projet personnel d'apprentissage développé avec l'aide de Claude (Anthropic).

## Demo en ligne
👉 [Accéder à l'application](https://ai-engineering-journey-nh339jabwaxdty3ckkftf3.streamlit.app/)

## C'est quoi ?

Un outil qui analyse automatiquement les transactions bancaires d'un foyer. Il catégorise les dépenses et revenus, génère des graphiques et sort un rapport financier complet - le tout en Python avec une interface web.

La catégorisation est assurée par un modèle de Machine Learning (TF-IDF + Régression Logistique) entraîné sur les données du foyer, avec un taux de précision de 97%.

Le projet évolue au fur et à mesure de mon apprentissage de Python, Pandas, Scikit-learn, Streamlit et de l'IA.

## Ce que ça fait

- Import d'un relevé bancaire CSV (ou utilisation des données de démo)
- Validation et nettoyage automatique des données
- Catégorisation des transactions par un modèle ML
- Graphique des dépenses par catégorie avec code couleur vert/rouge
- Graphique des dépenses par mois (en français)
- Rapport financier : revenus, dépenses, taux d'épargne, top 5 des grosses dépenses

## Stack technique

- Python 3.12
- Pandas - manipulation des données
- Seaborn / Matplotlib - visualisations
- Scikit-learn - modèle ML (TF-IDF + LogisticRegression)
- Streamlit - interface web
- Babel - internationalisation (noms des mois en français)
- Joblib - sauvegarde du modèle ML
- Pytest - tests unitaires
- uv - gestion des dépendances

## Installation

```bash
git clone https://github.com/Axel-Dls/AI-Engineering-Journey.git
cd AI-Engineering-Journey/projects/bank-analyzer
uv install
```

## Lancer l'application

```bash
uv run streamlit run app.py
```

## Entraîner le modèle ML

```bash
cd src
uv run python train_model.py
```

## Lancer les tests

```bash
uv run pytest tests/
```

## Format CSV attendu

```
date,montant,libelle
2024-01-01,2800.00,VIREMENT SALAIRE
2024-01-02,-850.00,VIREMENT LOYER
```

## Structure

```
bank-analyzer/
├── data/
│   └── sample_transactions.csv   # Données de démo
├── src/
│   ├── analyzer.py               # Fonctions principales
│   └── train_model.py            # Entraînement du modèle ML
├── tests/
│   ├── conftest.py               # Configuration pytest
│   └── test_analyzer.py          # Tests unitaires
├── app.py                        # Interface Streamlit
├── model.joblib                  # Modèle ML sauvegardé
└── README.md
```

## Ce qui est prévu

- [ ] Export du rapport en PDF
- [ ] Catégorisation avec un LLM pour les transactions inconnues
- [ ] Support d'autres formats bancaires (OFX, QIF)
- [ ] Comparaison mois par mois

---

*Projet en cours, dans le cadre d'une transition vers un poste d'AI Engineer.*
