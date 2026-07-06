# Synthèse Run 1 – Run 3
## NER sur les catalogues de manuscrits de la Biblioteca Riccardiana
### Projet PRIMA · `experiment1_Torres2022`

> Document de synthèse consolidant les trois runs d'expérimentation NER, avec (1) présentation des modèles, (2) tableaux de résultats issus des fichiers `*_results.json` / `test_results.json`, et (3) exemples de prédictions extraits des `details` de ces mêmes fichiers.
> Toutes les valeurs proviennent directement des logs du dépôt `NER_Experiments/experiment1_Torres2022/ner_models/`.

---

## 0. Contexte commun

Les trois runs testent la transférabilité du modèle et de la méthodologie de **Torres Aguilar (2022)** (`magistermilitum/roberta-multilingual-medieval-ner`, corpus HOME-Alcar, entités PER/LOC) vers notre tâche : cinq entités **auteur, ouvrage, material, date, etat** sur des entrées de catalogues de manuscrits (latin/italien).

| Run | But | Données | Jeu de test | Entités évaluées |
|---|---|---|---|---|
| **Run 1** | Transfert direct suffisant ? | 100 gold | 10 entrées | `auteur` seul (PERS→auteur) |
| **Run 2** | Quels hyperparamètres ? | 100 gold (70/20/10) | 10 entrées · 46 spans | 5 entités |
| **Run 3** | Évaluation fiable sur tout le corpus | 938 (657/188/93) | 93 entrées · 396 spans | 5 entités |

> ⚠️ Les F1 des trois runs **ne sont pas directement comparables** : les jeux de test diffèrent en taille (10 → 10 → 93 entrées) et en périmètre (1 entité → 5 entités). La progression se lit qualitativement : *confirmer l'insuffisance du transfert direct (Run 1) → fixer les hyperparamètres (Run 2) → obtenir une évaluation robuste (Run 3)*.

---

## 1. RUN 1 — Évaluation zéro-shot

### 1.1 Modèle
- **`magistermilitum/roberta-multilingual-medieval-ner`** (Torres Aguilar 2022), utilisé **directement, sans aucun fine-tuning**.
- Un seul modèle, **3 stratégies d'alignement** subword→word (`simple`, `first`, `max`) — ce ne sont **pas** 3 modèles distincts.
- Le modèle ne produit que des étiquettes **PERS** ; seule l'entité `auteur` du gold est donc évaluable (alignement PERS→auteur). Les autres entités n'ont pas de correspondance.

### 1.2 Résultats (test = 10 entrées, support auteur = 10)

| Stratégie | Precision | Recall | F1 |
|---|---|---|---|
| **simple** ★ | 0.455 | 0.500 | **0.476** |
| **first** ★ | 0.455 | 0.500 | **0.476** |
| max | 0.444 | 0.400 | 0.421 |

**Meilleur F1 = 0.476** (`simple` / `first`, à égalité).
*Source : `prima_run1_v2_pers_refined/test_results_strategies.json`, `prima_run1_v1_pers_simple/test_results_run1.json`.*

### 1.3 Exemples de prédictions

| entry_id | Texte (extrait) | gold auteur | pred PERS |
|---|---|---|---|
| 338 | *Leonis Urbevetani chronicon…* | `Leonis Urbevetani` | `Leonis Urbe` — **partiel** |
| 1298 | *da Cascia Fra Simone, volgarizzamento…* | `da Cascia Fra Simone` | `[]` — **manqué** |
| 286 | *S. Ephraem, et Chrysostomi opera…* | `S. Ephraem`, `Chrysostomi` | fragments subword (`E`,`phra`,…) |

### 1.4 Conclusion Run 1
Le transfert direct est **insuffisant** : le modèle segmente mal (fragments de sous-mots), ne connaît pas nos frontières d'entités, et ne couvre qu'une entité sur cinq. → Nécessité d'un ré-entraînement sur nos données (Run 2).

---

## 2. RUN 2 — Recherche d'hyperparamètres (fine-tuning)

