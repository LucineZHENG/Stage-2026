# Rapport d'analyse — XLM-RoBERTa (TEST)

**Paramètres** : epochs=20, lr=2e-05, batch=8, max_len=128  
**Date** : 2026-06-07 22:34

---

## Matrice de résultats (seqeval — entité stricte)

```
Label                  P        R       F1   Support
----------------------------------------------------
auteur             0.533    0.800    0.640        10
ouvrage            0.385    0.455    0.417        11
material           0.917    1.000    0.957        11
date               1.000    1.000    1.000        10
etat               0.500    0.500    0.500         4
----------------------------------------------------
micro avg          0.667    0.783    0.720        46
macro avg          0.667    0.751    0.703        46
weighted avg       0.688    0.783    0.728        46
```

- **F1** = 0.7200  **P** = 0.6667  **R** = 0.7826

---

## Exemples détaillés par type d'erreur

### ✅ Correct — correspondance exacte (5 entrées)

**#297** `297 Martyrologium. Cod. membran. in quarto Saec. XIII.`
- Gold : ouvrage(Cod. membran. in quarto Saec.), material(XIII.)
- Préd : ouvrage(Cod. membran. in quarto Saec.), material(XIII.)

**#338** `338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV.`
- Gold : auteur(Urbevetani chronicon et alia. Cod. membr.), ouvrage(Saec XIV.)
- Préd : auteur(Urbevetani chronicon et alia. Cod. membr.), ouvrage(Saec XIV.)

**#1512** `1512 Meditazioni sacre. Cod. membran. in 16. Sec. XV.`
- Gold : ouvrage(sacre. Cod. membran. in 16. Sec.), material(XV.)
- Préd : ouvrage(sacre. Cod. membran. in 16. Sec.), material(XV.)

**#235** `235 Origenes, super vetus Testamentum. Cod. membr. in fol. Saec. XV in fine mutilus.`
- Gold : auteur(Origenes, super vetus), ouvrage(Testamentum. Cod. membr. in fol. Saec.), material(XV in fine mutilus.)
- Préd : auteur(Origenes, super vetus), ouvrage(Testamentum. Cod. membr. in fol. Saec.), material(XV in fine mutilus.)

**#286** `286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mut`
- Gold : auteur(Ephraem, et Chrysostomi opera quaedam. Cod.), auteur(in quarto Saec. XV), ouvrage(Aggiunte: mutilus in), material(principio)
- Préd : auteur(Ephraem, et Chrysostomi opera quaedam. Cod.), auteur(in quarto Saec. XV), ouvrage(Aggiunte: mutilus in), material(principio)

### 〰️ Erreur partielle — détection incomplète ou mauvais label (5 entrées)

**#1298** `1298 da Cascia Fra Simone, volgarizzamento ed Esposizione dei Vangeli. Cod. cart. fol. Sec`
- Gold : auteur(Cascia Fra Simone, volgarizzamento ed Esposizione), ouvrage(Sec. XV sul princ.)
- Préd : auteur(Fra Simone, volgarizzamento ed Esposizione), ouvrage(dei Vangeli. Cod. cart. fol. Sec. XV sul princ.)

**#276** `276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec. XII in f`
- Gold : auteur(translatio de Tractatu), ouvrage(Origenis in Epithalamicis. Cod. membr. Saec.), auteur(XII in fol.), ouvrage(in fine mutilus, sed eleganter scriptus,), material(ac bene servatus.)
- Préd : auteur(translatio de Tractatu), material(ac bene servatus.)

**#333** `333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. X`
- Gold : ouvrage(S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV.)
- Préd : ouvrage(S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod.), auteur(Saec. XV.)

**#351** `351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quat`
- Gold : auteur(Sancti, oratio ad), ouvrage(huma nioribus studii, et Marsilii Ficini), auteur(Saec. XV.)
- Préd : auteur(Sancti, oratio ad), ouvrage(huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod.), auteur(Saec. XV.)

**#1232** `1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232`
- Gold : auteur(Eclogae ad Donatum Apenninigenam.), ouvrage(Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa), material(a Tommaso Spinelli. In cornice.)
- Préd : auteur(Eclogae ad Donatum Apenninigenam.), ouvrage(Cod.), material(a Tommaso Spinelli. In cornice.)

