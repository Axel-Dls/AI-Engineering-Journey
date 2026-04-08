# Bank Analyzer 🏦

Projet personnel d'apprentissage développé avec l'aide de Claude (Anthropic).

## Description

Bank Analyzer est un outil d'analyse automatique des transactions bancaires d'un foyer. Il catégorise les dépenses et revenus, génère des visualisations et produit un rapport financier complet - le tout en Python, sans interface graphique complexe.

Ce projet est en constante évolution au fil de mon apprentissage de Python, Pandas, Seaborn et de l'IA.

## Fonctionnalités

- Chargement de relevés bancaires au format CSV
- Catégorisation automatique des transactions par règles métier
- Graphique des dépenses/revenus par catégorie (vert/rouge)
- Graphique des dépenses par mois
- Rapport financier : revenus, dépenses, taux d'épargne, top 5 des dépenses

## Technologies utilisées

- Python 3.12
- Pandas - manipulation et analyse des données
- Seaborn / Matplotlib - visualisations
- Pathlib - gestion des chemins de fichiers
- uv - gestion des dépendances

## Installation

```bash
# Cloner le repo
git clone https://github.com/Axel-Dls/AI-Engineering-Journey.git
cd AI-Engineering-Journey

# Installer les dépendances
uv install
```

## Utilisation

```bash
uv run python projects/bank-analyzer/src/analyzer.py
```

Le script attend un fichier CSV dans `projects/bank-analyzer/data/` avec les colonnes suivantes :

```
date,montant,libelle
2024-01-01,2800.00,VIREMENT SALAIRE
2024-01-02,-850.00,VIREMENT LOYER
```

## Structure du projet

```
bank-analyzer/
├── data/
│   └── sample_transactions.csv   # Données de test
├── src/
│   └── analyzer.py               # Script principal
└── README.md
```

## Roadmap

- [ ] Export du rapport en PDF
- [ ] Interface web avec Streamlit
- [ ] Catégorisation intelligente avec un LLM (GPT / Claude)
- [ ] Support de plusieurs formats bancaires (OFX, QIF)

---

*Projet en cours de développement - partie d'une transition vers un poste d'AI Engineer.*
