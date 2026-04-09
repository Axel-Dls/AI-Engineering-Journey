from io import BytesIO

import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import pandas as pd
from src.analyzer import get_financial_summary, get_stats, get_monthly_stats, create_barplot

def generate_pdf_report(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Titre
    story.append(Paragraph("Rapport Financier", styles['Title']))
    story.append(Spacer(1, 0.5 * cm))

    # Métriques
    summary = get_financial_summary(df)
    story.append(Paragraph("Bilan financier", styles['Heading1']))
    metrics = [
        ["Revenus totaux", f"{summary['income']:.0f} €"],
        ["Dépenses totales", f"{summary['expenses']:.0f} €"],
        ["Taux d'épargne", f"{summary['savings_rate']:.1f} %"],
    ]
    table = Table(metrics, colWidths=[8*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    # Top 5 dépenses
    story.append(Paragraph("Top 5 dépenses", styles['Heading1']))
    top5 = summary['top_five_expenses']
    top5_data = [["Libellé", "Montant"]] + [
        [row['libelle'], f"{row['montant']:.2f} €"]
        for _, row in top5.iterrows()
    ]
    table_top5 = Table(top5_data, colWidths=[11*cm, 4*cm])
    table_top5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.red),
    ]))
    story.append(table_top5)
    story.append(Spacer(1, 0.5 * cm))

    # Montant par catégorie avec couleurs
    story.append(Paragraph("Montant par catégorie", styles['Heading1']))
    stats = get_stats(df)
    cat_data = [["Catégorie", "Montant"]]
    for categorie, montant in stats.items():
        cat_data.append([categorie, f"{montant:.2f} €"])
    table_cat = Table(cat_data, colWidths=[9*cm, 5*cm])
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]
    for i, (_, montant) in enumerate(stats.items(), start=1):
        color = colors.HexColor('#27ae60') if montant > 0 else colors.HexColor('#e74c3c')
        style_cmds.append(('TEXTCOLOR', (1, i), (1, i), color))
    table_cat.setStyle(TableStyle(style_cmds))
    story.append(table_cat)
    story.append(Spacer(1, 0.5 * cm))

    # Graphiques
    story.append(Paragraph("Graphiques", styles['Heading1']))
    for title, serie, x_col in [
        ("Dépenses par catégorie", get_stats(df), "categorie"),
        ("Bilan par mois", get_monthly_stats(df, list(df['mois'].unique())), "mois"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 4))
        couleurs = ["green" if x > 0 else "red" for x in serie.values]
        create_barplot(serie, x_col, title, couleurs, ax=ax)
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        img_buffer.seek(0)
        story.append(Image(img_buffer, width=16*cm, height=7*cm))
        story.append(Spacer(1, 0.3 * cm))

    doc.build(story)
    return buffer.getvalue()