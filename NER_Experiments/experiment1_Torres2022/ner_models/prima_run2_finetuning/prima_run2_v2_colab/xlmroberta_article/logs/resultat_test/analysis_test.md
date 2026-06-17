# Rapport d'analyse — XLM-RoBERTa (TEST)

**Paramètres** : epochs=5, lr=2e-05, batch=16, max_len=250  
**Référence** : Torres Aguilar (2022), LREC LT4HALA  
**Date** : 2026-06-07 22:13

---

## Matrice de résultats (seqeval — entité stricte)

```
Label                  P        R       F1   Support
----------------------------------------------------
auteur             0.000    0.000    0.000        10
ouvrage            0.000    0.000    0.000        11
material           0.125    0.273    0.171        11
date               0.000    0.000    0.000        10
etat               0.000    0.000    0.000         4
----------------------------------------------------
micro avg          0.041    0.065    0.050        46
macro avg          0.025    0.055    0.034        46
weighted avg       0.030    0.065    0.041        46
```

- **F1** = 0.0500  **P** = 0.0405  **R** = 0.0652

---

## Exemples détaillés par type d'erreur

### ❌ Faux négatif — entité non détectée (10 entrées)

**#1298** `1298 da Cascia Fra Simone, volgarizzamento ed Esposizione dei Vangeli. Cod. cart. fol. Sec`
- Gold : auteur(Cascia Fra Simone, volgarizzamento ed Esposizione), ouvrage(Sec. XV sul princ.)
- Préd : —

**#276** `276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec. XII in f`
- Gold : auteur(translatio de Tractatu), ouvrage(Origenis in Epithalamicis. Cod. membr. Saec.), auteur(XII in fol.), ouvrage(in fine mutilus, sed eleganter scriptus,), material(ac bene servatus.)
- Préd : —

**#297** `297 Martyrologium. Cod. membran. in quarto Saec. XIII.`
- Gold : ouvrage(Cod. membran. in quarto Saec.), material(XIII.)
- Préd : —

**#333** `333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. X`
- Gold : ouvrage(S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV.)
- Préd : —

**#338** `338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV.`
- Gold : auteur(Urbevetani chronicon et alia. Cod. membr.), ouvrage(Saec XIV.)
- Préd : —

**#351** `351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quat`
- Gold : auteur(Sancti, oratio ad), ouvrage(huma nioribus studii, et Marsilii Ficini), auteur(Saec. XV.)
- Préd : —

**#1512** `1512 Meditazioni sacre. Cod. membran. in 16. Sec. XV.`
- Gold : ouvrage(sacre. Cod. membran. in 16. Sec.), material(XV.)
- Préd : —

**#235** `235 Origenes, super vetus Testamentum. Cod. membr. in fol. Saec. XV in fine mutilus.`
- Gold : auteur(Origenes, super vetus), ouvrage(Testamentum. Cod. membr. in fol. Saec.), material(XV in fine mutilus.)
- Préd : —

**#286** `286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mut`
- Gold : auteur(Ephraem, et Chrysostomi opera quaedam. Cod.), auteur(in quarto Saec. XV), ouvrage(Aggiunte: mutilus in), material(principio)
- Préd : —

**#1232** `1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232`
- Gold : auteur(Eclogae ad Donatum Apenninigenam.), ouvrage(Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa), material(a Tommaso Spinelli. In cornice.)
- Préd : —

