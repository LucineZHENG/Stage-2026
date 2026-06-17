# Rapport Run 1 v3

**Modèle** : `magistermilitum/roberta-multilingual-medieval-ner`  
**Date** : 2026-06-07 21:13  
**Données** : `test_run1.json` (10 entrées)

## Métriques

| Stratégie | F1_pers_all | P | R | F1_auteur_excl | P | R | F1_ouvrage_pers | P | R |
|---|---|---|---|---|---|---|---|---|---|
| simple | 0.4762 | 0.4545 | 0.5000 | 0.6250 | 0.8333 | 0.5000 | 0.3333 | 0.3333 | 0.3333 |
| first | 0.4762 | 0.4545 | 0.5000 | 0.6250 | 0.8333 | 0.5000 | 0.3333 | 0.3333 | 0.3333 |
| max | 0.4211 | 0.4444 | 0.4000 | 0.5333 | 0.8000 | 0.4000 | 0.3333 | 0.3333 | 0.3333 |

## Analyse des erreurs (stratégie simple)

| Type | N | entry_ids |
|---|---|---|
| Correct (rien attendu) | 2 | #297, #1512 |
| Faux négatif | 3 | #1298, #276, #235 |
| Faux positif | 1 | #333 |
| Erreur de frontière | 4 | #338, #351, #286, #1232 |

## Détails par entrée (stratégie simple)

**#1298** `1298 da Cascia Fra Simone, volgarizzamento ed Esposizione dei Vangeli. Cod. cart...`
- pred PERS (all)      : []
- pred auteur (excl)   : []
- pred ouvr. pers      : []
- gold auteur          : ['da Cascia Fra Simone']
- gold ouvr. pers      : []

**#276** `276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec...`
- pred PERS (all)      : []
- pred auteur (excl)   : []
- pred ouvr. pers      : []
- gold auteur          : ['Hieronymi', 'Origenis']
- gold ouvr. pers      : []

**#297** `297 Martyrologium. Cod. membran. in quarto Saec. XIII....`
- pred PERS (all)      : []
- pred auteur (excl)   : []
- pred ouvr. pers      : []
- gold auteur          : []
- gold ouvr. pers      : []

**#333** `333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. ...`
- pred PERS (all)      : ['Ioannis', 'Gu', 'al', 'ber', 'Bernard']
- pred auteur (excl)   : []
- pred ouvr. pers      : ['Ioannis', 'Gu', 'al', 'ber', 'Bernard']
- gold auteur          : []
- gold ouvr. pers      : ['Ioannis Gualberti', 'Bernardi']

**#338** `338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV....`
- pred PERS (all)      : ['Leonis Urbe']
- pred auteur (excl)   : ['Leonis Urbe']
- pred ouvr. pers      : []
- gold auteur          : ['Leonis Urbevetani']
- gold ouvr. pers      : []

**#351** `351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Fici...`
- pred PERS (all)      : ['Basil', 'Mar', 'silii Fi']
- pred auteur (excl)   : ['Basil', 'Mar', 'silii Fi']
- pred ouvr. pers      : []
- gold auteur          : ['Basilii', 'Marsilii Ficini']
- gold ouvr. pers      : []

**#1512** `1512 Meditazioni sacre. Cod. membran. in 16. Sec. XV....`
- pred PERS (all)      : []
- pred auteur (excl)   : []
- pred ouvr. pers      : []
- gold auteur          : []
- gold ouvr. pers      : []

**#235** `235 Origenes, super vetus Testamentum. Cod. membr. in fol. Saec. XV in fine muti...`
- pred PERS (all)      : []
- pred auteur (excl)   : []
- pred ouvr. pers      : []
- gold auteur          : ['Origenes']
- gold ouvr. pers      : []

**#286** `286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Agg...`
- pred PERS (all)      : ['E', 'phra', 'Ch', 'rys', 'os']
- pred auteur (excl)   : ['E', 'phra', 'Ch', 'rys', 'os']
- pred ouvr. pers      : []
- gold auteur          : ['S. Ephraem', 'Chrysostomi']
- gold ouvr. pers      : []

**#1232** `1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggi...`
- pred PERS (all)      : ['Boc', 'cacci', 'Antoni', 'Tommaso Spinelli']
- pred auteur (excl)   : ['Boc', 'cacci']
- pred ouvr. pers      : []
- gold auteur          : ['Boccaccii']
- gold ouvr. pers      : ['Donatum Apenninigenam']

