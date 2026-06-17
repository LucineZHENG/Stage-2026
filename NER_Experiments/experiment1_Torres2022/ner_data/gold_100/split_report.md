# Rapport de division des données — PRIMA NER

Seed : 42 | Total : 100 entrées | Train : 70 / Val : 20 / Test : 10

Source : `gold_annotations_with_el.json`


---

## TRAIN — 70 entrées

### Distribution des labels

| Label | Nb spans | % |
|---|---|---|
| auteur | 51 | 17.9% |
| ouvrage | 74 | 26.0% |
| material | 73 | 25.6% |
| date | 70 | 24.6% |
| etat | 17 | 6.0% |
| **Total** | **285** | 100% |

### Caractéristiques

- Longueur moyenne des entrées : **14.9 tokens** (min 9, max 68)
- Spans par entrée (moyenne) : **4.1**
- Entrées avec `auteur` : **41**
- Entrées avec `ouvrage` : **70**
- Entrées avec `etat` : **17**

### Siècles des manuscrits

| Siècle | Nb entrées |
|---|---|
| 1000–1099 | 2 |
| 1200–1299 | 4 |
| 1300–1399 | 10 |
| 1400–1499 | 42 |
| 1500–1599 | 6 |
| 1600–1699 | 3 |
| 1700–1799 | 2 |

### Fichiers sources

| Fichier | Nb entrées |
|---|---|
| Catalogo_III_Riccardiana_421-520.json | 19 |
| Catalogo_II_Riccardiana_321-420.json | 19 |
| Catalogo_IV_Riccardiana_1002-1700.json | 14 |
| Catalogo_I_Riccardiana_221-320.json | 18 |

### Entry IDs (70)

`225, 233, 239, 247, 249, 250, 251, 253, 275, 291, 293, 299, 304, 305, 309, 310, 312, 318, 327, 335, 342, 343, 350, 356, 359, 367, 368, 369, 372, 379, 382, 383, 394, 401, 406, 413, 417, 426, 430, 431, 442, 446, 451, 456, 457, 459, 468, 469, 471, 481, 494, 497, 504, 510, 516, 519, 1061, 1174, 1183, 1231, 1240, 1251, 1296, 1349, 1421, 1439, 1444, 1592, 1630, 1675`

### Détail des entrées

