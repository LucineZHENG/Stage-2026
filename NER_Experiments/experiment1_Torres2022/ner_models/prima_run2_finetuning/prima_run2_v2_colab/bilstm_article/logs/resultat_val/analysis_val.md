# Rapport d'analyse — BiLSTM-CRF (VAL)

**Paramètres** : epochs=5, lr=0.01, batch=16, embed=64, hidden=128  
**Référence** : Torres Aguilar (2022), LREC LT4HALA  
**Date** : 2026-06-07 22:13

---

## Matrice de résultats (seqeval — entité stricte)

```
Label                  P        R       F1   Support
----------------------------------------------------
auteur             0.333    0.176    0.231        17
ouvrage            0.143    0.130    0.136        23
material           0.857    0.857    0.857        21
date               0.900    0.900    0.900        20
etat               0.750    0.500    0.600         6
----------------------------------------------------
micro avg          0.600    0.517    0.556        87
macro avg          0.597    0.513    0.545        87
weighted avg       0.568    0.517    0.536        87
```

- **F1** = 0.5556  **P** = 0.6000  **R** = 0.5172

---

## Exemples détaillés par type d'erreur

### ✅ Correct — correspondance exacte (1 entrées)

**#432** `432 Officium B. M. Virginis. Cod. membr. in octavo Saec. XVI cum picturis.`
- Gold : ouvrage(Officium B. M. Virginis.), material(Cod. membr. in octavo), date(Saec. XVI)
- Préd : ouvrage(Officium B. M. Virginis.), material(Cod. membr. in octavo), date(Saec. XVI)

### 〰️ Erreur partielle — détection incomplète ou mauvais label (19 entrées)

**#224** `224 Lectionarium secundum anni circulum. Cod. membr. in fol max Saec. XI.`
- Gold : ouvrage(Lectionarium secundum anni circulum.), material(Cod. membr. in fol max), date(Saec. XI.)
- Préd : material(Cod. membr. in fol), date(Saec. XI.)

**#1554** `1554 T. Livio, la prima Deca volgarizzata. Cod. cart. in fol. Sec XIV.`
- Gold : auteur(T. Livio,), ouvrage(la prima Deca volgarizzata.), material(Cod. cart. in fol.), date(Sec XIV.)
- Préd : material(Cod. cart. in fol.), date(Sec XIV.)

**#448** `448 ex Firmiano Lactantio Excerpta, ec. Cod. chartac. Saec. XVII in octavo.`
- Gold : auteur(Firmiano Lactantio), ouvrage(Excerpta,), material(Cod. chartac.), date(Saec. XVII), material(in octavo.)
- Préd : material(Cod. chartac.), date(Saec. XVII), etat(in octavo.)

**#1507** `1507 1508 S. Antonino, Trattato de’ peccati mortali, de’ Sacramenti, delle virtù, e de’ 10`
- Gold : auteur(S. Antonino,), ouvrage(Trattato de’ peccati mortali,), material(Cod. cartac.), date(Secolo XV.)
- Préd : auteur(S.), material(Cod. cartac.)

**#1360** `1360 Gregorio S. Morali parte 3. Cod. cart. in fol. Sec. XV.`
- Gold : auteur(Gregorio S.), ouvrage(Morali parte 3.), material(Cod. cart. in fol.), date(Sec. XV.)
- Préd : auteur(S. Morali parte 3.), material(Cod. cart. in fol.), date(Sec. XV.)

**#321** `321 S. Augustini chronici epitome. Cod. Membranac in quarto Saec XIV in fine mutilus`
- Gold : auteur(S. Augustini), ouvrage(chronici epitome.), material(Cod. Membranac in quarto), date(Saec XIV), etat(in fine mutilus)
- Préd : auteur(S. Augustini chronici epitome.), material(Cod. Membranac in quarto), date(Saec XIV), etat(in fine mutilus)

**#509** `509 Ciceronis Questiones Tusculanae. Demosthenis Philppica octava, et alia. Cod. chartac. `
- Gold : auteur(Ciceronis), ouvrage(Questiones Tusculanae.), auteur(Demosthenis), ouvrage(Philppica octava,), material(Cod. chartac. in fol.), date(Saec. XV), etat(initio mutilus.)
- Préd : auteur(Ciceronis), auteur(Questiones), material(Cod. chartac. in fol.), date(Saec. XV), etat(initio mutilus.)

