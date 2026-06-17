# PRIMA NER — Comparaison BiLSTM-CRF vs XLM-RoBERTa

Généré le : 2026-05-18 03:13:46

Données : 100 entrées annotées (train=70, val=20, test=10), seed=42

## Résultats globaux

| Système | Val F1 | Test F1 | Test Precision | Test Recall |
|---|---|---|---|---|
| BiLSTM-CRF | 0.5786 | 0.5952 | 0.6579 | 0.5435 |
| XLM-RoBERTa | 0.8000 | 0.7071 | 0.6604 | 0.7609 |

## Résultats par label (test set)

| Label | BiLSTM P | BiLSTM R | BiLSTM F1 | XLMR P | XLMR R | XLMR F1 | Meilleur |
|---|---|---|---|---|---|---|---|
| auteur | 0.333 | 0.100 | 0.154 | 0.540 | 0.700 | 0.610 | XLM-RoBERTa |
| ouvrage | 0.300 | 0.273 | 0.286 | 0.310 | 0.360 | 0.330 | XLM-RoBERTa |
| material | 0.909 | 0.909 | 0.909 | 0.920 | 1.000 | 0.960 | XLM-RoBERTa |
| date | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | égalité |
| etat | 0.250 | 0.250 | 0.250 | 0.600 | 0.750 | 0.670 | XLM-RoBERTa |

## Hyperparamètres

| Paramètre | BiLSTM-CRF | XLM-RoBERTa |
|---|---|---|
| Modèle de base | From scratch | xlm-roberta-base |
| Epochs | 50 | 20 |
| Learning rate | 0.001 | 2e-05 |
| Batch size | 8 | 8 |
| Vocab size | 509 | N/A (SentencePiece) |
| Embed dim | 64 | 768 (fixe) |
| Hidden dim | 128 | N/A |
| Temps entraînement | 0.45 min | 2.1 min |

## Analyse

- XLM-RoBERTa surpasse BiLSTM-CRF sur tous les labels sauf `date` (égalité à 1.00)
- Le gain le plus important est sur `auteur` : XLM-RoBERTa bénéficie du préentraînement multilingue pour reconnaître les formes latines
- `ouvrage` reste le label le plus difficile pour les deux systèmes (titres latins très variables)
- BiLSTM-CRF présente une perte négative à partir de l'epoch 27 → signe de surapprentissage (overfitting)
- XLM-RoBERTa converge plus vite (20 epochs vs 50) et de manière plus stable