| entry_id | Texte brut | Labels |
|---|---|---|
| 225 | 225 Passionarium Sanctorum. Cod. Membran in fol. Atlantico. Saec. XI nitidissime… | ouvrage(Passionarium Sanctor), material(Cod. Membran in fol.), date(Saec. XI), etat(nitidissime scriptus) |
| 233 | 233 S. Augustini de Civitate Dei. Cod. membr. in fol. maximo venustissimus, cum … | auteur(S. Augustini), ouvrage(de Civitate Dei), material(Cod. membr. in fol. ), date(Saec. XV in), etat(elegantissimis) |
| 239 | 239 Vetus et Novum Testamentum latinis ver sibus redirum a Petro de Riga. Cod. m… | auteur(Petro de Riga), ouvrage(Vetus et Novum Testa), material(Cod. membr. in fol.), date(Saec. XIII), etat(in fine mutilus) |
| 247 | 247 Sidonii Apollinaris Epistolae. Cod. chart. in fol. Saec. XV. | auteur(Sidonii Apollinaris), ouvrage(Epistolae), material(Cod. chart. in fol.), date(Saec. XV) |
| 249 | 249 Ferrarii Gregorii Commentaria in Apocalypsim. Cod. chart. Saec. XVII in fol. | auteur(Ferrarii Gregorii), ouvrage(Commentaria in Apoca), material(Cod. chart), material(n fol.), date(Saec. XVII) |
| 250 | 250 Hieremiae Compendium Moralium. Cod. chart. in fol. Saec. XV. | auteur(Hieremiae), ouvrage(Compendium Moralium), material(Cod. chart. in fol.), date(Saec. XV) |
| 251 | 251 Sermones Sacri. Cod. chart. in fol. Saec. XV initio et fine mutilus. | ouvrage(Sermones Sacri), material(Cod. chart. in fol.), date(Saec. XV), etat(initio et fine mutil) |
| 253 | 253 Adalperii Pisauriensis Compendium Theologiae. Cod. membr. in fol. Saec. XV. | auteur(Adalperii Pisauriens), ouvrage(Compendium Theologia), material(Cod. membr. in fol.), date(Saec. XV) |
| 275 | 275 Hieroimus in Matthaeum. Cod. chart. in fol. Saec XV. | auteur(Hieroimus), ouvrage(in Matthaeum), material(Cod. chart. in fol.), date(Saec XV) |
| 291 | 291 Psalterium Davidis. Cod. membran. in fol. Saec. XIII venustissimus. | ouvrage(Psalterium Davidis), material(Cod. membran. in fol), date(Saec. XIII) |
| 293 | 293 S. Matthaei Evangelium, cum glossis marginalibus. Accedit Evang. S. Johannis… | ouvrage(S. Matthaei Evangeli), ouvrage(Evang. S. Johanni), material(Cod. membr. in quart), date(Saec. XIII) |
| 299 | 299 Missale. Cod. membran. in quarto Saec. XV preciosus. | ouvrage(Missale), material(Cod. membran. in qua), date(Saec. XV) |
| 304 | 304 Sermones Sacri Codex chart. in quarto Saec. XIV. | ouvrage(Sermones Sacri), material(Codex chart. in quar), date(Saec. XIV) |
| 305 | 305 S. Cypriani Episcopi Epistolae.Cod. chart. in quarto Saec. XV. | auteur(S. Cypriani), ouvrage(Epistolae.), material(Cod. chart. in quart), date(Saec. XV) |
| 309 | 309 Psalterium et officia Ecclesiastica. Cod. membranac in quarto Saec. XV nonnu… | ouvrage(Psalterium et offici), material(Cod. membranac in qu), date(Saec. XV) |
| 310 | 310 Passionarium SS. Cod. membr. in quarto Saec. XIV. | ouvrage(Passionarium SS), material(Cod. membr. in quart), date(Saec. XIV) |
| 312 | 312 Hieronymi et Rufini opera varia. Cod. chart. in fine mutilus Saec. XV. | auteur(Hieronymi), auteur(Rufini), ouvrage(opera varia), material(Cod. chart.), date(Saec. XV), etat(in fine mutilus) |
| 318 | 318 De conditionibus ad rite sumendam Eucharisti; &c. Cod. chart. in quarto Saec… | ouvrage(De conditionibus ad ), material(Cod. chart. in quart), date(Saec. XVI) |
| 327 | 327 Computus ecclesiasticus &c Cod. membr. in quarto Saec XIV. | ouvrage(Computus ecclesiasti), material(Cod. membr. in quart), date(Saec XIV) |
| 335 | 335 Sentenze et notabili de’ SS. Girolamo, Am brogio, Agostino, Gregorio. Cod. m… | auteur(Girolamo), auteur(Agostino), auteur(Gregorio), ouvrage(Sentenze et notabili), material(Cod. membran), material(in 8), date(Saec. XV) |
| 342 | 342 Bauriae, Fr. Andrene, Defensio Apostolicae potestatis contra Lutherum. Cod. … | auteur(Fr. Andrene), ouvrage(Defensio Apostolicae), material(Cod. chart. in 4), date(Saec. XVI) |
| 343 | 343 Tractatus varii de diversis virtutibus. Cod. chart. in quarto Saec XV. | ouvrage(Tractatus varii de d), material(Cod. chart. in quart), date(Saec XV) |
| 350 | 350 Prosperi, Sancti, de virtute activa et contemplativa. Adcedunt Aesopi fabula… | auteur(Prosperi), auteur(Aesopi), ouvrage(de virtute activa et), ouvrage(Aesopi fabulae), material(Cod. memb. in octavo), date(Saec. XIV) |
| 356 | 356 Ceremoniale Basilicae S. Petri. Cod. chart. in quarto Seac. XVI. | ouvrage(Ceremoniale Basilica), material(Cod. chart. in quart), date(Seac. XVI) |
| 359 | 359 Clementis VII. et Paulli III. Brevia. Cod. membr. in quarto Saec. XVI. | auteur(Clementis VII), auteur(Paulli III), ouvrage(Brevia), material(Cod. membr. in quart), date(Saec. XVI) |
| 367 | 367 Etymologicum nominum hebraicorum quae in. SS. Scripturis occurrunt. Cod. mem… | ouvrage(Etymologicum nominum), material(Cod. membr. in quart), date(Saec. XIV) |
| 368 | 368 Collationes et Sermones Sacri varii. Cod. chart in octavo Saec. XV. | ouvrage(Collationes et Sermo), material(Cod. chart in octavo), date(Saec. XV) |
| 369 | 369 Gregorii, S. Magni, Dialogi. Cod. memb. in octavo Saec. XIV. | auteur(Gregorii), ouvrage(Dialogi), material(Cod. memb. in octavo), date(Saec. XIV) |
| 372 | 372 Breviarium Monasticum ord Vallisumbrosae. Cod. membr. in octavo Saec. XV nit… | ouvrage(Breviarium Monasticu), material(Cod. membr. in octav), date(Saec. XV), etat(nitidissime scriptus) |
| 379 | 379 Bedae dererum natura, et Psalterium; Computus S. Augustini &c. Codex membr. … | auteur(Bedae), auteur(S. Augustini), ouvrage(dererum natura), ouvrage(Psalterium), material(Codex membr. in octa), date(Saec. XI) |
| 382 | 382 Hieronymi Dialogus. Cod. chart. in octavo Saec. XV. | auteur(Hieronymi), ouvrage(Dialogus), material(Cod. chart. in octav), date(Saec. XV) |
| 383 | 383 Joh. Nesii Florent. Oraculum de novo Saeculo. Cod. membr in octavo Saec XV. | auteur(Joh. Nesii Florent), ouvrage(Oraculum de novo Sae), material(Cod. membr in octavo), date(Saec XV) |
| 394 | 394 Constitutiones Ecclesiasticae. Cod. chart in fol. Saec XV. | ouvrage(Constitutiones Eccle), material(Cod. chart in fol.), date(Saec XV) |
| 401 | 401 Lamii Ioh. Praelectiones Ecclesiasticae. Cod. char. in fol. Saec. XVIII. Agg… | auteur(Lamii Ioh), ouvrage(Praelectiones Eccles), material(Cod. char. in fol.), date(Saec. XVIII) |
| 406 | 406 Bardis de Roberti, et aliorum Sermones. Cod. chart. in fol Saec. XIV. | auteur(Bardis de Roberti), ouvrage(Sermones), material(Cod. chart. in fol), date(Saec. XIV) |
| 413 | 413 Codex Miscellaneus varios Tractatus continens, Theologico-Morales, et fragme… | ouvrage(varios Tractatus con), material(Cod. chartac. in qua), date(Saec XV) |
| 417 | 417 Landini Christophori Dialogi de Anima. Cod. chartac. in quarto Saec. XV Auto… | auteur(Landini Christophori), ouvrage(Dialogi de Anima), material(Cod. chartac. in qua), date(Saec. XV) |
| 426 | 426 Evangelia, et Epistolae D. Paulli. Cod. Membr. in octavo Saec. XIII. | ouvrage(Evangelia, et Episto), material(Cod. Membr. in octav), date(Saec. XIII) |
| 430 | 430 Fortini de bene moriendo. Cod. membr. in octavo Saec. XV. | auteur(Fortini), ouvrage(de bene moriendo), material(Cod. membr. in octav), date(Saec. XV) |
| 431 | 431 D. Thomae Quaestiones super confessionem. Cod. chartac. in octavo Saec. XV. | auteur(D. Thomae), ouvrage(Quaestiones super co), material(Cod. chartac. in oct), date(Saec. XV) |
| 442 | 442 Cellarii Martini Rombaci, de Iustificatione Peccatoris Opus Haereticum. Cod.… | auteur(Cellarii Martini Rom), ouvrage(de Iustificatione Pe), material(Cod. chartac. in oct), date(Saec. XVI) |
| 446 | 446 a S. Concordio Barptolomaei Summa. Cod. membr. in octavo venustissimus Saec.… | auteur(Barptolomaei), ouvrage(Summa), material(Cod. membr. in octav), date(Saec. XV) |
| 451 | 451 Homiliae super Joh. Evangelistam Cod. chartac. Saec. XVII in octavo. | ouvrage(Homiliae super Joh. ), material(Cod. chartac.), material(in octavo), date(Saec. XVII) |
| 456 | 456 Officium B. M. Virginis, et Mortuorum Cod. membr. in octavo Saec. XV cum pic… | ouvrage(Officium B. M. Virgi), material(Cod. membr. in octav), date(Saec. XV) |
| 457 | 457 Officium B. M. Virginia Cod. membr. in octavo Saec. XV cum picturis. | ouvrage(Officium B. M. Virgi), material(Cod. membr. in octav), date(Saec. XV) |
| 459 | 459 Breviarium Romanum. Cod. membr. in 16, Saec. XV Aggiunte: in fine mutilus | ouvrage(Breviarium Romanum), date(Saec. XV), etat(in fine mutilus), material(Cod. membr. in 16) |
| 468 | 468 Officium B. M. Virginis. Cod. membr. in octavo Saec. XV. | ouvrage(Officium B. M. Virgi), material(Cod. membr. in octav), date(Saec. XV) |
| 469 | 469 Officium B. M. Virginis. Cod. membr. in octavo Saec XV cum picturis. | ouvrage(Officium B. M. Virgi), material(Cod. membr. in octav), date(Saec XV) |
| 471 | 471 Caeremoniale liturgicum. Cod. membr. in octavo Saec. XV mutilus. | ouvrage(Caeremoniale liturgi), material(Cod. membr. in octav), date(Saec. XV), etat(mutilus) |
| 481 | 481 Orationes quaedam, et preces sacrae. Cod. chartac. in 16 Saec. XVIII. | ouvrage(Orationes quaedam, e), material(Cod. chartac. in 16), date(Saec. XVIII) |
| 494 | 494 P. Virgilii Maronis Aeneis. Cod. chartac. in fol. Saec. XV initio mutilus. | auteur(P. Virgilii Maronis), ouvrage(Aeneis), material(Cod. chartac. in fol), date(Saec. XV), etat(initio mutilus) |
| 497 | 497 Ciceronis M. Tullii Orationes. Cod, membr. nitilissimus Saec. XV. | auteur(Ciceronis M. Tullii), ouvrage(Orationes), material(Cod, membr.), date(Saec. XV) |
| 504 | 504 Ciceronis, de Finibus, de Amicitia, de Senecture &c Cod membr. Saec XV nitid… | auteur(Ciceronis), ouvrage(de Finibus, de Amici), material(Cod membr.), date(Saec XV), etat(nitidissimus) |
| 510 | 510 Ciceronis Quaestiones Tusculanae. Cod. chartac. in fol. Saec. XIV. | auteur(Ciceronis), ouvrage(Quaestiones Tusculan), material(Cod. chartac. in fol), date(Saec. XIV) |
| 516 | 516 Ciceronis de Senectute etc. Cod. membr. in fol. Saec. XIV initio et fine mut… | auteur(Ciceronis), ouvrage(de Senectute), material(Cod. membr. in fol.), date(Saec. XIV), etat(initio et fine mutil) |
| 519 | 519 Ciceronis De Inventione. Cod. membr in fol. Saec. XV in: a Francisco de S. M… | auteur(Ciceronis), ouvrage(De Inventione), material(Cod. membr in fol.), date(Saec. XV) |
| 1061 | 1061 Boccaccio Decamerone. Cod. cart. Sec. XV mancante in principio, mezzo e. fi… | auteur(Boccaccio), ouvrage(Decamerone), material(Cod. cart.), date(Sec. XV), etat(mancante in principi) |
| 1174 | 1174 Cermusona Ant. Consilia Medica. Codex chartac. in fol. Saec. XV. | auteur(Cermusona Ant), ouvrage(Consilia Medica), material(Codex chartac. in fo), date(Saec. XV) |
| 1183 | 1183 Capponi March. Vincenzio, Studj diversi. Cod. car. in quarto, ed in fol. Se… | auteur(Capponi March. Vince), ouvrage(Studj diversi), material(Cod. car. in quarto), date(Sec. XVII) |
| 1231 | 1231 Pierii Francisci Orthographia. Cod. chart. in octavo Saec. XV. | auteur(Pierii Francisci), ouvrage(Orthographia), material(Cod. chart. in octav), date(Saec. XV) |
| 1240 | 1240 Ambrosit Camaldulensis, Ciceronis, Poggii, et aliorum Epistolae. Cod. char.… | auteur(Ambrosit Camaldulens), auteur(Ciceronis), auteur(Poggii,), ouvrage(Epistolae), material(Cod. char. in octavo), date(Saec. XVI) |
| 1251 | 1251 Epistole e Vangeli volgarizz. per tutto 1’anno &c. Cod. cart. in fol. Sec. … | ouvrage(Epistole e Vangeli v), material(Cod. cart. in fol.), date(Sec. XV) |
| 1296 | 1296 Vita di S. Gio. Batista. Cod. cartac. fol. Sec. XV. | ouvrage(Vita di S. Gio. Bati), material(Cod. cartac. fol.), date(Sec. XV.) |
| 1349 | 1349 Apocalisse di S. Gio. Pistola di S. Bernardo del governo della famiglia ec.… | auteur(S. Bernardo), ouvrage(Apocalisse di S. Gio), ouvrage(del governo della fa), material(Cod. cart. in fol.), date(Sec. XV), etat(non terminato di scr) |
| 1421 | 1421 S. Gregorio Dialoghi Volgarizzati. Cod. cartac. in quarto Sec. XV non finit… | auteur(S. Gregorio), ouvrage(Dialoghi Volgarizzat), material(Cod. cartac. in quar), date(Sec. XV), etat(non finito di scrive) |
| 1439 | 1439 Cavalca, Specchio de’ Peccati. De dieci Comandamenti, e de’ sette Peccati m… | auteur(Cavalca), ouvrage(Specchio de’ Peccati), material(Cod cartac. in quart), date(Sec. XV), etat(assai guasto) |
| 1444 | 1444 S. Girolamo Regola Latina e Volgare Regola di S. Agostino, e Giovanni Costa… | auteur(S. Girolamo), auteur(S. Agostin), ouvrage(Regola Latina e Volg), material(Cod. cartac. in quar), date(Sec XV), etat(mancante in principi) |
| 1592 | 1592 Astrologia &c. Geta e Birria; così vi si legge in principio. Traductus de l… | auteur(Boccaccium), ouvrage(Geta e Birria), material(Cod. cartac in quart), date(Sec. XV) |
| 1630 | 1630 S. Gregorio, Morali volgarizzati (forse un ristretto) S. Gio. Grisostomo de… | auteur(S. Gregorio), auteur(S. Gio. Grisostomo), ouvrage(Morali volgarizzati), material(Cod. cart. in 4.), date(Sec. XIV) |
| 1675 | 1675 Miracoli della Madonna. Cod. membr. in fol. Sec. XV. mancante in fine. | ouvrage(Miracoli della Madon), material(Cod. membr. in fol.), date(Sec. XV), etat(mancante in fine) |