**#1270** `1270 Trattati morali e rettorici; e volgarizzamento dell’Eneide di Virgilio. Cod. cart. in`
- Gold : ouvrage(Trattati morali e rettorici;), ouvrage(volgarizzamento dell’Eneide), auteur(Virgilio.), material(Cod. cart. in fol.), date(Sec. XIV.)
- Préd : material(Cod. cart. in fol.), date(Sec. XIV.)

**#1071** `1071 Boccaccio, Ninfale ecc. Cod. cart. in fol. Sec. XV.`
- Gold : auteur(Boccaccio,), ouvrage(Ninfale), material(Cod. cart. in fol.), date(Sec. XV.)
- Préd : material(Cod. cart. in fol.), date(Sec. XV.)

**#470** `470 S. Bonaventurae Dialogus. Cod. chartac in 16. Saec. XV.`
- Gold : auteur(S. Bonaventurae), ouvrage(Dialogus.), material(Cod. chartac in 16.), date(Saec. XV.)
- Préd : auteur(S. Bonaventurae Dialogus.), material(Cod. chartac in 16.), date(Saec. XV.)

**#334** `334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV.`
- Gold : auteur(Iustiniani Leonardi,), ouvrage(vita S. Nicolai.), material(Cod membr. in 8), date(Saec. XV.)
- Préd : auteur(S. Nicolai.), material(Cod membr. in 8), date(Saec. XV.)

**#332** `332 Conciones quadragesimales incerti Auctoris. Cod. membr. in 8. Saec. XIV initio et medi`
- Gold : ouvrage(Conciones quadragesimales), material(Cod. membr. in 8.), date(Saec. XIV), etat(initio et medio mutilus.)
- Préd : material(Cod. membr. in 8.), date(Saec. XIV), etat(initio et medio mutilus.)

**#1350** `1350 Gradi di S. Girolamo. Cod. cartac. in fol. Sec. XIV sul fine, manc. in fine.`
- Gold : ouvrage(Gradi di S. Girolamo.), material(Cod. cartac. in fol.), date(Sec. XIV), etat(manc. in fine.)
- Préd : auteur(S. Girolamo.), material(Cod. cartac. in fol.), date(Sec. XIV)

**#1618** `1618 Boezio, volgarizzato da M. Alberto. Cod. cart. in quarto Sec. XV. mancante di una pag`
- Gold : ouvrage(Boezio, volgarizzato), auteur(M. Alberto.), material(Cod. cart. in quarto), date(Sec. XV.), etat(mancante di una pagina in principio.)
- Préd : material(Cod. cart. in quarto), date(Sec. XV.)

**#236** `236 Petri Comestoris Historia Ecclesiastica. Cod.membr. in fol. Saec. XIII.`
- Gold : auteur(Petri Comestoris), ouvrage(Historia Ecclesiastica.), material(Cod.membr. in fol.), date(Saec. XIII.)
- Préd : material(Cod.membr. in fol.), date(Saec. XIII.)

**#434** `434 Evangelia. Accedunt Collationes abb. Isaaci et alia. Cod. membr. in octavo Saec. XIV.`
- Gold : ouvrage(Evangelia.), ouvrage(Collationes), auteur(Isaaci), material(Cod. membr. in octavo), date(Saec. XIV.)
- Préd : material(Cod. membr. in octavo), date(Saec. XIV.)

**#1036** `1036 Dante la Divina commedia &c. Cod. cart. in fol. Secolo XIV sul fine, lacero nella pri`
- Gold : auteur(Dante), ouvrage(la Divina commedia), material(Cod. cart. in fol.), date(Secolo XIV), etat(lacero nella prima carta.)
- Préd : material(Cod. cart. in fol.)

**#257** `257 Synodus Dioecesan. Gasparis Pasquali Episcopi Rubensis. Cod. chartac. autogr. in fol. `
- Gold : ouvrage(Synodus Dioecesan.), auteur(Gasparis Pasquali), material(Cod. chartac. autogr. in fol.), date(Saec. XVI)
- Préd : material(Cod. chartac. autogr. in fol.), date(Saec. XVI)

**#503** `503 Ciceronis Epistolae ad familiares Cod partim membr. partim chartac. Saec. XV.`
- Gold : auteur(Ciceronis), ouvrage(Epistolae ad familiares), material(Cod partim membr. partim chartac.), date(Saec. XV.)
- Préd : auteur(Ciceronis), date(Saec. XV.)