### 2.1 Modèles — **4 systèmes**, comparés deux à deux

| Système | Type | Paramètres entraînés | Config |
|---|---|---|---|
| **XLM-R (nos params)** | **Fine-tuning complet** | **278 M (tous)** | ep=20, batch=8, lr=2e-5, max_len=128 |
| XLM-R (params article) | Fine-tuning complet | 278 M (tous) | ep=5, batch=16, lr=2e-5, max_len=250 |
| **BiLSTM-CRF (nos params)** | *from scratch* | ~toutes (aléatoire) | ep=50, batch=8, lr=1e-3 |
| BiLSTM-CRF (params article) | *from scratch* | ~toutes (aléatoire) | ep=5, batch=16, lr=1e-2 |

> **Fine-tuning ?** Les deux XLM-R du Run 2 sont en **fine-tuning complet** (tous les poids de l'encodeur sont mis à jour). Les BiLSTM-CRF sont entraînés *from scratch* (pas de poids pré-entraînés → ce n'est pas du fine-tuning au sens transfer learning). Voir §5.

### 2.2 Résultats — jeu de test (10 entrées, 46 spans)

| Système | Precision | Recall | **F1** |
|---|---|---|---|
| **XLM-R — nos params** ★ | 0.667 | 0.783 | **0.72** |
| BiLSTM-CRF — nos params | 0.658 | 0.543 | 0.595 |
| BiLSTM-CRF — params article | 0.579 | 0.478 | 0.524 |
| XLM-R — params article | 0.041 | 0.065 | 0.050 |

*Source : `prima_run2_v2_colab/{xmlroberta,bilstm_our_params,bilstm_article,xlmroberta_article}/logs/resultat_test/results_test.json`.*
*Réplication PAGODA du meilleur système (XLM-R nos params) : test F1 = 0.707 — `prima_run2_v1_pagoda_our_params/xlm_roberta/logs/test_results.json`.*

### 2.3 XLM-R (nos params) — détail par entité (val, support plus large)

| Entité | P | R | F1 | support |
|---|---|---|---|---|
| date | 1.00 | 1.00 | 1.00 | 20 |
| material | 0.95 | 0.95 | 0.95 | 21 |
| auteur | 0.81 | 0.76 | 0.79 | 17 |
| etat | 0.67 | 0.67 | 0.67 | 6 |
| ouvrage | 0.55 | 0.70 | 0.62 | 23 |
| **micro avg (val)** | 0.79 | 0.84 | **0.816** | 87 |

### 2.4 Exemple de prédiction (XLM-R nos params, entry 235 — parfait)
```
raw : 235 Origenes, super vetus Testamentum. Cod. membr. in fol. Saec. XV in fine mutilus.
gold: [Origenes,](auteur) [super vetus Testamentum. Cod. membr. in fol. Saec.](ouvrage) [XV in fine mutilus.](material)
pred: [Origenes,](auteur) [super vetus Testamentum. Cod. membr. in fol. Saec.](ouvrage) [XV in fine mutilus.](material)  ✓
```

### 2.5 Conclusion Run 2
Nos hyperparamètres ajustés **surpassent** ceux de l'article : XLM-R passe de 0.05 (5 epochs) à **0.72** (20 epochs). Le fine-tuning complet reste le meilleur choix **à cette échelle (100 entrées)**.

---

## 3. RUN 3 — Évaluation formelle sur données complètes (938 entrées)

Consigne de l'encadrant : **ne pas fine-tuner directement** XLM-R, mais l'utiliser comme **extracteur de features** avec une tête de classification ; entraîner le **BiLSTM-CRF from scratch** ; utiliser **toutes les données**.

### 3.1 v1 — Encodeur gelé vs BiLSTM-CRF

| Système | Stratégie | Params entraînables | Config | **Test F1** |
|---|---|---|---|---|
| XLM-R **frozen** | encodeur **100 % gelé** + tête `Linear(768→11)` | **8 459** | ep=10, lr=5e-4 | **0.072** ❌ |
| **BiLSTM-CRF** | *from scratch* | emb=100, hid=256 | ep=30, lr=1e-3 | **0.634** ★ |

