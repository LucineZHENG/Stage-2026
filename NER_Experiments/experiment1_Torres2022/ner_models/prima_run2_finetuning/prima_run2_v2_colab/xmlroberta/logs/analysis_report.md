# Rapport d'analyse — XLM-RoBERTa (nos paramètres)

**Paramètres** : epochs=20, lr=2e-05, batch=8, max_len=128  
**Date** : 2026-06-07 22:34

---

# Rapport d'analyse — XLM-RoBERTa (VAL)

**Paramètres** : epochs=20, lr=2e-05, batch=8, max_len=128  
**Date** : 2026-06-07 22:34

---

## Matrice de résultats (seqeval — entité stricte)

```
Label                  P        R       F1   Support
----------------------------------------------------
auteur             0.812    0.765    0.788        17
ouvrage            0.552    0.696    0.615        23
material           0.952    0.952    0.952        21
date               1.000    1.000    1.000        20
etat               0.667    0.667    0.667         6
----------------------------------------------------
micro avg          0.793    0.839    0.816        87
macro avg          0.797    0.816    0.804        87
weighted avg       0.810    0.839    0.822        87
```

- **F1** = 0.8156  **P** = 0.7935  **R** = 0.8391

---

## Exemples détaillés par type d'erreur

### ✅ Correct — correspondance exacte (10 entrées)

**#224** `224 Lectionarium secundum anni circulum. Cod. membr. in fol max Saec. XI.`
- Gold : ouvrage(Lectionarium secundum anni circulum. Cod. membr. in fol), material(max Saec. XI.)
- Préd : ouvrage(Lectionarium secundum anni circulum. Cod. membr. in fol), material(max Saec. XI.)

**#1554** `1554 T. Livio, la prima Deca volgarizzata. Cod. cart. in fol. Sec XIV.`
- Gold : auteur(Livio, la prima Deca volgarizzata.), ouvrage(Cod. cart. in fol. Sec XIV.)
- Préd : auteur(Livio, la prima Deca volgarizzata.), ouvrage(Cod. cart. in fol. Sec XIV.)

**#432** `432 Officium B. M. Virginis. Cod. membr. in octavo Saec. XVI cum picturis.`
- Gold : ouvrage(B. M. Virginis. Cod. membr. in octavo Saec. XVI cum), material(picturis.)
- Préd : ouvrage(B. M. Virginis. Cod. membr. in octavo Saec. XVI cum), material(picturis.)

**#321** `321 S. Augustini chronici epitome. Cod. Membranac in quarto Saec XIV in fine mutilus`
- Gold : auteur(Augustini chronici epitome. Cod.), ouvrage(Membranac in quarto Saec XIV in), material(fine mutilus)
- Préd : auteur(Augustini chronici epitome. Cod.), ouvrage(Membranac in quarto Saec XIV in), material(fine mutilus)

**#470** `470 S. Bonaventurae Dialogus. Cod. chartac in 16. Saec. XV.`
- Gold : auteur(S. Bonaventurae Dialogus. Cod. chartac in), ouvrage(16. Saec. XV.)
- Préd : auteur(S. Bonaventurae Dialogus. Cod. chartac in), ouvrage(16. Saec. XV.)

**#334** `334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV.`
- Gold : auteur(Leonardi, vita S. Nicolai. Cod membr. in), ouvrage(8 Saec. XV.)
- Préd : auteur(Leonardi, vita S. Nicolai. Cod membr. in), ouvrage(8 Saec. XV.)

**#1350** `1350 Gradi di S. Girolamo. Cod. cartac. in fol. Sec. XIV sul fine, manc. in fine.`
- Gold : ouvrage(di S. Girolamo. Cod. cartac. in fol. Sec. XIV), material(sul fine, manc. in fine.)
- Préd : ouvrage(di S. Girolamo. Cod. cartac. in fol. Sec. XIV), material(sul fine, manc. in fine.)

**#236** `236 Petri Comestoris Historia Ecclesiastica. Cod.membr. in fol. Saec. XIII.`
- Gold : auteur(Comestoris Historia Ecclesiastica. Cod.membr.), ouvrage(in fol. Saec. XIII.)
- Préd : auteur(Comestoris Historia Ecclesiastica. Cod.membr.), ouvrage(in fol. Saec. XIII.)

**#1036** `1036 Dante la Divina commedia &c. Cod. cart. in fol. Secolo XIV sul fine, lacero nella pri`
- Gold : auteur(la Divina), ouvrage(commedia &c. Cod. cart. in), material(sul fine, lacero nella prima carta.)
- Préd : auteur(la Divina), ouvrage(commedia &c. Cod. cart. in), material(sul fine, lacero nella prima carta.)