---

## VAL — 20 entrées

### Distribution des labels

| Label | Nb spans | % |
|---|---|---|
| auteur | 19 | 21.3% |
| ouvrage | 23 | 25.8% |
| material | 21 | 23.6% |
| date | 20 | 22.5% |
| etat | 6 | 6.7% |
| **Total** | **89** | 100% |

### Caractéristiques

- Longueur moyenne des entrées : **14.2 tokens** (min 10, max 23)
- Spans par entrée (moyenne) : **4.5**
- Entrées avec `auteur` : **17**
- Entrées avec `ouvrage` : **20**
- Entrées avec `etat` : **6**

### Siècles des manuscrits

| Siècle | Nb entrées |
|---|---|
| 1000–1099 | 1 |
| 1200–1299 | 1 |
| 1300–1399 | 7 |
| 1400–1499 | 8 |
| 1500–1599 | 2 |
| 1600–1699 | 1 |

### Fichiers sources

| Fichier | Nb entrées |
|---|---|
| Catalogo_III_Riccardiana_421-520.json | 6 |
| Catalogo_II_Riccardiana_321-420.json | 3 |
| Catalogo_IV_Riccardiana_1002-1700.json | 8 |
| Catalogo_I_Riccardiana_221-320.json | 3 |

### Entry IDs (20)

