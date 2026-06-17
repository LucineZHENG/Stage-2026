# Rapport d'analyse — Run 1 : modèle médiéval (zero-shot)

**Modèle** : `magistermilitum/roberta-multilingual-medieval-ner`  
**Date** : 2026-05-26 06:06  
**Données** : `test.json` (10 entrées)  
**Évaluation** : `auteur` (gold) → `PERS` (pred) uniquement

---

## 1. Définitions des métriques d'évaluation

### Français

| Métrique | Définition |
|---|---|
| **Precision** | Parmi toutes les entités prédites par le modèle, quelle proportion est correcte ? Une precision faible signifie beaucoup de fausses alarmes (faux positifs). |
| **Recall** | Parmi toutes les entités réellement présentes dans le gold standard, quelle proportion a été détectée ? Un recall faible signifie que le modèle rate beaucoup d'entités (faux négatifs). |
| **F1-score** | Moyenne harmonique de la precision et du recall. Indicateur d'équilibre entre les deux. F1 = 2 × (P × R) / (P + R). |
| **Micro avg** | Calcule P/R/F1 en agrégeant tous les tokens de toutes les classes ensemble. Donne plus de poids aux classes fréquentes. |
| **Macro avg** | Calcule P/R/F1 séparément pour chaque classe, puis fait la moyenne simple. Chaque classe a le même poids, indépendamment de sa fréquence. |
| **Weighted avg** | Comme le macro avg, mais pondéré par le nombre d'instances de chaque classe (support). Tient compte du déséquilibre entre classes. |


### 中文

| 指标 | 定义 |
|---|---|
| **Precision（精确率）** | 在模型预测的所有实体中，真正正确的比例。精确率低意味着误报多（假阳性多）。|
| **Recall（召回率）** | 在gold标准中实际存在的所有实体中，被模型成功识别的比例。召回率低意味着漏报多（假阴性多）。|
| **F1-score** | 精确率和召回率的调和平均数，综合衡量两者的平衡。公式：F1 = 2×(P×R)/(P+R)。|
| **Micro avg（微平均）** | 将所有类别的token合并后统一计算P/R/F1，频率高的类别权重更大。|
| **Macro avg（宏平均）** | 对每个类别分别计算P/R/F1后取简单平均，每个类别权重相同，不考虑频率差异。|
| **Weighted avg（加权平均）** | 类似宏平均，但按每个类别的样本数量加权，能反映类别不平衡的影响。|

---

## 2. Résultats globaux (seqeval — entité stricte)

```

              precision    recall  f1-score   support

        PERS       0.45      0.50      0.48        10

   micro avg       0.45      0.50      0.48        10
   macro avg       0.45      0.50      0.48        10
weighted avg       0.45      0.50      0.48        10

```

- **F1** = 0.4762  
- **Precision** = 0.4545  
- **Recall** = 0.5000

> ⚠️ Évaluation stricte : une entité n'est comptée comme correcte que si ses bornes correspondent exactement au gold standard (pas de correspondance partielle).

---

## 3. Analyse des erreurs par type

| Type d'erreur | Nb entrées | entry_ids |
|---|---|---|
| ✅ Correct (pas d'auteur attendu ni prédit) | 2 | #297, #1512 |
| ❌ Faux négatif — modèle n'a pas détecté l'auteur | 3 | #1298, #276, #235 |
| ⚠️ Faux positif — modèle a prédit un auteur inexistant | 1 | #333 |
| 〰️ Erreur de frontière — détection partielle | 4 | #338, #351, #286, #1232 |

---

## 4. Exemples détaillés

### ❌ Type 1 : Faux négatifs — auteur non détecté

*Le modèle n'a prédit aucune entité PERS là où le gold indique un auteur. Cause probable : forme latine génitif (-i, -ii) peu fréquente dans les chartes médiévales ; entrée non conventionnelle (ex. `da Cascia Fra Simone`).*

**Entrée #1298**

```
Texte : 1298 da Cascia Fra Simone, volgarizzamento ed Esposizione dei Vangeli. Cod. cart. fol. Sec. XV sul princ.
Gold  : ['da Cascia Fra Simone']
Préd  : []
```

**Entrée #276**

```
Texte : 276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec. XII in fol. in fine mutilus, sed eleganter scriptus, ac bene servatus.
Gold  : ['Hieronymi', 'Origenis']
Préd  : []
```

**Entrée #235**

```
Texte : 235 Origenes, super vetus Testamentum. Cod. membr. in fol. Saec. XV in fine mutilus.
Gold  : ['Origenes']
Préd  : []
```

### ⚠️ Type 2 : Faux positifs — entité prédite sans gold

*Le modèle a détecté des personnes réelles (saints, personnages dans les titres) qui ne sont pas des auteurs au sens de notre annotation. Cause : le modèle reconnaît tous les noms de personnes, pas seulement les auteurs.*

**Entrée #333**

```
Texte : 333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV.
Gold  : []
Préd  : ['Ioannis', 'Gu', 'al', 'ber', 'Bernard']
```

### 〰️ Type 3 : Erreurs de frontière — détection partielle

*Le modèle identifie la bonne entité mais avec des bornes incorrectes. Cause : tokenisation en sous-mots (subword) de XLM-RoBERTa, qui découpe les tokens différemment de notre annotation au niveau du mot.*

**Entrée #338**

```
Texte : 338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV.
Gold  : ['Leonis Urbevetani']
Préd  : ['Leonis Urbe']
```

**Entrée #351**

```
Texte : 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod. chart. in quarto Saec. XV.
Gold  : ['Basilii', 'Marsilii Ficini']
Préd  : ['Basil', 'Mar', 'silii Fi']
```

**Entrée #286**

```
Texte : 286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mutilus in principio
Gold  : ['S. Ephraem', 'Chrysostomi']
Préd  : ['E', 'phra', 'Ch', 'rys', 'os']
```

**Entrée #1232**

```
Texte : 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa a Tommaso Spinelli. In cornice.
Gold  : ['Boccaccii']
Préd  : ['Boc', 'cacci', 'Antoni', 'Tommaso Spinelli']
```

---

## 5. Conclusion

Le modèle `magistermilitum/roberta-multilingual-medieval-ner` obtient un **F1 de 0.4762** (P=0.4545, R=0.5000) en mode zero-shot sur notre test set de 10 entrées, évalué uniquement sur la correspondance `auteur` → `PERS`.

Les principales limites observées sont :
1. **Faux négatifs** : le modèle rate les auteurs en forme génitif latin et les noms non conventionnels.
2. **Faux positifs** : le modèle détecte des personnages cités dans les titres d'ouvrages comme auteurs.
3. **Erreurs de frontière** : la tokenisation subword crée des décalages de bornes.

Ces résultats confirment que le modèle, bien qu'entraîné sur des textes médiévaux latins, n'est pas adapté à notre tâche spécifique (catalogue de manuscrits vs chartes diplomatiques) et justifient l'entraînement d'un modèle dédié (Run 2 et Run 3).

