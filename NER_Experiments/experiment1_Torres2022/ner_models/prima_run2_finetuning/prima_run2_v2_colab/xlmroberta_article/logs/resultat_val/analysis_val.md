# Rapport d'analyse — XLM-RoBERTa (VAL)

**Paramètres** : epochs=5, lr=2e-05, batch=16, max_len=250  
**Référence** : Torres Aguilar (2022), LREC LT4HALA  
**Date** : 2026-06-07 22:13

---

## Matrice de résultats (seqeval — entité stricte)

```
Label                  P        R       F1   Support
----------------------------------------------------
auteur             0.000    0.000    0.000        17
ouvrage            0.019    0.043    0.026        23
material           0.085    0.190    0.118        21
date               0.000    0.000    0.000        20
etat               0.000    0.000    0.000         6
----------------------------------------------------
micro avg          0.040    0.057    0.047        87
macro avg          0.021    0.047    0.029        87
weighted avg       0.025    0.057    0.035        87
```

- **F1** = 0.0474  **P** = 0.0403  **R** = 0.0575

---

## Exemples détaillés par type d'erreur

### ❌ Faux négatif — entité non détectée (19 entrées)

**#224** `224 Lectionarium secundum anni circulum. Cod. membr. in fol max Saec. XI.`
- Gold : ouvrage(Lectionarium secundum anni circulum. Cod. membr. in fol), material(max Saec. XI.)
- Préd : —

**#1554** `1554 T. Livio, la prima Deca volgarizzata. Cod. cart. in fol. Sec XIV.`
- Gold : auteur(Livio, la prima Deca volgarizzata.), ouvrage(Cod. cart. in fol. Sec XIV.)
- Préd : —

**#448** `448 ex Firmiano Lactantio Excerpta, ec. Cod. chartac. Saec. XVII in octavo.`
- Gold : auteur(Lactantio Excerpta, ec. Cod. chartac. Saec.), ouvrage(XVII in octavo.)
- Préd : —

**#1507** `1507 1508 S. Antonino, Trattato de’ peccati mortali, de’ Sacramenti, delle virtù, e de’ 10`
- Gold : auteur(Trattato de’ peccati mortali, de’), ouvrage(Sacramenti, delle virtù, e de’ 10 comandamenti di Dio. Cod.)
- Préd : —

**#432** `432 Officium B. M. Virginis. Cod. membr. in octavo Saec. XVI cum picturis.`
- Gold : ouvrage(B. M. Virginis. Cod. membr. in octavo Saec. XVI cum), material(picturis.)
- Préd : —

**#1360** `1360 Gregorio S. Morali parte 3. Cod. cart. in fol. Sec. XV.`
- Gold : auteur(S. Morali parte 3.), ouvrage(Cod. cart. in fol.), material(Sec. XV.)
- Préd : —

**#321** `321 S. Augustini chronici epitome. Cod. Membranac in quarto Saec XIV in fine mutilus`
- Gold : auteur(Augustini chronici epitome. Cod.), ouvrage(Membranac in quarto Saec XIV in), material(fine mutilus)
- Préd : —

**#509** `509 Ciceronis Questiones Tusculanae. Demosthenis Philppica octava, et alia. Cod. chartac. `
- Gold : auteur(Questiones Tusculanae.), ouvrage(Demosthenis Philppica octava, et alia. Cod. chartac.), auteur(in fol. Saec. XV), ouvrage(initio mutilus.)
- Préd : —

**#1270** `1270 Trattati morali e rettorici; e volgarizzamento dell’Eneide di Virgilio. Cod. cart. in`
- Gold : ouvrage(morali e rettorici; e volgarizzamento dell’Eneide di Virgilio. Cod.), ouvrage(in fol. Sec. XIV.)
- Préd : —

**#1071** `1071 Boccaccio, Ninfale ecc. Cod. cart. in fol. Sec. XV.`
- Gold : auteur(Ninfale ecc. Cod. cart.), ouvrage(in fol. Sec.)
- Préd : —

**#470** `470 S. Bonaventurae Dialogus. Cod. chartac in 16. Saec. XV.`
- Gold : auteur(S. Bonaventurae Dialogus. Cod. chartac in), ouvrage(16. Saec. XV.)
- Préd : —

**#334** `334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV.`
- Gold : auteur(Leonardi, vita S. Nicolai. Cod membr. in), ouvrage(8 Saec. XV.)
- Préd : —

**#332** `332 Conciones quadragesimales incerti Auctoris. Cod. membr. in 8. Saec. XIV initio et medi`
- Gold : ouvrage(quadragesimales incerti Auctoris. Cod. membr. in), material(mutilus.)
- Préd : —

**#1350** `1350 Gradi di S. Girolamo. Cod. cartac. in fol. Sec. XIV sul fine, manc. in fine.`
- Gold : ouvrage(di S. Girolamo. Cod. cartac. in fol. Sec. XIV), material(sul fine, manc. in fine.)
- Préd : —

**#236** `236 Petri Comestoris Historia Ecclesiastica. Cod.membr. in fol. Saec. XIII.`
- Gold : auteur(Comestoris Historia Ecclesiastica. Cod.membr.), ouvrage(in fol. Saec. XIII.)
- Préd : —

**#434** `434 Evangelia. Accedunt Collationes abb. Isaaci et alia. Cod. membr. in octavo Saec. XIV.`
- Gold : ouvrage(Accedunt Collationes abb.), ouvrage(Cod. membr. in)
- Préd : —

**#1036** `1036 Dante la Divina commedia &c. Cod. cart. in fol. Secolo XIV sul fine, lacero nella pri`
- Gold : auteur(la Divina), ouvrage(commedia &c. Cod. cart. in), material(sul fine, lacero nella prima carta.)
- Préd : —

**#257** `257 Synodus Dioecesan. Gasparis Pasquali Episcopi Rubensis. Cod. chartac. autogr. in fol. `
- Gold : ouvrage(Dioecesan. Gasparis Pasquali Episcopi Rubensis. Cod. chartac.), auteur(autogr. in fol. Saec. XVI)
- Préd : —

**#503** `503 Ciceronis Epistolae ad familiares Cod partim membr. partim chartac. Saec. XV.`
- Gold : auteur(Epistolae ad), ouvrage(familiares Cod partim membr.), material(partim chartac. Saec. XV.)
- Préd : —

### 〰️ Erreur partielle — détection incomplète ou mauvais label (1 entrées)

**#1618** `1618 Boezio, volgarizzato da M. Alberto. Cod. cart. in quarto Sec. XV. mancante di una pag`
- Gold : ouvrage(volgarizzato da M. Alberto. Cod. cart. in), auteur(Sec. XV. mancante di), material(una pagina in principio.)
- Préd : material(una pagina in principio.)

