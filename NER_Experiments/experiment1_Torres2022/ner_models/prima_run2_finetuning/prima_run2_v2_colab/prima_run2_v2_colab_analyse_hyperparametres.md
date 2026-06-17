# Expérience 2 — Analyse de la capacité de transfert des hyperparamètres

## Objectif

Utiliser les paramètres de l'article (Torres Aguilar 2022) comme référence afin d'observer leur capacité de transfert sur notre jeu de données et d'identifier une plage de paramètres adaptée à notre tâche.

---

## 1. XLM-RoBERTa

### Paramètres comparés

| Configuration | epochs | batch size | lr | max_len |
|---|---|---|---|---|
| Nos paramètres | 20 | 8 | 2e-5 | 128 |
| Paramètres article | 5 | 16 | 2e-5 | 250 |

### Courbe d'apprentissage

| Epoch | XLM-R nos param. (val F1) | XLM-R article (val F1) |
|---|---|---|
| 1 | 0.0000 | 0.0000 |
| 2 | 0.0157 | 0.0000 |
| 3 | 0.2538 | 0.0183 |
| 4 | 0.4271 | 0.0282 |
| 5 | 0.5000 | 0.0474 |
| 6 | 0.6020 | — |
| 7 | 0.6596 | — |
| 8 | 0.6813 | — |
| 9 | 0.7473 | — |
| 10 | 0.7514 | — |
| 11 | 0.7778 | — |
| 12 | 0.7821 | — |
| 16 | **0.8068** | — |
| 19–20 | **0.8156** | — |

### Observations

Le modèle XLM-R avec nos paramètres converge progressivement : il ne produit aucune prédiction utile avant l'epoch 3, puis monte régulièrement pour atteindre un val F1 de **0.82** à l'epoch 16–20. La convergence est lente mais stable, ce qui est cohérent avec un jeu de données de petite taille (70 entrées d'entraînement).

Avec les paramètres de l'article (epochs=5), le modèle atteint seulement un val F1 de **0.05** à l'epoch 5 — la loss diminue (2.22 → 1.55) mais reste bien au-dessus du seuil de convergence. Le modèle n'a tout simplement pas le temps d'apprendre : à l'epoch 5, XLM-R avec nos paramètres n'en est qu'à F1=0.50, soit encore à mi-chemin de sa performance finale.

**Conclusion XLM-R** : 5 epochs est insuffisant pour notre jeu de données. La plage adaptée se situe entre **15 et 20 epochs**, avec un batch size de 8 (plus adapté à la taille du corpus que batch=16 qui réduit le nombre de mises à jour par epoch). Le max_len=128 est suffisant pour nos entrées de catalogue.

---

## 2. BiLSTM-CRF

### Paramètres comparés

| Configuration | epochs | batch size | lr |
|---|---|---|---|
| Nos paramètres | 50 | 8 | 0.001 |
| Paramètres article | 5 | 16 | 0.01 |

### Courbe d'apprentissage

| Epoch | BiLSTM nos param. (val F1) | BiLSTM article (val F1) |
|---|---|---|
| 1 | 0.2367 | 0.4173 |
| 2 | 0.1061 | 0.4070 |
| 3 | 0.1746 | 0.4405 |
| 4 | 0.3453 | 0.4375 |
| 5 | 0.4490 | **0.5556** |
| 10 | 0.5161 | — |
| 13 | 0.5419 | — |
| 32 | 0.5513 | — |
| 41 | 0.5535 | — |
| 46 | **0.5714** | — |
| 49 | 0.5732 | — |
| 50 | 0.5786 | — |

### Observations

Le comportement des deux configurations BiLSTM est inverse de celui observé pour XLM-R. Avec lr=0.01 et batch=16 (paramètres article), le modèle converge très rapidement : dès l'epoch 1, il atteint F1=0.42, et arrive à **0.56** en seulement 5 epochs. En comparaison, nos paramètres (lr=0.001) n'atteignent F1=0.45 qu'à l'epoch 5.

Cependant, avec 50 epochs, nos paramètres finissent par dépasser les paramètres article (**0.58 vs 0.56**), tout en présentant une loss qui devient négative à partir de l'epoch 27 — signe que la CRF loss non normalisée diverge et que le modèle commence à surajuster.

**Conclusion BiLSTM** : Le lr=0.01 de l'article est mieux adapté pour une convergence rapide sur notre corpus. En revanche, 5 epochs reste insuffisant pour exploiter pleinement le modèle. Une plage de **10 à 15 epochs avec lr=0.01** permettrait de combiner la vitesse de convergence des paramètres article et la stabilité d'un entraînement plus long. La loss négative observée avec lr=0.001 sur 50 epochs indique un problème de normalisation à corriger.

---

## 3. Synthèse

| Modèle | Param. article (5 ep.) | Nos param. | Plage recommandée |
|---|---|---|---|
| XLM-R | val F1 = 0.05 ❌ | val F1 = 0.82 ✅ | epochs ∈ [15, 20], batch=8, max_len=128 |
| BiLSTM | val F1 = 0.56 ✅ | val F1 = 0.58 ✅ | epochs ∈ [10, 15], lr=0.01, batch=16 |

Les paramètres de l'article ont été conçus pour un corpus plus large où XLM-R peut converger rapidement. Sur notre jeu de 100 entrées, la convergence est naturellement plus lente et nécessite davantage d'epochs. En revanche, le lr et le batch size de l'article pour BiLSTM se transfèrent bien, car ce modèle est moins sensible à la taille du corpus pour sa phase d'initialisation.

Ces observations orientent les choix pour les expériences suivantes : favoriser un entraînement plus long pour XLM-R, et adopter lr=0.01 pour BiLSTM tout en ajustant le nombre d'epochs à la hausse par rapport à l'article.