`224, 236, 257, 321, 332, 334, 432, 434, 448, 470, 503, 509, 1036, 1071, 1270, 1350, 1360, 1507, 1554, 1618`

### Détail des entrées

| entry_id | Texte brut | Labels |
|---|---|---|
| 224 | 224 Lectionarium secundum anni circulum. Cod. membr. in fol max Saec. XI. | material(Cod. membr. in fol m), date(Saec. XI), ouvrage(Lectionarium secundu) |
| 236 | 236 Petri Comestoris Historia Ecclesiastica. Cod.membr. in fol. Saec. XIII. | auteur(Petri Comestoris), ouvrage(Historia Ecclesiasti), material(Cod.membr. in fol.), date(Saec. XIII) |
| 257 | 257 Synodus Dioecesan. Gasparis Pasquali Episcopi Rubensis. Cod. chartac. autogr… | auteur(Gasparis Pasquali), ouvrage(Synodus Dioecesan), material(Cod. chartac. autogr), date(Saec. XVI) |
| 321 | 321 S. Augustini chronici epitome. Cod. Membranac in quarto Saec XIV in fine mut… | auteur(S. Augustini), ouvrage(chronici epitome), material(Cod. Membranac in qu), date(Saec XIV), etat(in fine mutilus) |
| 332 | 332 Conciones quadragesimales incerti Auctoris. Cod. membr. in 8. Saec. XIV init… | ouvrage(Conciones quadragesi), material(Cod. membr. in 8.), date(Saec. XIV), etat(initio et medio muti) |
| 334 | 334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV. | auteur(Iustiniani Leonardi), ouvrage(vita S. Nicolai), material(Cod membr. in 8), date(Saec. XV) |
| 432 | 432 Officium B. M. Virginis. Cod. membr. in octavo Saec. XVI cum picturis. | ouvrage(Officium B. M. Virgi), material(Cod. membr. in octav), date(Saec. XVI) |
| 434 | 434 Evangelia. Accedunt Collationes abb. Isaaci et alia. Cod. membr. in octavo S… | auteur(Isaaci), ouvrage(Evangelia), ouvrage(Collationes), material(Cod. membr. in octav), date(Saec. XIV) |
| 448 | 448 ex Firmiano Lactantio Excerpta, ec. Cod. chartac. Saec. XVII in octavo. | auteur(Firmiano Lactantio), ouvrage(Excerpta), material(Cod. chartac.), material(in octavo), date(Saec. XVII) |
| 470 | 470 S. Bonaventurae Dialogus. Cod. chartac in 16. Saec. XV. | auteur(S. Bonaventurae), ouvrage(Dialogus), material(Cod. chartac in 16.), date(Saec. XV) |
| 503 | 503 Ciceronis Epistolae ad familiares Cod partim membr. partim chartac. Saec. XV… | auteur(Ciceronis), ouvrage(Epistolae ad familia), material(Cod partim membr. pa), date(Saec. XV) |
| 509 | 509 Ciceronis Questiones Tusculanae. Demosthenis Philppica octava, et alia. Cod.… | auteur(Ciceronis), auteur(Demosthenis), ouvrage(Questiones Tusculana), ouvrage(Philppica octava), material(Cod. chartac. in fol), date(Saec. XV), etat(initio mutilus) |
| 1036 | 1036 Dante la Divina commedia &c. Cod. cart. in fol. Secolo XIV sul fine, lacero… | auteur(Dante), ouvrage(la Divina commedia), material(Cod. cart. in fol.), date(Secolo XIV), etat(lacero nella prima c) |
| 1071 | 1071 Boccaccio, Ninfale ecc. Cod. cart. in fol. Sec. XV. | auteur(Boccaccio), ouvrage(Ninfale), material(Cod. cart. in fol.), date(Sec. XV) |
| 1270 | 1270 Trattati morali e rettorici; e volgarizzamento dell’Eneide di Virgilio. Cod… | auteur(Virgilio), ouvrage(Trattati morali e re), ouvrage(volgarizzamento dell), material(Cod. cart. in fol.), date(Sec. XIV) |
| 1350 | 1350 Gradi di S. Girolamo. Cod. cartac. in fol. Sec. XIV sul fine, manc. in fine… | auteur(S. Girolamo), ouvrage(Gradi di S. Girolamo), date(Sec. XIV), etat(manc. in fine), material(Cod. cartac. in fol.) |
| 1360 | 1360 Gregorio S. Morali parte 3. Cod. cart. in fol. Sec. XV. | auteur(Gregorio S.), ouvrage(Morali parte 3), material(Cod. cart. in fol.), date(Sec. XV) |
| 1507 | 1507 1508 S. Antonino, Trattato de’ peccati mortali, de’ Sacramenti, delle virtù… | auteur(S. Antonino), ouvrage(Trattato de’ peccati), material(Cod. cartac.), date(Secolo XV) |
| 1554 | 1554 T. Livio, la prima Deca volgarizzata. Cod. cart. in fol. Sec XIV. | auteur(T. Livio), ouvrage(la prima Deca volgar), material(Cod. cart. in fol.), date(Sec XIV) |
| 1618 | 1618 Boezio, volgarizzato da M. Alberto. Cod. cart. in quarto Sec. XV. mancante … | auteur(Boezio), auteur(M. Alberto), ouvrage(Boezio, volgarizzato), material(Cod. cart. in quarto), date(Sec. XV), etat(mancante di una pagi) |