*Source : `prima_run3_v1_.../xlmroberta_frozen/logs/test_results.json`, `.../bilstm_crf/logs/test_results.json`.*

L'encodeur gelé échoue (8 459 paramètres = une seule couche linéaire ne peut pas adapter des représentations génériques à la NER ; seul `date` est partiellement appris grâce aux marqueurs `Saec./Sec.`).

### 3.2 v2 — Dégel partiel (2 dernières couches) vs BiLSTM-CRF

| Système | Stratégie | Params entraînables | Protocole | Résultat |
|---|---|---|---|---|
| XLM-R **partial unfreeze** | couches 10–11 dégelées + tête | ~14,18 M (5,1 %) | 5-fold CV sur 845 + test 93 **isolé** | CV F1 = **0.517 ± 0.023** · **Test F1 = 0.498** |
| **BiLSTM-CRF** | *from scratch* (identique v1) | emb=100, hid=256 | split fixe 657/188/93 | **Test F1 = 0.634** ★ |

*Source : `.../xlmroberta_partial_unfreeze/logs/cv_summary.json` + `test_final_results.json` ; `.../bilstm_crf/logs/test_results.json`.*

> **⚠️ Correction de protocole (data leakage).** Une première version de v2 incluait `test_all.json` dans la validation croisée 5-fold, ce qui gonflait le score (CV F1 = 0.530 ± 0.019). Après correction (test strictement isolé), **CV F1 = 0.517 ± 0.023** et **test F1 = 0.498**. Le `cv_summary.json` du dépôt reflète la version **corrigée**.

### 3.3 ★ Comparaison ciblée — Tentative 2 (partial unfreeze) vs BiLSTM-CRF, par entité
*(jeu de test, 93 entrées, 396 spans — chiffres citables)*

| Entité | T2 F1 | BiLSTM F1 | Δ (BiLSTM − T2) |
|---|---|---|---|
| auteur | 0.420 | 0.425 | +0.005 |
| date | 0.847 | 0.917 | +0.070 |
| etat | 0.129 | 0.486 | **+0.357** |
| material | 0.619 | 0.780 | +0.161 |
| ouvrage | 0.315 | 0.427 | +0.112 |
| **micro avg** | **0.498** | **0.635** | **+0.137** |

Détail des precision/recall :

| Entité | T2 P | T2 R | BiLSTM P | BiLSTM R |
|---|---|---|---|---|
| auteur | 0.347 | 0.532 | 0.562 | 0.342 |
| date | 0.798 | 0.902 | 0.933 | 0.902 |
| etat | 0.100 | 0.182 | 0.600 | 0.409 |
| material | 0.575 | 0.670 | 0.780 | 0.780 |
| ouvrage | 0.256 | 0.411 | 0.435 | 0.420 |
| **micro** | **0.428** | **0.596** | **0.675** | **0.598** |

**Lecture.**
- Le **BiLSTM-CRF surpasse T2 sur toutes les entités**. Écart le plus fort sur **etat** (+0.357) : la couche CRF, qui modélise explicitement les transitions d'étiquettes, aide fortement cette classe rare.
- Recall quasi identique (0.596 vs 0.598) mais **precision très différente** (0.428 vs 0.675) : **T2 sur-prédit massivement** (beaucoup de faux positifs). Son problème n'est pas d'oublier des entités, mais d'en inventer.

### 3.4 Exemples de prédictions (Tentative 2 — partial unfreeze)

| entry_id | Erreur illustrée |
|---|---|
| 314 | *Constitutiones hospitalis domus Dei Flor. Cod. Membr. Saec. XV in quarto.* → `ouvrage` correct, mais **`quarto.` (material) manqué** |
| 1053 | *Grazia Maestro. Esposizione sopra Dante…* → span `Maestro. Esposizione sopra Dante` prédit **`ouvrage`** au lieu de **`auteur`** (confusion auteur↔ouvrage) |

