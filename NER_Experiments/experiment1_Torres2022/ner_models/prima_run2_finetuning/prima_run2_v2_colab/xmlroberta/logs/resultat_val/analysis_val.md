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