---

## TEST — 10 entrées

### Distribution des labels

| Label | Nb spans | % |
|---|---|---|
| auteur | 10 | 21.7% |
| ouvrage | 11 | 23.9% |
| material | 11 | 23.9% |
| date | 10 | 21.7% |
| etat | 4 | 8.7% |
| **Total** | **46** | 100% |

### Caractéristiques

- Longueur moyenne des entrées : **16.0 tokens** (min 8, max 23)
- Spans par entrée (moyenne) : **4.6**
- Entrées avec `auteur` : **7**
- Entrées avec `ouvrage` : **10**
- Entrées avec `etat` : **3**

### Siècles des manuscrits

| Siècle | Nb entrées |
|---|---|
| 1100–1199 | 1 |
| 1200–1299 | 1 |
| 1300–1399 | 2 |
| 1400–1499 | 6 |

### Fichiers sources

| Fichier | Nb entrées |
|---|---|
| Catalogo_II_Riccardiana_321-420.json | 3 |
| Catalogo_IV_Riccardiana_1002-1700.json | 3 |
| Catalogo_I_Riccardiana_221-320.json | 4 |

### Entry IDs (10)

`235, 276, 286, 297, 333, 338, 351, 1232, 1298, 1512`

### Détail des entrées

| entry_id | Texte brut | Labels |
|---|---|---|
| 235 | 235 Origenes, super vetus Testamentum. Cod. membr. in fol. Saec. XV in fine muti… | auteur(Origenes), ouvrage(super vetus Testamen), material(Cod. membr. in fol.), date(Saec. XV), etat(in fine mutilus) |
| 276 | 276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec… | auteur(Hieronymi), auteur(Origenis), ouvrage(translatio de Tracta), ouvrage(in Epithalamicis), material(Cod. membr.), material(in fol.), date(Saec. XII), etat(in fine mutilus), etat(bene servatus) |
| 286 | 286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Agg… | auteur(S. Ephraem), auteur(Chrysostomi), ouvrage(opera quaedam), material(Cod. chart. in quart), date(Saec. XV), etat(mutilus in principio) |
| 297 | 297 Martyrologium. Cod. membran. in quarto Saec. XIII. | ouvrage(Martyrologium), material(Cod. membran. in qua), date(Saec. XIII.) |
| 333 | 333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. … | ouvrage(Vitae S. Ioannis Gua), material(Cod. membr. in. 8.), date(Saec. XV) |
| 338 | 338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV. | auteur(Leonis Urbevetani), ouvrage(chronicon et alia), material(Cod. membr.), date(Saec XIV) |
| 351 | 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Fici… | auteur(Basilii), auteur(Marsilii Ficini), ouvrage(oratio ad juvenes), material(Cod. chart. in quart), date(Saec. XV) |
| 1232 | 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggi… | auteur(Boccaccii), ouvrage(Eclogae ad Donatum A), material(Cod. mem. in 8.), date(Saec. XIV) |
| 1298 | 1298 da Cascia Fra Simone, volgarizzamento ed Esposizione dei Vangeli. Cod. cart… | auteur(da Cascia Fra Simone), ouvrage(Esposizione dei Vang), material(Cod. cart. fol.), date(Sec. XV) |
| 1512 | 1512 Meditazioni sacre. Cod. membran. in 16. Sec. XV. | ouvrage(Meditazioni sacre), material(Cod. membran. in 16.), date(Sec. XV) |
