# Experiment 1 — Torres Aguilar (2022)

## I. Contexte

Cette série d'expériences est fondée sur l'article suivant :

> Torres Aguilar, S. (2022). *Multilingual Named Entity Recognition for Medieval Charters Using Stacked Embeddings and BERT-based Models*. In *Proceedings of the LT4HALA Workshop @ LREC 2022*, Marseille.
> - Article : https://aclanthology.org/2022.lt4hala-1.17.pdf
> - Modèle pré-entraîné (HuggingFace) : https://huggingface.co/magistermilitum/roberta-multilingual-medieval-ner/tree/main
> - Code source (GitLab) : https://gitlab.com/magistermilitum/ner_medieval_multilingual/-/tree/main?ref_type=heads

L'article propose deux approches parallèles pour la NER sur des documents médiévaux multilingues : (1) BiLSTM-CRF avec stacked embeddings ; (2) fine-tuning de modèles pré-entraînés multilingues (mBERT, XLM-RoBERTa). Les types d'entités sont PER (noms de personnes) et LOC (noms de lieux), appliqués au corpus HOME-Alcar (latin, ancien français, ancien espagnol). L'auteur a publié le modèle `magistermilitum/roberta-multilingual-medieval-ner` sur HuggingFace.

La question centrale de cette série d'expériences est : **ce modèle et cette méthodologie sont-ils transférables à la tâche NER sur les entrées de catalogues de manuscrits de la Biblioteca Riccardiana ?**

Notre tâche diffère de l'article original : les types d'entités passent de PER/LOC à cinq catégories (auteur, ouvrage, material, date, etat), et le genre textuel est le catalogue de manuscrits (latin/italien) et non la charte diplomatique.

---

## II. Données

### ner_data/gold_100/
100 entrées annotées manuellement (gold standard), issues du catalogue de manuscrits de la Biblioteca Riccardiana. Divisées en train/val/test = 70/20/10 (seed=42) :
- `train.json` (70 entrées)
- `val.json` (20 entrées)
- `test.json` (10 entrées)

Les fichiers `train_run1.json`, `val_run1.json`, `test_run1.json` sont la version spécifique au Run 1 : deux champs ont été ajoutés aux spans ouvrage contenant des noms de personnes (`label_detail` et `contains_persons`), à partir de sources externes (Wikidata, VIAF, Treccani, LoC).

### ner_data/all_938/
Corpus complet obtenu par fusion des 100 entrées gold et des 838 entrées restantes annotées, redivisé selon le même ratio 70/20/10 (seed=42) :
- `train_all.json` (657 entrées)
- `val_all.json` (188 entrées)
- `test_all.json` (93 entrées)

Script de fusion et de division : `merge_and_split_all.py`

---

## III. Structure des fichiers

```
experiment1_Torres2022/
├── ner_data/
│   ├── gold_100/                          ← 100 entrées gold (Run 1, Run 2)
│   │   ├── train.json
│   │   ├── val.json
│   │   ├── test.json
│   │   ├── train_run1.json                ← version Run 1 (contains_persons)
│   │   ├── val_run1.json
│   │   └── test_run1.json
│   └── all_938/                           ← 938 entrées complètes (Run 3)
│       ├── train_all.json
│       ├── val_all.json
│       └── test_all.json
├── ner_models/
│   ├── prima_run1_zero_shot/
│   │   ├── v1_pers_simple/                ← détection PERS de base
│   │   └── v2_pers_refined/               ← subdivision auteur/ouvrage_pers
│   ├── prima_run2_finetuning/
│   │   ├── v1_pagoda_our_params/          ← PAGODA, nos paramètres
│   │   └── v2_colab/                      ← Colab, nos params vs params article
│   └── prima_run3_full_data/
│       ├── prima_run3_v1_xlmroberta_frozen_vs_bilstm_crf/
│       │   ├── xlmroberta_frozen/         ← XLM-RoBERTa entièrement gelé
│       │   └── bilstm_crf/               ← BiLSTM-CRF from scratch
│       └── prima_run3_v2_xlmroberta_partial_vs_bilstm_crf/
│           ├── xlmroberta_partial/        ← XLM-RoBERTa 2 couches dégelées
│           └── bilstm_crf/               ← BiLSTM-CRF from scratch
├── merge_and_split_all.py
└── README.md
```