**#503** `503 Ciceronis Epistolae ad familiares Cod partim membr. partim chartac. Saec. XV.`
- Gold : auteur(Epistolae ad), ouvrage(familiares Cod partim membr.), material(partim chartac. Saec. XV.)
- Préd : auteur(Epistolae ad), ouvrage(familiares Cod partim membr.), material(partim chartac. Saec. XV.)

### 〰️ Erreur partielle — détection incomplète ou mauvais label (10 entrées)

**#448** `448 ex Firmiano Lactantio Excerpta, ec. Cod. chartac. Saec. XVII in octavo.`
- Gold : auteur(Lactantio Excerpta, ec. Cod. chartac. Saec.), ouvrage(XVII in octavo.)
- Préd : ouvrage(XVII in octavo.)

**#1507** `1507 1508 S. Antonino, Trattato de’ peccati mortali, de’ Sacramenti, delle virtù, e de’ 10`
- Gold : auteur(Trattato de’ peccati mortali, de’), ouvrage(Sacramenti, delle virtù, e de’ 10 comandamenti di Dio. Cod.)
- Préd : auteur(Trattato de’ peccati mortali, de’), ouvrage(Sacramenti, delle virtù, e), ouvrage(Secolo XV.)

**#1360** `1360 Gregorio S. Morali parte 3. Cod. cart. in fol. Sec. XV.`
- Gold : auteur(S. Morali parte 3.), ouvrage(Cod. cart. in fol.), material(Sec. XV.)
- Préd : auteur(S. Morali parte 3. Cod. cart.), material(Sec. XV.)

**#509** `509 Ciceronis Questiones Tusculanae. Demosthenis Philppica octava, et alia. Cod. chartac. `
- Gold : auteur(Questiones Tusculanae.), ouvrage(Demosthenis Philppica octava, et alia. Cod. chartac.), auteur(in fol. Saec. XV), ouvrage(initio mutilus.)
- Préd : auteur(Questiones Tusculanae.), ouvrage(Demosthenis Philppica octava, et alia. Cod. chartac.), ouvrage(in fol. Saec. XV), ouvrage(initio mutilus.)

**#1270** `1270 Trattati morali e rettorici; e volgarizzamento dell’Eneide di Virgilio. Cod. cart. in`
- Gold : ouvrage(morali e rettorici; e volgarizzamento dell’Eneide di Virgilio. Cod.), ouvrage(in fol. Sec. XIV.)
- Préd : ouvrage(morali e rettorici; e volgarizzamento dell’Eneide di Virgilio. Cod.)

**#1071** `1071 Boccaccio, Ninfale ecc. Cod. cart. in fol. Sec. XV.`
- Gold : auteur(Ninfale ecc. Cod. cart.), ouvrage(in fol. Sec.)
- Préd : auteur(Ninfale ecc. Cod. cart.), ouvrage(in fol. Sec. XV.)

**#332** `332 Conciones quadragesimales incerti Auctoris. Cod. membr. in 8. Saec. XIV initio et medi`
- Gold : ouvrage(quadragesimales incerti Auctoris. Cod. membr. in), material(mutilus.)
- Préd : ouvrage(quadragesimales incerti Auctoris. Cod. membr. in), ouvrage(XIV initio et medio), material(mutilus.)

**#1618** `1618 Boezio, volgarizzato da M. Alberto. Cod. cart. in quarto Sec. XV. mancante di una pag`
- Gold : ouvrage(volgarizzato da M. Alberto. Cod. cart. in), auteur(Sec. XV. mancante di), material(una pagina in principio.)
- Préd : auteur(volgarizzato da M. Alberto.), ouvrage(Cod. cart. in quarto Sec. XV. mancante di), material(una pagina in principio.)

**#434** `434 Evangelia. Accedunt Collationes abb. Isaaci et alia. Cod. membr. in octavo Saec. XIV.`
- Gold : ouvrage(Accedunt Collationes abb.), ouvrage(Cod. membr. in)
- Préd : ouvrage(Accedunt Collationes abb.), ouvrage(Isaaci et alia. Cod. membr. in octavo Saec. XIV.)

**#257** `257 Synodus Dioecesan. Gasparis Pasquali Episcopi Rubensis. Cod. chartac. autogr. in fol. `
- Gold : ouvrage(Dioecesan. Gasparis Pasquali Episcopi Rubensis. Cod. chartac.), auteur(autogr. in fol. Saec. XVI)
- Préd : ouvrage(Dioecesan. Gasparis Pasquali Episcopi Rubensis. Cod. chartac.), auteur(autogr. in fol. Saec. XVI et alia.)


---

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


