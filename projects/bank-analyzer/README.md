# Bank Analyzer 🏦

Projet personnel d'apprentissage développé avec l'aide de Claude (Anthropic).

## Demo en ligne
👉 [Accéder à l'application](https://ai-engineering-journey-nh339jabwaxdty3ckkftf3.streamlit.app/)

## C'est quoi ?

Un outil qui analyse automatiquement les transactions bancaires d'un foyer. Il catégorise les dépenses et revenus, génère des graphiques et sort un rapport financier complet - le tout en Python avec une interface web.

La catégorisation est assurée par un modèle de Machine Learning (TF-IDF + Régression Logistique) entraîné sur les données du foyer, avec un taux de précision de 97%.

**Pourquoi TF-IDF + Régression Logistique ?** Les libellés bancaires sont des courtes chaînes de texte (ex: "CARREFOUR MARKET", "VIREMENT LOYER"). TF-IDF transforme ces textes en vecteurs numériques en pondérant les mots les plus discriminants. La Régression Logistique est ensuite parfaite pour ce type de classification : rapide à entraîner, interprétable, et très efficace sur des données peu volumineuses et bien séparables comme des catégories bancaires. Pas besoin de sortir l'artillerie lourde (réseau de neurones, etc.) quand un modèle simple fait le job à 97%.

Pour les transactions que le modèle ne reconnaît pas (catégorie "Autre"), un LLM (Gemini 2.5 Flash) prend le relais pour les catégoriser intelligemment.

Le projet a été développé dans le cadre de mon AI Engineering Journey, et a fait l'objet d'une review complète par Claude Code.

## Ce que ça fait

- Import d'un relevé bancaire CSV, OFX ou QIF
- Validation et nettoyage automatique des données
- Catégorisation des transactions par un modèle ML (TF-IDF + Régression Logistique, 97% de précision)
- Catégorisation des transactions inconnues via Gemini 2.5 Flash
- Graphique des dépenses par catégorie avec code couleur vert/rouge
- Graphique des dépenses par mois (en français), filtrable par mois
- Rapport financier : revenus, dépenses, taux d'épargne, top 5 des grosses dépenses
- Export du rapport en PDF (avec graphiques et tableaux)
- Interface optimisée : les données sont mises en cache, Gemini n'est appelé qu'une seule fois par fichier

## Stack technique

- Python 3.12
- Pandas - manipulation des données
- Seaborn / Matplotlib - visualisations
- Scikit-learn - modèle ML (TF-IDF + LogisticRegression)
- Streamlit - interface web
- Google Gemini 2.5 Flash - catégorisation LLM des transactions inconnues
- ReportLab - génération de rapports PDF
- Babel - internationalisation (noms des mois en français)
- Joblib - sauvegarde du modèle ML
- ofxparse / quiffen - parsing des formats OFX et QIF
- Pytest - tests unitaires
- uv - gestion des dépendances

## Installation

```bash
git clone https://github.com/Axel-Dls/AI-Engineering-Journey.git
cd AI-Engineering-Journey/projects/bank-analyzer
uv sync
```

## Lancer l'application

```bash
uv run streamlit run app.py
```

## Entraîner le modèle ML

```bash
uv run python src/train_model.py
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
│   ├── sample_transactions.csv   # Données de démo
│   ├── sample.ofx                # Fichier test OFX
│   └── sample.qif                # Fichier test QIF
├── src/
│   ├── __init__.py
│   ├── analyzer.py               # Fonctions principales
│   ├── file_parser.py            # Parsers OFX/QIF
│   ├── pdf_report.py             # Génération PDF
│   └── train_model.py            # Entraînement du modèle ML
├── tests/
│   ├── conftest.py               # Configuration pytest
│   └── test_analyzer.py          # Tests unitaires
├── app.py                        # Interface Streamlit
├── pyproject.toml                # Dépendances du projet
└── README.md
```

---

*Projet réalisé dans le cadre de mon AI Engineering Journey.*