---

## IV. Analyses des trois expériences

### Run 1 — Évaluation zéro-shot, 100 entrées gold

Données : 100 entrées annotées manuellement (gold standard), jeu de test : 10 entrées (46 spans).
Modèle : **1 modèle, 3 stratégies de décodage**

- `magistermilitum/roberta-multilingual-medieval-ner` : modèle pré-entraîné publié par Torres Aguilar (2022), spécialisé sur des documents latins/italiens médiévaux, utilisé **directement sans aucun fine-tuning**.
- Les 3 stratégies (simple/first/max) correspondent à différentes méthodes d'alignement subword→word, et non à 3 modèles distincts.
- Seule l'entité auteur est évaluée (le modèle produit des étiquettes PERS, alignées sur le gold auteur) ; les autres entités n'ont pas d'étiquette correspondante.
- Meilleur F1 = 0,476 (stratégies simple et first à égalité).

---

### Run 2 — Comparaison de fine-tuning, 100 entrées gold

Données : mêmes 100 entrées gold standard, divisées en train/val/test = 70/20/10.
Modèle : **4 systèmes**, comparés deux à deux.

- **XLM-RoBERTa (nos paramètres)** : epochs=20, batch=8, lr=2e-5, max_len=128. Fine-tuning complet de tous les paramètres (278M). F1=0,72, **meilleur résultat du Run 2**.
- **XLM-RoBERTa (paramètres article)** : paramètres de Torres Aguilar (2022), epochs=5, batch=16, lr=2e-5, max_len=250. Nombre d'epochs insuffisant, échec complet, F1=0,05.
- **BiLSTM-CRF (nos paramètres)** : epochs=50, batch=8, lr=0,001, entraîné depuis zéro. F1=0,60.
- **BiLSTM-CRF (paramètres article)** : epochs=5, batch=16, lr=0,01. F1=0,52.

L'objectif principal du Run 2 est la **recherche d'hyperparamètres** : nos paramètres ajustés surpassent les paramètres originaux de l'article sur notre jeu de données.

---

### Run 3 — Évaluation formelle sur données complètes, 938 entrées

Données : 100 entrées gold + 838 entrées restantes annotées = 938 entrées, divisées en train/val/test = 657/188/93 (70/20/10, seed=42). Évaluation sur 5 entités : auteur, ouvrage, material, date, etat.
Modèle : **3 systèmes**, regroupés en deux notebooks de comparaison.

**`prima_run3_v1_xlmroberta_frozen_vs_bilstm_crf`**
- **XLM-RoBERTa Tentative 1 (encodeur entièrement gelé)** : encodeur complètement gelé, seule la tête de classification est entraînée (Linear 768→11, 8 459 paramètres). epochs=10, lr=5e-4. Expérience de diagnostic visant à vérifier la viabilité du gel complet. Résultat : F1=0,072, **échec**.
- **BiLSTM-CRF from scratch** : entraîné depuis zéro, sans connaissance pré-entraînée, embeddings initialisés aléatoirement. epochs=30, lr=0,001, split fixe 657/188/93. Test F1=0,634.

**`prima_run3_v2_xlmroberta_partial_vs_bilstm_crf`**
- **XLM-RoBERTa Tentative 2 (2 dernières couches dégelées)** : dégel des 2 dernières couches (~14M paramètres, 5,1 %), le reste gelé. epochs=15, lr=2e-5, validation croisée 5-fold (845 entrées pour la CV + 93 entrées test isolées). CV F1=0,517 ± 0,023, test F1=0,498.
- **BiLSTM-CRF from scratch** : mêmes paramètres que ci-dessus. Test F1=0,634, **meilleur résultat du Run 3**, supérieur à la Tentative 2 sur toutes les entités.

**Tendance générale**

La progression Run 1 → Run 2 → Run 3 ne se mesure pas à une hausse monotone du F1 (les jeux de test étant de tailles différentes, les chiffres ne sont pas directement comparables), mais à trois avancées successives : confirmer que le transfert direct est insuffisant (Run 1) → identifier les hyperparamètres optimaux (Run 2) → obtenir une évaluation fiable sur données complètes (Run 3).
