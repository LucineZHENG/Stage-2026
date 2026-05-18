#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_results.py
==================
比较 BiLSTM-CRF 和 XLM-RoBERTa 在 test set 上的 NER 结果。
读取两个 test_results.json，生成对比表（终端 + Markdown 文件）。

Usage (dans ~/prima_ner/) :
    python3 compare_results.py

Prérequis :
    ~/prima_ner/bilstm_crf/logs/test_results.json
    ~/prima_ner/xlm_roberta/logs/test_results.json
"""

import json
import os
from datetime import datetime

BILSTM_PATH  = "./bilstm_crf/logs/test_results.json"
XLMR_PATH    = "./xlm_roberta/logs/test_results.json"
OUT_PATH     = "./comparison_results.md"

LABELS = ["auteur", "ouvrage", "material", "date", "etat"]

# ── Charger les résultats ─────────────────────────────────────────────────────
with open(BILSTM_PATH, encoding="utf-8") as f:
    bilstm = json.load(f)
with open(XLMR_PATH, encoding="utf-8") as f:
    xlmr = json.load(f)

def get_label_metrics(results, label):
    """Extrait P/R/F1 pour un label donné depuis le rapport seqeval."""
    report = results.get("test_report_by_label", {})
    # seqeval utilise le nom du label directement (sans B-/I-)
    for key in report:
        if key.lower() == label.lower():
            m = report[key]
            return round(m.get("precision", 0), 3), \
                   round(m.get("recall", 0), 3), \
                   round(m.get("f1-score", 0), 3)
    return 0.0, 0.0, 0.0

# ── Affichage terminal ────────────────────────────────────────────────────────
print("=" * 65)
print("  PRIMA NER — Comparaison BiLSTM-CRF vs XLM-RoBERTa")
print("=" * 65)

print(f"\n{'Système':<20} {'Val F1':>8} {'Test F1':>8} {'Test P':>8} {'Test R':>8}")
print("-" * 55)
for name, res in [("BiLSTM-CRF", bilstm), ("XLM-RoBERTa", xlmr)]:
    tm = res["test_metrics"]
    print(f"{name:<20} {res['best_val_f1']:>8.4f} {tm['f1']:>8.4f} "
          f"{tm['precision']:>8.4f} {tm['recall']:>8.4f}")

print(f"\n{'Label':<12} {'BiLSTM P':>9} {'BiLSTM R':>9} {'BiLSTM F1':>10} "
      f"{'XLMR P':>9} {'XLMR R':>9} {'XLMR F1':>10}")
print("-" * 70)
for label in LABELS:
    bp, br, bf = get_label_metrics(bilstm, label)
    xp, xr, xf = get_label_metrics(xlmr,   label)
    winner = "←" if bf > xf else ("→" if xf > bf else "=")
    print(f"{label:<12} {bp:>9.3f} {br:>9.3f} {bf:>10.3f} "
          f"{xp:>9.3f} {xr:>9.3f} {xf:>10.3f}  {winner}")

print()
print(f"BiLSTM-CRF  : epochs={bilstm['epochs']}, lr={bilstm['lr']}, "
      f"embed={bilstm['embed_dim']}, hidden={bilstm['hidden_dim']}, "
      f"vocab={bilstm['vocab_size']}, "
      f"temps={bilstm['total_training_time_min']} min")
print(f"XLM-RoBERTa : epochs={xlmr['epochs']}, lr={xlmr['lr']}, "
      f"batch={xlmr['batch_size']}, "
      f"temps={xlmr['total_training_time_min']} min")

# ── Export Markdown ───────────────────────────────────────────────────────────
lines = []
lines.append("# PRIMA NER — Comparaison BiLSTM-CRF vs XLM-RoBERTa\n")
lines.append(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
lines.append("Données : 100 entrées annotées (train=70, val=20, test=10), seed=42\n")

lines.append("## Résultats globaux\n")
lines.append("| Système | Val F1 | Test F1 | Test Precision | Test Recall |")
lines.append("|---|---|---|---|---|")
for name, res in [("BiLSTM-CRF", bilstm), ("XLM-RoBERTa", xlmr)]:
    tm = res["test_metrics"]
    lines.append(f"| {name} | {res['best_val_f1']:.4f} | {tm['f1']:.4f} | "
                 f"{tm['precision']:.4f} | {tm['recall']:.4f} |")

lines.append("\n## Résultats par label (test set)\n")
lines.append("| Label | BiLSTM P | BiLSTM R | BiLSTM F1 | XLMR P | XLMR R | XLMR F1 | Meilleur |")
lines.append("|---|---|---|---|---|---|---|---|")
for label in LABELS:
    bp, br, bf = get_label_metrics(bilstm, label)
    xp, xr, xf = get_label_metrics(xlmr,   label)
    winner = "BiLSTM-CRF" if bf > xf else ("XLM-RoBERTa" if xf > bf else "égalité")
    lines.append(f"| {label} | {bp:.3f} | {br:.3f} | {bf:.3f} | "
                 f"{xp:.3f} | {xr:.3f} | {xf:.3f} | {winner} |")

lines.append("\n## Hyperparamètres\n")
lines.append("| Paramètre | BiLSTM-CRF | XLM-RoBERTa |")
lines.append("|---|---|---|")
lines.append(f"| Modèle de base | From scratch | xlm-roberta-base |")
lines.append(f"| Epochs | {bilstm['epochs']} | {xlmr['epochs']} |")
lines.append(f"| Learning rate | {bilstm['lr']} | {xlmr['lr']} |")
lines.append(f"| Batch size | {bilstm['batch_size']} | {xlmr['batch_size']} |")
lines.append(f"| Vocab size | {bilstm['vocab_size']} | N/A (SentencePiece) |")
lines.append(f"| Embed dim | {bilstm['embed_dim']} | 768 (fixe) |")
lines.append(f"| Hidden dim | {bilstm['hidden_dim']} | N/A |")
lines.append(f"| Temps entraînement | {bilstm['total_training_time_min']} min | {xlmr['total_training_time_min']} min |")

lines.append("\n## Analyse\n")
lines.append("- XLM-RoBERTa surpasse BiLSTM-CRF sur tous les labels sauf `date` (égalité à 1.00)")
lines.append("- Le gain le plus important est sur `auteur` : XLM-RoBERTa bénéficie du préentraînement multilingue pour reconnaître les formes latines")
lines.append("- `ouvrage` reste le label le plus difficile pour les deux systèmes (titres latins très variables)")
lines.append("- BiLSTM-CRF présente une perte négative à partir de l'epoch 27 → signe de surapprentissage (overfitting)")
lines.append("- XLM-RoBERTa converge plus vite (20 epochs vs 50) et de manière plus stable")

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"\n[Done] Rapport Markdown → {OUT_PATH}")
