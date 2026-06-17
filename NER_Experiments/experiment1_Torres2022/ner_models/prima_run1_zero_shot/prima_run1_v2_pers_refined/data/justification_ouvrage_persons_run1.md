# Justification de la distinction *auteur* / personnes dans les *ouvrages* — Run 1

## Contexte

Dans notre gold standard (catalogue Riccardiana), le label `ouvrage` désigne le titre d'une œuvre. Certains titres contiennent des noms de personnes historiques réelles (saints, humanistes, personnages bibliques), que le modèle NER prédit comme `PERS`. Cette distinction est essentielle pour interpréter les faux positifs du modèle dans Run 1 : le modèle identifie correctement un nom de personne sur le plan lexical, mais ce nom appartient à un span annoté `ouvrage` dans notre gold, non `auteur`.

---

## TEST.JSON

### Entrée 333

**Texte brut :** `333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV.`

**Label gold :** `ouvrage` = `"Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum"`

#### Ioannis Gualberti (= Giovanni Gualberto)

- **Type :** Personne historique réelle, saint catholique
- **Rôle dans le titre :** Sujet de la biographie hagiographique (*Vitae* = Vies des saints), **non auteur**
- **Dates :** c. 985 – 12 juillet 1073, Florence, Italie
- **Wikidata :** [Q707172](https://www.wikidata.org/wiki/Q707172)
- **VIAF :** [64818224](https://viaf.org/viaf/64818224)
- **Noms latins attestés :** *Ioannes Gualbertus*, *Iohannis Gualberti* (génitif), *Johannes Gualbertus*, *Johannis Gualberti*
- **Notice LoC :** `n85152848` — « Giovanni Gualberto, Saint, approximately 1000–1073 »
- **Résumé :** Noble florentin (famille Visdomini), fondateur de l'Ordre vallombrosain (1038), canonisé en 1193 par le pape Célestin III. Patron des forestiers.

#### Bernardi (= Bernard de Clairvaux)

- **Type :** Personne historique réelle, saint catholique, Docteur de l'Église
- **Rôle dans le titre :** Sujet de la biographie hagiographique, **non auteur**
- **Dates :** 1090 – 20 août 1153
- **Wikidata :** [Q188411](https://www.wikidata.org/wiki/Q188411)
- **VIAF :** [59875293](https://viaf.org/viaf/59875293)
- **Noms latins attestés :** *Bernardus Claraevallensis*, *Bernardi* (génitif)
- **Résumé :** Abbé cistercien, co-fondateur de l'Ordre des Templiers, réformateur bénédictin majeur, Docteur de l'Église.

**Conclusion :** Les noms *Ioannis Gualberti* et *Bernardi* sont des noms propres de personnages historiques réels, mais ils apparaissent ici comme **sujets d'une hagiographie**, non comme auteurs. Le modèle peut les prédire comme `PERS` (lexicalement correct), mais dans notre gold, l'ensemble du titre est annoté `ouvrage`.

---

### Entrée 1232

**Texte brut :** `1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV.`

**Labels gold :** `auteur` = `"Boccaccii"` ; `ouvrage` = `"Eclogae ad Donatum Apenninigenam"`

#### Donatum Apenninigenam (= Donato degli Albanzani)

- **Type :** Personne historique réelle, humaniste
- **Rôle dans le titre :** Dédicataire de l'œuvre (*ad Donatum* = à l'adresse de Donato), **non auteur**
- **Dates :** c. 1326/1328, Pratovecchio – c. 1411, Ferrare
- **Wikidata :** [Q3713731](https://www.wikidata.org/wiki/Q3713731)
- **VIAF :** [59443057](https://viaf.org/viaf/59443057)
- **Forme latine :** *Donatus Appenninigena* ou *Apenninigena* (surnom donné par Pétrarque, signifiant « né de l'Apennin »)
- **Attestation :** Treccani, *Dizionario Biografico degli Italiani*, vol. 1 (1960) : « presso gli amici umanisti *Donatus Appenninigena* o *Apenninigena*, nome impostogli probabilmente dal Petrarca »
- **Contexte :** Ami du Boccace et de Pétrarque, grammairien et rhétoricien. Boccace lui a dédié le *Bucolicum carmen* (1367). Les *Eclogae* de l'entrée 1232 sont vraisemblablement ce *Bucolicum carmen*.

**Conclusion :** *Donatum Apenninigenam* est à l'accusatif (complément de *ad*), désignant le **dédicataire**, pas l'auteur. L'auteur est *Boccaccii* (annoté `auteur`). Le modèle peut prédire *Donatum* comme `PERS`, créant un faux positif pour la catégorie `auteur`.

---

## TRAIN.JSON

### Entrée 291

**Texte brut :** `291 Psalterium Davidis. Cod. membran. in fol. Saec. XIII venustissimus.`

**Label gold :** `ouvrage` = `"Psalterium Davidis"`

#### Davidis (= David, roi d'Israël)

- **Type :** Figure biblique, roi de la tradition hébraïque
- **Rôle dans le titre :** Auteur traditionnel attribué des Psaumes (génitif de possession), **non auteur au sens bibliographique** (recueil collectif et anonyme)
- **Dates :** c. 1010 – 970 av. J.-C.
- **Wikidata :** [Q41370](https://www.wikidata.org/wiki/Q41370)
- **Forme latine :** *David* (indéclinable ou 3e déclinaison), génitif *Davidis*

**Conclusion :** *Davidis* est un nom propre dans le titre de l'œuvre ; le modèle peut le prédire comme `PERS`, mais notre gold l'intègre dans le label `ouvrage`.

---

### Entrée 342

**Texte brut :** `342 Bauriae, Fr. Andrene, Defensio Apostolicae potestatis contra Lutherum. Cod. chart. in 4 Saec. XVI.`

**Labels gold :** `auteur` = `"Fr. Andrene"` ; `ouvrage` = `"Defensio Apostolicae potestatis contra Lutherum"`

#### Lutherum (= Martin Luther)

- **Type :** Personne historique réelle, théologien réformateur
- **Rôle dans le titre :** Cible d'une polémique (accusatif de *contra*), **non auteur**
- **Dates :** 10 novembre 1483, Eisleben – 18 février 1546
- **Wikidata :** [Q9554](https://www.wikidata.org/wiki/Q9554)
- **VIAF :** [14773105](https://viaf.org/viaf/14773105)
- **Forme latine :** *Lutherus*, accusatif *Lutherum*
- **Contexte :** L'œuvre est une réfutation de Luther par *Frater Andreas de Bauria* (auteur catholique). Le titre *Defensio contra Lutherum* relève d'un topos polémique fréquent au XVIe siècle.

**Conclusion :** *Lutherum* est un nom propre dans le titre ; le modèle peut le prédire comme `PERS`, mais notre gold l'intègre dans le label `ouvrage`.

---

### Entrées 456, 457, 468, 469

**Ouvrages :** `Officium B. M. Virginis` (et variantes)

**Personne implicite :** *B. M. Virginis* = *Beatae Mariae Virginis* = Vierge Marie — Wikidata [Q345](https://www.wikidata.org/wiki/Q345), VIAF [268615423](https://viaf.org/viaf/268615423)

**Conclusion :** *Virginis* est un génitif qualificatif dans un titre liturgique standard. Probabilité faible que le modèle prédise `PERS` pour ce terme isolé. Ces entrées restent marquées `ouvrage` uniquement, sans sous-label.

---

### Entrée 1349

**Texte brut :** `1349 Apocalisse di S. Gio. Pistola di S. Bernardo del governo della famiglia ec. Cod. cart. in fol. Sec. XV.`

**Labels gold :** `auteur` = `"S. Bernardo"` ; `ouvrage` = `"Apocalisse di S. Gio"` ; `ouvrage` = `"del governo della famiglia"`

#### S. Gio. (= San Giovanni, l'Évangéliste)

- **Type :** Figure biblique, saint catholique
- **Rôle dans le titre :** Auteur traditionnel attribué de l'Apocalypse, annoté `ouvrage` dans notre gold
- **Wikidata :** [Q43274](https://www.wikidata.org/wiki/Q43274) — VIAF [89659771](https://viaf.org/viaf/89659771)

**Conclusion :** *S. Gio.* est une abréviation dans le texte brut ; risque faible que le modèle le reconnaisse comme `PERS`.

---

### Entrée 293

**Texte brut :** `293 S. Matthaei Evangelium, cum glossis marginalibus. Accedit Evang. S. Johannis. Cod. membr. in quarto Saec. XIII.`

**Labels gold :** `ouvrage` = `"S. Matthaei Evangelium"` ; `ouvrage` = `"Evang. S. Johanni"`

- *Matthaei* = Saint Matthieu, évangéliste — Wikidata [Q43423](https://www.wikidata.org/wiki/Q43423)
- *Johanni* = Saint Jean, évangéliste — Wikidata [Q43274](https://www.wikidata.org/wiki/Q43274)

**Conclusion :** Noms propres d'évangélistes intégrés dans des titres d'œuvres scripturaires ; `PERS` prédit par le modèle constituerait un faux positif.

---

### Entrées 426 et 356

| Entrée | Ouvrage | Nom propre | Identification | Rôle | Décision |
|--------|---------|------------|----------------|------|----------|
| 426 | *Evangelia, et Epistolae D. Paulli* | *D. Paulli* | Saint Paul (Q9200, VIAF 51780650) | Auteur attribué | pers_in_ouvrage ✅ |
| 356 | *Ceremoniale Basilicae S. Petri* | *S. Petri* | Saint Pierre (Q33923, VIAF 22933420) | Désignation de lieu | pers_in_ouvrage (risque faible) |

---

## VAL.JSON

### Entrée 334

**Texte brut :** `334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV.`

**Labels gold :** `auteur` = `"Iustiniani Leonardi"` ; `ouvrage` = `"vita S. Nicolai"`

#### S. Nicolai (= Saint Nicolas de Myre)

- **Type :** Saint catholique
- **Rôle dans le titre :** Sujet d'une biographie hagiographique (*vita* = vie), **non auteur**
- **Dates :** c. 270 – c. 343, Myre (Turquie actuelle)
- **Wikidata :** [Q44746](https://www.wikidata.org/wiki/Q44746) — VIAF [88969561](https://viaf.org/viaf/88969561)
- **Auteur réel :** *Iustiniani Leonardi* = Leonardo Giustiniani (c. 1388–1446), humaniste et homme d'État vénitien.

**Conclusion :** *Nicolai* (génitif de *Nicolaus*) est un nom propre dans le titre de l'hagiographie. Faux positif potentiel du modèle.

---

### Entrée 1350

**Texte brut :** `1350 Gradi di S. Girolamo. Cod. cartac. in fol. Sec. XIV sul fine, manc. in fine.`

**Labels gold :** `auteur` = `"S. Girolamo"` ; `ouvrage` = `"Gradi di S. Girolamo"`

**Cas particulier :** Le même nom *S. Girolamo* est à la fois `auteur` ET contenu dans le titre de l'`ouvrage`.

#### S. Girolamo (= Saint Jérôme)

- **Type :** Père de l'Église, traducteur de la Vulgate
- **Dates :** c. 342/347 – 30 septembre 420
- **Wikidata :** [Q44248](https://www.wikidata.org/wiki/Q44248) — VIAF [95147024](https://viaf.org/viaf/95147024)
- **Noms latins :** *Sophronius Eusebius Hieronymus* (complet), *Hieronymus*, *S. Hieronymus*
- **Notice LoC :** `n79124709` — « Jerome, Saint, -419 or 420 »

**Conclusion :** Cas ambivalent : *S. Girolamo* est à la fois annoté `auteur` et présent dans le titre de l'`ouvrage`. Cette double occurrence illustre précisément le phénomène que notre analyse cherche à capturer.

---

### Entrée 1618

**Texte brut :** `1618 Boezio, volgarizzato da M. Alberto. Cod. cart. in quarto Sec. XV. mancante di una pagina in principio.`

**Labels gold :** `auteur` = `"Boezio"` ; `auteur` = `"M. Alberto"` ; `ouvrage` = `"Boezio, volgarizzato"`

**Cas particulier :** *Boezio* est à la fois `auteur` ET première partie du titre de l'`ouvrage`.

#### Boezio (= Boèce)

- **Type :** Philosophe et homme d'État romain du haut Moyen Âge
- **Dates :** c. 480 – 524 ap. J.-C., Pavie (Ostrogothie)
- **Wikidata :** [Q102851](https://www.wikidata.org/wiki/Q102851) — VIAF [100218964](https://viaf.org/viaf/100218964)
- **Nom latin complet :** *Anicius Manlius Severinus Boethius*
- **Œuvre principale :** *De consolatione philosophiae*
- **Contexte :** *Boezio, volgarizzato* = traduction italienne de Boèce par *M. Alberto* (probablement Alberto della Piagentina, XIVe s.).

**Conclusion :** Même logique que l'entrée 1350 : nom d'auteur réutilisé dans le titre de l'ouvrage sous forme abrégée.

---

## Tableau récapitulatif

| Fichier | Entrée | Ouvrage (gold) | Nom propre | Identité | Wikidata | VIAF | Rôle | Décision Run 1 |
|---------|--------|----------------|------------|----------|----------|------|------|----------------|
| test | 333 | *Vitae S. Ioannis Gualberti...* | Ioannis Gualberti | Giovanni Gualberto, saint (c.985–1073) | Q707172 | 64818224 | Sujet hagiographique | pers_in_ouvrage ✅ |
| test | 333 | idem | Bernardi | Bernard de Clairvaux (1090–1153) | Q188411 | 59875293 | Sujet hagiographique | pers_in_ouvrage ✅ |
| test | 1232 | *Eclogae ad Donatum Apenninigenam* | Donatum Apenninigenam | Donato degli Albanzani (c.1328–c.1411) | Q3713731 | 59443057 | Dédicataire | pers_in_ouvrage ✅ |
| train | 291 | *Psalterium Davidis* | Davidis | David, roi d'Israël | Q41370 | — | Auteur attribué | pers_in_ouvrage ✅ |
| train | 342 | *Defensio...contra Lutherum* | Lutherum | Martin Luther (1483–1546) | Q9554 | 14773105 | Cible polémique | pers_in_ouvrage ✅ |
| train | 1349 | *Apocalisse di S. Gio* | S. Gio. | Saint Jean l'Évangéliste | Q43274 | 89659771 | Auteur attribué (abrégé) | pers_in_ouvrage (risque faible) |
| train | 293 | *S. Matthaei Evangelium* | Matthaei | Saint Matthieu, évangéliste | Q43423 | — | Auteur attribué | pers_in_ouvrage ✅ |
| train | 293 | *Evang. S. Johanni* | Johanni | Saint Jean, évangéliste | Q43274 | — | Auteur attribué | pers_in_ouvrage ✅ |
| train | 426 | *Evangelia, et Epistolae D. Paulli* | D. Paulli | Saint Paul apôtre | Q9200 | 51780650 | Auteur attribué | pers_in_ouvrage ✅ |
| train | 356 | *Ceremoniale Basilicae S. Petri* | S. Petri | Saint Pierre apôtre | Q33923 | 22933420 | Désignation de lieu | pers_in_ouvrage (risque faible) |
| val | 334 | *vita S. Nicolai* | S. Nicolai | Saint Nicolas de Myre (c.270–343) | Q44746 | 88969561 | Sujet hagiographique | pers_in_ouvrage ✅ |
| val | 1350 | *Gradi di S. Girolamo* | S. Girolamo | Saint Jérôme (c.347–420) | Q44248 | 95147024 | Auteur répété dans le titre | pers_in_ouvrage ✅ |
| val | 1618 | *Boezio, volgarizzato* | Boezio | Boèce (c.480–524) | Q102851 | 100218964 | Auteur répété dans le titre | pers_in_ouvrage ✅ |

---

## Note méthodologique

Les cas marqués « risque faible » (*B. M. Virginis*, *S. Gio.*, *S. Petri*) correspondent à des formes abrégées ou à des titres liturgiques figés dans lesquels la probabilité que le modèle prédise `PERS` est faible. Les cas prioritaires pour l'analyse Run 1 sont ceux marqués ✅.

---

*Document préparé pour le projet PRIMA (ERC Grant 101142242), LIFAT — Université de Tours, juin 2026.*

---
---

# 佐证文件：ouvrage 中人名的区分依据 — Run 1

## 背景

在我们的 gold 标注体系（里恰尔迪亚纳目录）中，`ouvrage` 标签指代作品名。部分作品名含有真实历史人物（圣人、人文主义者、圣经人物）的名字，NER 模型会将其预测为 `PERS`。这一区分对于解读 Run 1 中模型的假阳性至关重要：模型在词汇层面正确识别了一个人名，但该人名所属的 span 在 gold 标注中为 `ouvrage`，而非 `auteur`。

---

## TEST.JSON

### 条目 333

**原始文本：** `333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV.`

**Gold 标签：** `ouvrage` = `"Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum"`

#### Ioannis Gualberti（= Giovanni Gualberto）

- **类型：** 真实历史人物，天主教圣人
- **在标题中的角色：** 圣徒传记的主题人物（*Vitae* = 圣人传记），**非作者**
- **生卒：** 约 985 年 – 1073 年 7 月 12 日，意大利佛罗伦萨
- **Wikidata：** [Q707172](https://www.wikidata.org/wiki/Q707172)
- **VIAF：** [64818224](https://viaf.org/viaf/64818224)
- **拉丁文形式：** *Ioannes Gualbertus*，属格 *Ioannis Gualberti*；另有 *Johannes Gualbertus*、*Johannis Gualberti*
- **LoC 记录：** `n85152848` — 「Giovanni Gualberto, Saint, approximately 1000–1073」
- **简介：** 佛罗伦萨贵族（Visdomini 家族），瓦隆布罗萨修会创始人（1038 年），1193 年由教皇塞莱斯廷三世封圣，护林者守护圣人。

#### Bernardi（= Bernard de Clairvaux，明谷伯纳德）

- **类型：** 真实历史人物，天主教圣人，教会博士
- **在标题中的角色：** 圣徒传记的主题人物，**非作者**
- **生卒：** 1090 年 – 1153 年 8 月 20 日
- **Wikidata：** [Q188411](https://www.wikidata.org/wiki/Q188411)
- **VIAF：** [59875293](https://viaf.org/viaf/59875293)
- **拉丁文形式：** *Bernardus Claraevallensis*，属格 *Bernardi*
- **简介：** 西多会修道院院长，圣殿骑士团联合创始人，本笃会主要改革者，教会博士。

**结论：** *Ioannis Gualberti* 和 *Bernardi* 是真实历史人物的名字，但在此处作为**圣徒传的主题人物**出现，而非作者。模型可能将其预测为 `PERS`（词汇层面正确），但在我们的 gold 标注中，整个作品名标注为 `ouvrage`。

---

### 条目 1232

**原始文本：** `1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV.`

**Gold 标签：** `auteur` = `"Boccaccii"` ；`ouvrage` = `"Eclogae ad Donatum Apenninigenam"`

#### Donatum Apenninigenam（= Donato degli Albanzani）

- **类型：** 真实历史人物，人文主义者
- **在标题中的角色：** 作品的献赠对象（*ad Donatum* = 致赠 Donato），**非作者**
- **生卒：** 约 1326/1328 年，普拉托韦基奥 – 约 1411 年，费拉拉
- **Wikidata：** [Q3713731](https://www.wikidata.org/wiki/Q3713731)
- **VIAF：** [59443057](https://viaf.org/viaf/59443057)
- **拉丁文形式：** *Donatus Appenninigena* 或 *Apenninigena*（绰号，由彼特拉克所赐，意为"亚平宁山之子"）
- **文献依据：** Treccani，《意大利人名词典》第 1 卷（1960）：「presso gli amici umanisti *Donatus Appenninigena* o *Apenninigena*, nome impostogli probabilmente dal Petrarca」
- **背景：** 薄伽丘和彼特拉克的朋友，语法学家和修辞学家。薄伽丘于 1367 年将《牧歌集》（*Bucolicum carmen*）题献给他。条目 1232 的 *Eclogae* 即此作品。

**结论：** *Donatum Apenninigenam* 为宾格（*ad* 的宾语），指**献赠对象**，非作者。作者为 *Boccaccii*（已标注 `auteur`）。模型可能将 *Donatum* 预测为 `PERS`，形成 `auteur` 类别的假阳性。

---

## TRAIN.JSON

### 条目 291

**原始文本：** `291 Psalterium Davidis. Cod. membran. in fol. Saec. XIII venustissimus.`

**Gold 标签：** `ouvrage` = `"Psalterium Davidis"`

#### Davidis（= 以色列国王大卫）

- **类型：** 圣经人物，希伯来传统中的国王
- **在标题中的角色：** 诗篇的传统归属作者（属格表所属关系：大卫的诗篇），但**非书目意义上的作者**（诗篇为集体匿名创作）
- **年代：** 约公元前 1010 – 970 年（据圣经传统）
- **Wikidata：** [Q41370](https://www.wikidata.org/wiki/Q41370)
- **拉丁文形式：** *David*（不变格或第三变格法），属格 *Davidis*

**结论：** *Davidis* 是作品名中的专有名词；模型可能将其预测为 `PERS`，但 gold 将其包含在 `ouvrage` 标签内。

---

### 条目 342

**原始文本：** `342 Bauriae, Fr. Andrene, Defensio Apostolicae potestatis contra Lutherum. Cod. chart. in 4 Saec. XVI.`

**Gold 标签：** `auteur` = `"Fr. Andrene"` ；`ouvrage` = `"Defensio Apostolicae potestatis contra Lutherum"`

#### Lutherum（= 马丁·路德）

- **类型：** 真实历史人物，宗教改革神学家
- **在标题中的角色：** 论战的攻击对象（*contra* 的宾格 = 反对路德），**非作者**
- **生卒：** 1483 年 11 月 10 日，艾斯莱本 – 1546 年 2 月 18 日
- **Wikidata：** [Q9554](https://www.wikidata.org/wiki/Q9554)
- **VIAF：** [14773105](https://viaf.org/viaf/14773105)
- **拉丁文形式：** *Lutherus*，宾格 *Lutherum*
- **背景：** 此作品是 *Frater Andreas de Bauria*（天主教作者）对路德的反驳，《反路德辩护》是 16 世纪常见的论战体裁。

**结论：** *Lutherum* 是作品名中的专有名词，模型可能预测为 `PERS`，但 gold 将其包含在 `ouvrage` 标签内。

---

### 条目 456、457、468、469

**作品名：** `Officium B. M. Virginis`（及变体）

**隐含人名：** *B. M. Virginis* = *Beatae Mariae Virginis* = 圣母玛利亚 — Wikidata [Q345](https://www.wikidata.org/wiki/Q345)，VIAF [268615423](https://viaf.org/viaf/268615423)

**结论：** *Virginis* 是标准礼仪标题中的形容词性属格。模型将其单独预测为 `PERS` 的概率**较低**（非典型孤立专有名词形式）。这些条目不创建子标签，仅保留 `ouvrage` 标注。

---

### 条目 1349

**原始文本：** `1349 Apocalisse di S. Gio. Pistola di S. Bernardo del governo della famiglia ec. Cod. cart. in fol. Sec. XV.`

**Gold 标签：** `auteur` = `"S. Bernardo"` ；`ouvrage` = `"Apocalisse di S. Gio"` ；`ouvrage` = `"del governo della famiglia"`

#### S. Gio.（= San Giovanni，圣若望福音书作者）

- **类型：** 圣经人物，天主教圣人
- **在标题中的角色：** 《启示录》的传统归属作者，但在 gold 中整体标注为 `ouvrage`
- **Wikidata：** [Q43274](https://www.wikidata.org/wiki/Q43274) — VIAF [89659771](https://viaf.org/viaf/89659771)

**结论：** *S. Gio.* 在原文中是缩写，模型识别为 `PERS` 的概率较低。风险较小。

---

### 条目 293

**原始文本：** `293 S. Matthaei Evangelium, cum glossis marginalibus. Accedit Evang. S. Johannis. Cod. membr. in quarto Saec. XIII.`

**Gold 标签：** `ouvrage` = `"S. Matthaei Evangelium"` ；`ouvrage` = `"Evang. S. Johanni"`

- *Matthaei* = 圣马太，福音书作者 — Wikidata [Q43423](https://www.wikidata.org/wiki/Q43423)
- *Johanni* = 圣约翰，福音书作者 — Wikidata [Q43274](https://www.wikidata.org/wiki/Q43274)

**结论：** 福音书作者名包含在圣经典籍作品名中。模型预测为 `PERS` 即构成假阳性。

---

### 条目 426 和 356

| 条目 | 作品名 | 人名 | 身份 | 在标题中的角色 | 决定 |
|------|--------|------|------|----------------|------|
| 426 | *Evangelia, et Epistolae D. Paulli* | *D. Paulli* | 圣保罗使徒（Q9200，VIAF 51780650） | 归属作者 | pers_in_ouvrage ✅ |
| 356 | *Ceremoniale Basilicae S. Petri* | *S. Petri* | 圣伯多禄使徒（Q33923，VIAF 22933420） | 地点命名 | pers_in_ouvrage（风险较低） |

---

## VAL.JSON

### 条目 334

**原始文本：** `334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV.`

**Gold 标签：** `auteur` = `"Iustiniani Leonardi"` ；`ouvrage` = `"vita S. Nicolai"`

#### S. Nicolai（= 圣尼古拉，米拉主教）

- **类型：** 天主教圣人
- **在标题中的角色：** 圣徒传记的主题人物（*vita* = 传记），**非作者**
- **生卒：** 约公元 270 – 343 年，米拉（今土耳其）
- **Wikidata：** [Q44746](https://www.wikidata.org/wiki/Q44746) — VIAF [88969561](https://viaf.org/viaf/88969561)
- **真实作者：** *Iustiniani Leonardi* = Leonardo Giustiniani（约 1388–1446），威尼斯人文主义者和政治家。

**结论：** *Nicolai*（*Nicolaus* 的属格）是圣徒传作品名中的专有名词，模型可能预测为 `PERS`，形成假阳性。

---

### 条目 1350

**原始文本：** `1350 Gradi di S. Girolamo. Cod. cartac. in fol. Sec. XIV sul fine, manc. in fine.`

**Gold 标签：** `auteur` = `"S. Girolamo"` ；`ouvrage` = `"Gradi di S. Girolamo"`

**特殊情况：** 同一名字 *S. Girolamo* 同时作为 `auteur` 和 `ouvrage` 标题中的人名出现。

#### S. Girolamo（= 圣热罗尼莫，圣杰罗姆）

- **类型：** 教会教父，拉丁圣经（武加大译本）译者
- **生卒：** 约公元 342/347 年 – 420 年 9 月 30 日
- **Wikidata：** [Q44248](https://www.wikidata.org/wiki/Q44248) — VIAF [95147024](https://viaf.org/viaf/95147024)
- **拉丁文形式：** 完整名 *Sophronius Eusebius Hieronymus*；常用 *Hieronymus*、*S. Hieronymus*；意大利语 *San Girolamo*
- **LoC 记录：** `n79124709` — 「Jerome, Saint, -419 or 420」

**结论：** 边界案例：*S. Girolamo* 同时作为 `auteur`（作品作者）和 `ouvrage` 名中的人名出现。这种双重出现正是我们分析试图捕捉的典型现象。

---

### 条目 1618

**原始文本：** `1618 Boezio, volgarizzato da M. Alberto. Cod. cart. in quarto Sec. XV. mancante di una pagina in principio.`

**Gold 标签：** `auteur` = `"Boezio"` ；`auteur` = `"M. Alberto"` ；`ouvrage` = `"Boezio, volgarizzato"`

**特殊情况：** *Boezio* 同时作为 `auteur` 和 `ouvrage` 标题首部出现。

#### Boezio（= 波埃修斯，Boèce）

- **类型：** 早期中世纪罗马哲学家和政治家
- **生卒：** 约公元 480 – 524 年，帕维亚（东哥特王国）
- **Wikidata：** [Q102851](https://www.wikidata.org/wiki/Q102851) — VIAF [100218964](https://viaf.org/viaf/100218964)
- **完整拉丁名：** *Anicius Manlius Severinus Boethius*
- **主要作品：** *De consolatione philosophiae*（《哲学的慰藉》）
- **背景：** *Boezio, volgarizzato* 指波埃修斯作品的意大利语译本，译者 *M. Alberto* 身份尚不完全确定（可能为 Alberto della Piagentina，14 世纪）。

**结论：** 与条目 1350 逻辑相同：作者名以简略形式（*Boezio, volgarizzato*）复现于作品名中。

---

## 汇总表

| 文件 | 条目 | Gold 作品名（ouvrage） | 人名 | 人物身份 | Wikidata | VIAF | 在标题中的角色 | Run 1 决定 |
|------|------|----------------------|------|----------|----------|------|----------------|------------|
| test | 333 | *Vitae S. Ioannis Gualberti...* | Ioannis Gualberti | Giovanni Gualberto，圣人（约985–1073） | Q707172 | 64818224 | 传记主题 | pers_in_ouvrage ✅ |
| test | 333 | 同上 | Bernardi | Bernard de Clairvaux（1090–1153） | Q188411 | 59875293 | 传记主题 | pers_in_ouvrage ✅ |
| test | 1232 | *Eclogae ad Donatum Apenninigenam* | Donatum Apenninigenam | Donato degli Albanzani（约1328–约1411） | Q3713731 | 59443057 | 献赠对象 | pers_in_ouvrage ✅ |
| train | 291 | *Psalterium Davidis* | Davidis | 以色列国王大卫 | Q41370 | — | 归属作者 | pers_in_ouvrage ✅ |
| train | 342 | *Defensio...contra Lutherum* | Lutherum | 马丁·路德（1483–1546） | Q9554 | 14773105 | 论战对象 | pers_in_ouvrage ✅ |
| train | 1349 | *Apocalisse di S. Gio* | S. Gio. | 圣若望福音书作者 | Q43274 | 89659771 | 归属作者（缩写） | pers_in_ouvrage（风险较低） |
| train | 293 | *S. Matthaei Evangelium* | Matthaei | 圣马太，福音书作者 | Q43423 | — | 归属作者 | pers_in_ouvrage ✅ |
| train | 293 | *Evang. S. Johanni* | Johanni | 圣约翰，福音书作者 | Q43274 | — | 归属作者 | pers_in_ouvrage ✅ |
| train | 426 | *Evangelia, et Epistolae D. Paulli* | D. Paulli | 圣保罗使徒 | Q9200 | 51780650 | 归属作者 | pers_in_ouvrage ✅ |
| train | 356 | *Ceremoniale Basilicae S. Petri* | S. Petri | 圣伯多禄使徒 | Q33923 | 22933420 | 地点命名 | pers_in_ouvrage（风险较低） |
| val | 334 | *vita S. Nicolai* | S. Nicolai | 圣尼古拉，米拉主教（约270–343） | Q44746 | 88969561 | 传记主题 | pers_in_ouvrage ✅ |
| val | 1350 | *Gradi di S. Girolamo* | S. Girolamo | 圣热罗尼莫（约347–420） | Q44248 | 95147024 | 作者名复现于标题 | pers_in_ouvrage ✅ |
| val | 1618 | *Boezio, volgarizzato* | Boezio | 波埃修斯（约480–524） | Q102851 | 100218964 | 作者名复现于标题 | pers_in_ouvrage ✅ |

---

## 方法论说明

标注为「风险较低」的情况（*B. M. Virginis*、*S. Gio.*、*S. Petri*）对应于缩写形式或固定礼仪标题，模型将其预测为 `PERS` 的概率较低。Run 1 分析的优先案例为汇总表中标注 ✅ 的条目。

---

*本文件为 PRIMA 项目（ERC 资助 101142242）准备，LIFAT — 图尔大学，2026 年 6 月。*
