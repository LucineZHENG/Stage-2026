# Rapport d'analyse — BiLSTM-CRF (TEST)

**Paramètres** : epochs=5, lr=0.01, batch=16, embed=64, hidden=128  
**Référence** : Torres Aguilar (2022), LREC LT4HALA  
**Date** : 2026-06-07 22:13

---

## Matrice de résultats (seqeval — entité stricte)

```
Label                  P        R       F1   Support
----------------------------------------------------
auteur             0.200    0.100    0.133        10
ouvrage            0.083    0.091    0.087        11
material           0.900    0.818    0.857        11
date               1.000    1.000    1.000        10
etat               1.000    0.250    0.400         4
----------------------------------------------------
micro avg          0.579    0.478    0.524        46
macro avg          0.637    0.452    0.495        46
weighted avg       0.583    0.478    0.507        46
```

- **F1** = 0.5238  **P** = 0.5789  **R** = 0.4783

---

## Exemples détaillés par type d'erreur

### 〰️ Erreur partielle — détection incomplète ou mauvais label (10 entrées)

**#1298** `1298 da Cascia Fra Simone, volgarizzamento ed Esposizione dei Vangeli. Cod. cart. fol. Sec`
- Gold : auteur(da Cascia Fra Simone,), ouvrage(Esposizione dei Vangeli.), material(Cod. cart. fol.), date(Sec. XV)
- Préd : material(Cod. cart. fol.), date(Sec. XV)

**#276** `276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec. XII in f`
- Gold : auteur(Hieronymi), ouvrage(translatio de Tractatu), auteur(Origenis), ouvrage(in Epithalamicis.), material(Cod. membr.), date(Saec. XII), material(in fol.), etat(in fine mutilus,), etat(bene servatus.)
- Préd : auteur(Hieronymi), auteur(translatio), ouvrage(de Tractatu Origenis in Epithalamicis.), material(Cod. membr.), date(Saec. XII)

**#297** `297 Martyrologium. Cod. membran. in quarto Saec. XIII.`
- Gold : ouvrage(Martyrologium.), material(Cod. membran. in quarto), date(Saec. XIII.)
- Préd : material(Cod. membran. in quarto), date(Saec. XIII.)

**#333** `333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. X`
- Gold : ouvrage(Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum.), material(Cod. membr. in. 8.), date(Saec. XV.)
- Préd : auteur(S.), auteur(S. Bernardi et aliorum.), material(Cod. membr. in. 8.), date(Saec. XV.)

**#338** `338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV.`
- Gold : auteur(Leonis Urbevetani), ouvrage(chronicon et alia.), material(Cod. membr.), date(Saec XIV.)
- Préd : material(Cod. membr.), date(Saec XIV.)

**#351** `351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quat`
- Gold : auteur(Basilii,), ouvrage(oratio ad juvenes), auteur(Marsilii Ficini), material(Cod. chart. in quarto), date(Saec. XV.)
- Préd : material(Cod. chart. in quarto), date(Saec. XV.)

**#1512** `1512 Meditazioni sacre. Cod. membran. in 16. Sec. XV.`
- Gold : ouvrage(Meditazioni sacre.), material(Cod. membran. in 16.), date(Sec. XV.)
- Préd : material(Cod. membran. in), date(Sec. XV.)

**#235** `235 Origenes, super vetus Testamentum. Cod. membr. in fol. Saec. XV in fine mutilus.`
- Gold : auteur(Origenes,), ouvrage(super vetus Testamentum.), material(Cod. membr. in fol.), date(Saec. XV), etat(in fine mutilus.)
- Préd : material(Cod. membr. in fol.), date(Saec. XV), etat(in fine mutilus.)

**#286** `286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mut`
- Gold : auteur(S. Ephraem,), auteur(Chrysostomi), ouvrage(opera quaedam.), material(Cod. chart. in quarto), date(Saec. XV), etat(mutilus in principio)
- Préd : auteur(S.), material(Cod. chart. in quarto), date(Saec. XV)

**#1232** `1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232`
- Gold : auteur(Boccaccii), ouvrage(Eclogae ad Donatum Apenninigenam.), material(Cod. mem. in 8.), date(Saec. XIV.)
- Préd : material(Cod. mem. in 8.), date(Saec. XIV.)