*Source : `test_final_results.json` → champ `details`.*

### 3.5 Conclusion Run 3
À l'échelle de **938 entrées**, le **BiLSTM-CRF from scratch (F1 = 0.634)** reste supérieur à XLM-R partiellement dégelé (0.498). L'avantage du pré-entraînement ne s'exprime pas pleinement : 938 entrées restent trop peu pour un fine-tuning Transformer efficace, et la couche CRF apporte des contraintes de séquence dont la tête softmax de T2 est dépourvue.

---

## 4. Tableau récapitulatif — meilleur système par run

| Run | Meilleur système | Test F1 | Note d'interprétation |
|---|---|---|---|
| Run 1 | XLM-R medieval (zéro-shot, `simple`) | 0.476 | 1 entité seulement, test = 10 |
| Run 2 | **XLM-R fine-tuning complet (nos params)** | **0.72** | 5 entités, test = 10 (46 spans) |
| Run 3 | **BiLSTM-CRF from scratch** | **0.634** | 5 entités, test = 93 (396 spans) — le plus fiable |

---

## 5. Point de clarification — Qui fait du fine-tuning ? (Run 2 vs Run 3)

| | Run 2 | Run 3 |
|---|---|---|
| **XLM-RoBERTa** | **Fine-tuning COMPLET** — 278 M params, tout l'encodeur mis à jour | **PAS de fine-tuning complet** : v1 = encodeur **entièrement gelé** (8 459 params) ; v2 = **dégel partiel** des 2 dernières couches (~14 M) |
| **BiLSTM-CRF** | *from scratch* (pas de transfert) | *from scratch* (pas de transfert) |

**En clair :**
- **Run 2 = le seul run avec un vrai fine-tuning** (complet) d'XLM-RoBERTa.
- **Run 3 n'utilise volontairement pas le fine-tuning complet** (consigne de l'encadrant) : l'encodeur sert d'extracteur de features (gelé en v1, partiellement dégelé en v2).
- Le BiLSTM-CRF, dans les deux runs, est entraîné **from scratch** — ce n'est jamais du fine-tuning.

### 5.1 Qu'est-ce que le fine-tuning, exactement ?

En résumé : le fine-tuning consiste à prendre un modèle **déjà entraîné** sur une autre tâche/d'autres données, puis à **continuer son entraînement** sur de nouvelles données pour l'adapter à une nouvelle tâche. Le point clé est de **réutiliser les connaissances déjà apprises** lors du pré-entraînement, plutôt que de tout apprendre depuis zéro.

**Les deux conditions du fine-tuning :**
1. Il faut un modèle **pré-entraîné** dont on réutilise les poids (c'est la base du transfer learning).
2. Ces poids doivent être **mis à jour** (au moins en partie) sur les nouvelles données.

**Application aux quatre configurations testées :**

| Configuration | Poids pré-entraînés ? | Poids mis à jour ? | Est-ce du fine-tuning ? |
|---|---|---|---|
| XLM-R Run 2 | ✅ Oui (pré-entraînement multilingue) | ✅ Les 278 M de paramètres sont tous mis à jour | ✅ **Oui** — c'est un fine-tuning **complet** |
| XLM-R Run 3 v1 (gelé) | ✅ Oui | ❌ L'encodeur est entièrement figé ; seule la petite tête de classification ajoutée (8 459 paramètres) est entraînée | ❌ **Non** — le modèle pré-entraîné est simplement utilisé comme extracteur de features |
| XLM-R Run 3 v2 (dégel partiel) | ✅ Oui | ⚠️ Seules les 2 dernières couches sont mises à jour (~5 % des paramètres), le reste reste gelé | 🔶 **Cas intermédiaire** — un fine-tuning léger/partiel, mais qui n'atteint pas le fine-tuning complet du Run 2 |
| BiLSTM-CRF (Run 2 et Run 3) | ❌ Non, initialisation aléatoire | ✅ Tous les paramètres sont appris | ❌ **Non** — c'est un entraînement *from scratch*, une notion différente du fine-tuning |

**En une phrase :** le fine-tuning consiste à s'appuyer sur les connaissances déjà acquises par un modèle pré-entraîné, puis à les ajuster pour la tâche visée. Geler tous les poids et n'entraîner qu'une petite tête revient à faire de l'**extraction de features**, pas du fine-tuning ; ne dégeler qu'une partie des couches est un fine-tuning **partiel** ; et entraîner un modèle sans aucun poids pré-existant (comme le BiLSTM-CRF) est un entraînement *from scratch*, une catégorie à part entière.

---

## 6. Traçabilité — fichiers de logs par prédiction *(pour la demande « fournir les preuves des prédictions »)*

Chaque système possède : un **journal d'entraînement** (`training_log.jsonl`, F1/loss par epoch) **et** un fichier de résultats (`test_results.json` / `results.json`) dont le champ **`details` / `test_details` contient `raw` + `gold_spans` + `pred_spans`** — c'est la preuve directe de chaque prédiction.

| Run / système | Journal | Résultats + prédictions |
|---|---|---|
| Run 1 · simple | `prima_run1_v1_pers_simple/output.log` | `test_results_run1.json`, `bio_sequences_run1.txt` |
| Run 1 · simple/first/max | `prima_run1_v2_pers_refined/output.log` | `test_results_strategies.json`, `bio_sequences_{simple,first,max}.txt` |
| Run 2 · XLM-R nos params | `.../xmlroberta/logs/training_log.jsonl` | `.../resultat_test/results_test.json` |
| Run 2 · XLM-R article | `.../xlmroberta_article/logs/training_log.jsonl` | `.../resultat_test/results_test.json` |
| Run 2 · BiLSTM nos params | `.../bilstm_our_params/logs/training_log.jsonl` | `.../resultat_test/results_test.json` |
| Run 2 · BiLSTM article | `.../bilstm_article/logs/training_log.jsonl` | `.../resultat_test/results_test.json` |
| Run 3 v1 · XLM-R frozen | `.../xlmroberta_frozen/logs/training_log.jsonl` | `.../logs/test_results.json` |
| Run 3 v1/v2 · BiLSTM | `.../bilstm_crf/logs/training_log.jsonl` | `.../logs/test_results.json` |
| Run 3 v2 · XLM-R partial | `.../xlmroberta_partial_unfreeze/logs/fold_{1..5}/training_log.jsonl` | `fold_{1..5}/results.json`, `cv_summary.json`, `test_final_results.json` |

> **Seul Run 1** dispose de fichiers `bio_sequences_*.txt` (alignement BIO token par token). Si le même niveau de détail BIO est requis pour Run 2 / Run 3, il faudra le régénérer à partir des `details` (les données sont présentes, seul l'export BIO manque).

---

## 7. Pistes « données trop faibles » → modifier les données

Deux points ressortent des logs pour cibler des ajouts d'annotation :

1. **`etat` — talon d'Achille.** Seulement **22 spans** en test (204 au total sur 938). T2 s'effondre (F1 = 0.13) ; même le BiLSTM plafonne à 0.49. → priorité : **plus d'exemples `etat`** ou rééquilibrage (class weights / oversampling).
2. **`ouvrage` — difficulté intrinsèque, pas un manque de données.** C'est l'entité la **mieux dotée** (112 spans en test, 1114 au total) et pourtant F1 ≈ 0.32–0.43 : frontières floues, confusion fréquente avec `auteur`. → ajouter des données aidera peu ; il faut surtout **clarifier la règle d'annotation auteur ↔ ouvrage** (cf. exemple 1053).
3. **`auteur`** — recall correct mais precision faible (sur-prédiction). Cohérence des frontières (titres honorifiques `S.`, `Fra`, génitifs latins) à resserrer dans le guide d'annotation.
