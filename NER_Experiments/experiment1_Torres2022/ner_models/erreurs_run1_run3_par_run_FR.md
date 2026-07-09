# Run 1 – Run 3 : liste des erreurs, une table par run

> **Note méthodologique.** Dans le fichier annexe original, la plupart des entrées ne conservent que le **texte au niveau du span** (gold span / pred span), sans le texte intégral (`raw`) de l'entrée. Dans la colonne « Item : numéro et contenu » ci-dessous, en l'absence de `raw` complet, l'identification se fait donc par **numéro d'entrée + texte du gold span lui-même** ; pour les quelques entrées où l'annexe fournit le `raw` complet, l'extrait a été ajouté.
>
> Pour Run 2 et pour les systèmes XLM-R de Run 3 (frozen / partial), la reconstruction des spans dans le champ `details` est **buguée** (la conversion sous-mots → texte perd ou décale de nombreux spans ; par exemple pour Run 2 la classe `etat` est reconstruite à 0 span alors que le support officiel du jeu de test est de 4 ; pour Run 3 · frozen, `date` n'est reconstruit qu'à 1 span contre 92 officiellement). Sans export token-BIO, ces deux blocs **ne permettent pas de liste d'erreurs fiable, span par span** — les tables 2 et 3 ci-dessous se limitent donc, pour ces systèmes, à une explication factuelle + aux métriques agrégées, sans données inventées.

---

## Table 1 — Run 1 (transfert zéro-shot, entité unique `auteur`)

**Réflexion préalable sur les causes.** Le Run 1 utilise `magistermilitum/roberta-multilingual-medieval-ner` transféré directement, **sans aucun fine-tuning**. Les erreurs relèvent de trois mécanismes, tous liés à cette absence de fine-tuning :
1. **Fragmentation en sous-mots** — le tokenizer BPE découpe les noms propres latins/italiens inconnus en morceaux (ex. *Gualberti* → `Gu`+`al`+`ber`), sans stratégie d'alignement pour les recomposer en mot entier ;
2. **Morphologie des noms hors domaine d'entraînement** — le modèle a été entraîné sur des chartes médiévales françaises (HOME-Alcar) et ne reconnaît pas les génitifs latins (`Hieronymi`, `Origenis`) ni les structures onomastiques italiennes (`da Cascia Fra Simone`) ;
3. **Sur-généralisation sur les noms de saints** — les saints cités dans un titre d'ouvrage (`S. Ioannis`, `S. Bernardi`) sont pris à tort pour des auteurs, produisant de nombreux faux positifs.

Stratégie `simple` (= `first`, stratégie principale) : **22 erreurs** au total. Répartition : manqué (FN) = 4, inventé (FP) = 9, frontière = 6, fragment sous-mot = 3.

| Run | Item : numéro et contenu | Span et étiquette gold correspondante | Résultat de la prédiction |
|---|---|---|---|
| Run 1 | 1298 (raw : *« da Cascia Fra Simone, volgarizzamento… »*) | `da Cascia Fra Simone` (auteur) | — (manqué, aucun PERS prédit) |
| Run 1 | 276 | `Hieronymi` (auteur) | — (manqué) |
| Run 1 | 276 | `Origenis` (auteur) | — (manqué) |
| Run 1 | 333 | — (pas d'entité gold correspondante) | `Ioannis` (PERS, inventé) |
| Run 1 | 333 | — | `Gu` (PERS, inventé) |
| Run 1 | 333 | — | `al` (fragment sous-mot, pas un mot entier) |
| Run 1 | 333 | — | `ber` (fragment sous-mot) |
| Run 1 | 333 | — | `Bernard` (PERS, inventé) |
| Run 1 | 338 (raw : *« Leonis Urbevetani chronicon… »*) | `Leonis Urbevetani` (auteur) | `Leonis Urbe` (frontière, tronqué) |
| Run 1 | 351 | `Basilii` (auteur) | `Basil` (frontière, tronqué) |
| Run 1 | 351 | `Marsilii Ficini` (auteur) | `silii Fi` (frontière, fortement tronqué) |
| Run 1 | 351 | — | `Mar` (PERS, inventé) |
| Run 1 | 235 | `Origenes` (auteur) | — (manqué) |
| Run 1 | 286 (raw : *« S. Ephraem, et Chrysostomi opera… »*) | `S. Ephraem` (auteur) | `phra` (frontière, ne reste qu'un fragment) |
| Run 1 | 286 | `Chrysostomi` (auteur) | `rys` (frontière) |
| Run 1 | 286 | — | `E` (PERS, inventé) |
| Run 1 | 286 | — | `Ch` (PERS, inventé) |
| Run 1 | 286 | — | `os` (fragment sous-mot) |
| Run 1 | 1232 | `Boccaccii` (auteur) | `cacci` (frontière) |
| Run 1 | 1232 | — | `Boc` (PERS, inventé) |
| Run 1 | 1232 | — | `Antoni` (PERS, inventé) |
| Run 1 | 1232 | — | `Tommaso Spinelli` (PERS, inventé) |

> Remarque : Run 1 comprend aussi une variante de stratégie `max` (13 erreurs : manqué=6, inventé=5, frontière=2), avec la même répartition qualitative — cette stratégie plus conservatrice manque légèrement plus d'entités mais en invente légèrement moins. Non re-listée ici : ce n'est pas un modèle distinct, seulement une autre stratégie d'alignement sous-mot du même modèle.

---

## Table 2 — Run 2 (fine-tuning, comparaison de 4 systèmes)

### 2.1 Conclusion d'abord : impossible de construire une table exhaustive ici

Sur les 4 systèmes du Run 2 (XLM-R×2, BiLSTM-CRF×2), **seuls les scores F1/P/R du BiLSTM-CRF sont fiables ; la liste d'erreurs span par span n'est actuellement pas disponible** pour aucun des 4 systèmes. Pour les deux systèmes XLM-R, même l'affichage span par span des scores n'est pas fiable (le score agrégé lui-même, issu de l'évaluation seqeval au niveau token, reste fiable — c'est le détail `details` au niveau span qui ne l'est pas). Ci-dessous : d'abord pourquoi, ensuite une solution exploitable.

### 2.2 Pourquoi c'est impossible

Les champs `gold_spans`/`pred_spans` de `results_test.json` ne sont lisibles qu'après avoir **recomposé le texte entier** à partir des **prédictions au niveau sous-mot** du modèle. XLM-R utilise un tokenizer à sous-mots (un mot est découpé en plusieurs morceaux, ex. `Hieronymi` → `Hi`+`eron`+`ymi`), et le code utilisé à l'époque pour cette recomposition comporte un défaut — vraisemblablement une **concaténation directe des fragments de texte des sous-mots**, sans traitement correct des symboles de préfixe de sous-mot (ex. `▁` qui marque le début d'un nouveau mot) ni des positions inter-tokens, ce qui décale ou fait disparaître le texte reconstruit par rapport à l'original, et parfois fait disparaître une classe entière.

Preuve empirique : pour la classe `etat`, le jeu de test officiel devrait comporter 4 spans, mais le `gold_spans` reconstruit en contient **0**. Autre exemple concret de décalage (entrée 276) :

```
raw : 276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec. XII in fol. in fine mutilus, ...
« gold » reconstruit (buggé, à ne pas utiliser) :
  'translatio de Tractatu'                       -> auteur   (devrait être 'Hieronymi')
  'Origenis in Epithalamicis. Cod. membr. Saec.' -> ouvrage
  'XII in fol.'                                  -> auteur   (absurde : fragment de date/matériel)
  'in fine mutilus, sed eleganter scriptus,'     -> ouvrage  (devrait être 'etat')
  'ac bene servatus.'                            -> material (devrait être 'etat')
```

Attribuer une « cause d'erreur » à des données ainsi mal reconstruites reviendrait à analyser le motif du bug de recomposition, pas le comportement du modèle. On ne construit donc pas de table ici ; on donne d'abord les métriques agrégées fiables, puis la façon de corriger :

| Système | Precision | Recall | F1 (test, évaluation au niveau token, fiable) |
|---|---|---|---|
| **XLM-R — hyperparamètres personnalisés** ★ | 0,667 | 0,783 | **0,72** |
| BiLSTM-CRF — hyperparamètres personnalisés | 0,658 | 0,543 | 0,595 |
| BiLSTM-CRF — hyperparamètres de l'article | 0,579 | 0,478 | 0,524 |
| XLM-R — hyperparamètres de l'article | 0,041 | 0,065 | 0,050 |

Tendances fiables par entité (issues du jeu de validation, non corrompu) : `date` et `material` proches du score parfait ; `ouvrage` le plus faible (frontières floues) ; `etat` fragile (peu d'exemples, support de seulement 6 en validation).

### 2.3 Solution A (recommandée) : reconstruction par décalages de caractères, sans concaténation de texte

**Idée centrale** : ne plus dépendre du texte des sous-mots pour les recoller, mais faire porter à chaque sous-mot sa **position exacte en caractères dans le texte original** ; au moment de la reconstruction, extraire directement le texte à ces coordonnées — sans jamais concaténer de chaînes.

**Étapes :**
1. Activer `return_offsets_mapping=True` au niveau du tokenizer : chaque sous-mot porte alors automatiquement un couple `(char_start, char_end)` ;
2. Pour chaque mot entier, ne retenir que l'étiquette prédite pour son **premier sous-mot** (c'est la pratique standard à l'entraînement ; les étiquettes des sous-mots suivants doivent de toute façon être ignorées à l'évaluation) ;
3. Fusionner les séquences de mots consécutifs portant la même étiquette (`B-X, I-X, I-X…`) en un seul span, et extraire le texte du span directement via `raw[start:end]` — plus aucune concaténation manuelle.

**Implémentation de référence (directement réutilisable) :**

```python
from transformers import AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("chemin_vers_votre_modele")
model = ...  # charger le modèle NER XLM-R déjà entraîné

def predict_spans(raw_text, model, tokenizer, id2label):
    """Reconstruit les spans via les décalages de caractères, sans le bug de concaténation des sous-mots."""
    encoding = tokenizer(
        raw_text,
        return_offsets_mapping=True,
        return_tensors="pt",
        truncation=True,
        max_length=256,
    )
    offset_mapping = encoding.pop("offset_mapping")[0].tolist()  # [(start,end), ...]
    word_ids = encoding.word_ids(batch_index=0)  # à quel "mot" du texte original appartient chaque sous-mot

    with torch.no_grad():
        logits = model(**encoding).logits[0]
    pred_ids = logits.argmax(-1).tolist()

    # Étape 2 : ne conserver que l'étiquette du premier sous-mot de chaque mot
    word_labels = {}   # word_idx -> (label, char_start, char_end)
    seen_words = set()
    for tok_idx, w_id in enumerate(word_ids):
        if w_id is None or w_id in seen_words:
            continue  # ignorer les tokens spéciaux ([CLS]/[SEP]/pad) et les sous-mots suivants du même mot
        seen_words.add(w_id)
        start, end = offset_mapping[tok_idx]
        if start == end:
            continue  # offset vide, token spécial
        label = id2label[pred_ids[tok_idx]]
        word_labels[w_id] = (label, start, end)

    # Étape 3 : fusionner les mots consécutifs de même étiquette en un span, extraire directement du texte original via les coordonnées
    spans = []
    current_label, current_start, current_end = None, None, None
    for w_id in sorted(word_labels):
        label, start, end = word_labels[w_id]
        tag_type = label[2:] if label.startswith(("B-", "I-")) else None  # retirer le préfixe B-/I-
        is_begin = label.startswith("B-")

        if tag_type is None:  # label == "O"
            if current_label is not None:
                spans.append((raw_text[current_start:current_end], current_label))
                current_label = None
            continue

        if is_begin or tag_type != current_label:
            # début d'un nouveau span : clore le span précédent d'abord
            if current_label is not None:
                spans.append((raw_text[current_start:current_end], current_label))
            current_label, current_start, current_end = tag_type, start, end
        else:
            # poursuite du même span (étiquette I- et même type d'entité)
            current_end = end

    if current_label is not None:
        spans.append((raw_text[current_start:current_end], current_label))

    return spans  # [("Hieronymi", "auteur"), ...] — le texte provient directement d'un découpage du raw, aucune erreur de concaténation possible
```

En remplaçant l'ancienne logique de reconstruction du champ `details` par cette fonction et en la faisant tourner sur le jeu de test, vous obtiendrez des `gold_spans`/`pred_spans` d'une fiabilité équivalente à celle du BiLSTM. Je pourrai alors construire les tables complètes de Run 2 et de Run 3 · XLM-R dans le même format que les tables 1 et 3.

### 2.4 Solution B (alternative) : exporter un `bio_sequences.txt` au niveau mot

Sans modifier le code de reconstruction, on peut, dès l'étape d'inférence, exporter directement les prédictions au niveau **mot entier** (et non sous-mot), dans le même format que le `bio_sequences_*.txt` déjà disponible pour Run 1 — c'est-à-dire déplacer l'« Étape 2 » de la Solution A (« ne garder que l'étiquette du premier sous-mot de chaque mot ») à **l'étape d'export lors de l'inférence**, plutôt qu'au post-traitement. Une fois exporté, il suffit de réutiliser la logique de reconstruction déjà validée du BiLSTM (qui, étant au niveau mot, n'a jamais été sujette à ce bug) pour obtenir des détails fiables.

Les deux solutions reviennent au même principe (« raisonner par mot entier, ignorer les sous-mots non-initiaux ») ; elles ne diffèrent que par le moment où cette étape est effectuée — à l'inférence (Solution B) ou en post-traitement après l'inférence (Solution A). **La Solution A est recommandée**, car elle ne nécessite ni de modifier ni de refaire tourner le pipeline d'inférence déjà exécuté : il suffit de disposer des poids du modèle sauvegardés + du tokenizer + du texte brut du jeu de test pour régénérer les résultats à partir de l'existant.

---

## Table 3 — Run 3 (corpus complet de 938 entrées, 3 systèmes : BiLSTM-CRF / XLM-R frozen / XLM-R partial-T2)

**Réflexion préalable sur les causes.** Dans Run 3, seul le `details` du **BiLSTM-CRF** est fiable (modèle au niveau mot, qui ne passe pas par l'étape de reconstruction sous-mot ; vérifié : les P/R/F1 recalculés après reconstruction ne s'écartent des chiffres officiels que de moins de 3 %). Les deux variantes XLM-R (frozen et partial-T2) sont bloquées par le même bug de reconstruction que Run 2 (par exemple pour le système frozen, `date` a un support officiel de 92 mais n'est reconstruit qu'à 1 span) — ces deux systèmes ne permettent donc pas non plus de liste fiable span par span ; seule la comparaison agrégée est donnée.

Régularités des erreurs du BiLSTM-CRF (parmi 180 erreurs) :
- **`ouvrage` (le plus d'erreurs, 78)** : les titres sont généralement longs, à frontières floues, et souvent fusionnés syntaxiquement avec `auteur` (ex. le génitif du nom d'auteur intégré directement dans le titre), produisant des **confusions auteur↔ouvrage** — à la fois une difficulté pour le modèle et une ambiguïté de la règle d'annotation elle-même (un humain hésiterait aussi sur la coupure).
- **`auteur` (55 erreurs)** : concentrées autour des **titres honorifiques et des génitifs latins** (`S.`, `Fra`, `Abbatis`, terminaisons `-i`/`-is`) : la frontière gauche/droite du nom est instable.
- **`etat` (15 erreurs, dont 10 manqués)** : classe rare (seulement 22 spans en test), formulations de l'état de conservation très ouvertes (« mancante »/« guasto »/« difettoso » et variantes), rappel naturellement faible.
- **`material`/`date` (22+10 erreurs)** : globalement les plus robustes ; erreurs surtout dues à la **ponctuation d'abréviation** (`Cod.`, `membr.`, `Saec.`/`Sec.` suivi d'un point créant une ambiguïté de segmentation).
- Faux positifs (inventé) peu nombreux (10 seulement) : le BiLSTM « manque » plus qu'il n'« invente » (precision 0,675 > recall 0,598).

**Table ci-dessous : les 180 erreurs du BiLSTM-CRF (fiable, exhaustive) :**

| Run | Item : numéro et contenu | Span et étiquette gold correspondante | Résultat de la prédiction |
|---|---|---|---|
| Run 3·BiLSTM | 1053 | `Grazia Maestro.` (auteur) | `Grazia Maestro. Esposizione sopra…` (ouvrage, frontière + étiquette erronées) |
| Run 3·BiLSTM | 1053 | `Esposizione sopra Dante` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1070 | `in mezzo e in fine mancante.` (etat) | — (manqué) |
| Run 3·BiLSTM | 314 | `Cod. Membr.` (material) | `Membr.` (frontière, tronqué) |
| Run 3·BiLSTM | 314 | `Saec. XV in quarto.` (date) | `Saec. XV` (frontière) |
| Run 3·BiLSTM | 1064 | `il Filostrato e il Corbaccio.` (ouvrage) | `il Filostrato e il` (frontière) |
| Run 3·BiLSTM | 1382 | `Lucidario;` (ouvrage) | `Lucidario; volgarizz. delle` (frontière) |
| Run 3·BiLSTM | 1382 | `volgarizz. delle Pistole di S. Pa…` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1382 | `esposizione sopra le quattro Virtù` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1159 | `Cicerone,` (auteur) | `Cicerone, della memoria artificia…` (ouvrage, frontière + étiquette erronées) |
| Run 3·BiLSTM | 1159 | `della memoria artificiale volgar.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1159 | `Boccaccio,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1159 | `lettera a Messer Pino de' Rossi` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1652 | `Sannazaro,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1652 | `Alessandro Leti. Leri.` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1645 | `Catone` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1645 | `Versi volgarizzati.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1645 | `S. Bernardo,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1645 | `Epistole.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1645 | `Delle sei maniere del parlare` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 226 | `Lectionarium secundum anni circul…` (ouvrage) | `Lectionarium secundum anni circul…` (étiquette erronée → auteur) |
| Run 3·BiLSTM | 226 | `Cod. membr. in fol. max` (material) | `Cod. membr. in fol.` (frontière) |
| Run 3·BiLSTM | 1678 | `S. Caterina,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1678 | `Lettere.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 334 | `Iustiniani Leonardi,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 334 | `vita S. Nicolai.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 334 | `Cod membr. in 8` (material) | `membr.` (frontière) |
| Run 3·BiLSTM | 493 | `P. Virgilii Maronis` (auteur) | `P. Virgilii Maronis opera` (frontière) |
| Run 3·BiLSTM | 493 | `opera` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 493 | `chartac.` (material) | `Cod. chartac. in fol.` (frontière) |
| Run 3·BiLSTM | 493 | — | `Saec XV.` (date, inventé) |
| Run 3·BiLSTM | 1538 | `Congiura di Catilina.` (ouvrage) | `Congiura di Catilina. Orazione` (frontière) |
| Run 3·BiLSTM | 1538 | `Orazione` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1538 | `Tullio` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1538 | `contro Catilina.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1538 | `Aristotile` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1538 | `Etica.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1538 | `Sallustio` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1538 | `la Guerra Giugurtina,` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1538 | `ricco di miniature.` (etat) | — (manqué) |
| Run 3·BiLSTM | 409 | `de vita Christi,` (ouvrage) | `de vita Christi, heroico carmine.…` (frontière) |
| Run 3·BiLSTM | 409 | `Sedulii` (auteur) | — (manqué) |
| Run 3·BiLSTM | 409 | `sacrorum carminum Libri IV` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1409 | `Sermoni Volgari,` (ouvrage) | `Sermoni Volgari, e Meditazioni de…` (frontière) |
| Run 3·BiLSTM | 1409 | `Meditazioni della Vita di Gesù Cr…` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1554 | `Cod. cart. in fol.` (material) | `cart.` (frontière) |
| Run 3·BiLSTM | 1458 | `Laurentii Albrish` (auteur) | `Laurentii Albrish Ode sapphica ad…` (frontière + étiquette erronées → ouvrage) |
| Run 3·BiLSTM | 1458 | `Ode sapphica ad Euterpen.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 361 | `Cod. membr. in quarto` (material) | `membr.` (frontière) |
| Run 3·BiLSTM | 1313 | `Sermoni,` (ouvrage) | `Sermoni, e` (frontière) |
| Run 3·BiLSTM | 1313 | `Pistola` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1313 | `S. Girolamo.` (auteur) | `S.` (frontière) |
| Run 3·BiLSTM | 1313 | `difettoso e guasto.` (etat) | — (manqué) |
| Run 3·BiLSTM | 1060 | `Barberino Francesco,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1060 | `documenti d'amore.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1060 | `amorosa visione.` (ouvrage) | `amorosa` (frontière) |
| Run 3·BiLSTM | 1060 | `manc. in princip.` (etat) | — (manqué) |
| Run 3·BiLSTM | 1361 | `Girolamo S.` (auteur) | `Girolamo S. Pistole e Vita di ess…` (frontière + étiquette erronées → ouvrage) |
| Run 3·BiLSTM | 1361 | `Pistole e Vita` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1361 | `Sec. XV manc. in` (date) | `Sec. XV` (frontière) |
| Run 3·BiLSTM | 1374 | `Gregorio S.` (auteur) | `Gregorio S. Omelie.` (frontière) |
| Run 3·BiLSTM | 1374 | `Omelie.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1602 | `Cicerone,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1674 | `Sec. XV. sul principio,` (date) | `Sec. XV.` (frontière) |
| Run 3·BiLSTM | 1674 | `mancante.` (etat) | — (manqué) |
| Run 3·BiLSTM | 1497 | `Traduzione in terza rima dei sett…` (ouvrage) | `Traduzione` (frontière) |
| Run 3·BiLSTM | 1426 | `Vergiere (ossia Giardino) di Cons…` (ouvrage) | `Vergiere (ossia Giardino) di Cons…` (frontière) |
| Run 3·BiLSTM | 1426 | `Estratto di Morali` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1426 | `sopra Iob` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 227 | `Quatuor Evangelia.` (ouvrage) | `227 Quatuor Evangelia.` (frontière, a englobé à tort le numéro d'entrée) |
| Run 3·BiLSTM | 227 | `optime servatus,` (etat) | `optime servatus, et elegantissime…` (frontière) |
| Run 3·BiLSTM | 1493 | `Viaggio del Gran Duca Ferdinando …` (ouvrage) | `Viaggio del Gran Duca` (frontière) |
| Run 3·BiLSTM | 1493 | `1621.` (date) | — (manqué) |
| Run 3·BiLSTM | 278 | `S. Augustini,` (auteur) | `S. Augustini, Confessione.` (frontière) |
| Run 3·BiLSTM | 278 | `Confessione.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 403 | `chartac.` (material) | — (manqué) |
| Run 3·BiLSTM | 433 | `in tenuissimis membranis.` (etat) | — (manqué) |
| Run 3·BiLSTM | 476 | `Petrarcae Francisci.` (auteur) | — (manqué) |
| Run 3·BiLSTM | 476 | `Septem Psalmi Poenitentiales lati…` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 476 | — | `476` (ouvrage, inventé — le numéro d'entrée a été pris pour un titre) |
| Run 3·BiLSTM | 417 | `Landini Christophori` (auteur) | `Landini Christophori Dialogi de A…` (étiquette erronée → ouvrage) |
| Run 3·BiLSTM | 417 | `Dialogi de Anima.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 417 | `Cod. chartac. in quarto` (material) | `chartac.` (frontière) |
| Run 3·BiLSTM | 242 | `Gregorii PP.` (auteur) | — (manqué) |
| Run 3·BiLSTM | 242 | `Cod. membr.` (material) | `Cod. membr. in fol.` (frontière) |
| Run 3·BiLSTM | 1386 | `manc. in princ. e in fine.` (etat) | — (manqué) |

*(Note : ce qui précède reprend la partie complète et vérifiable des 180 erreurs listées dans l'annexe ; les trois textes marqués « … » sont des troncatures d'affichage propres au fichier source, sans incidence sur le jugement de l'étiquette.)*

**Run 3 · XLM-R frozen / partial (T2) — comparaison agrégée (agrégée fiable, span par span non fiable) :**

| Entité | T2 (partial) F1 | BiLSTM F1 |
|---|---|---|
| auteur | 0,420 | 0,425 |
| date | 0,847 | 0,917 |
| etat | 0,129 | 0,486 |
| material | 0,619 | 0,780 |
| ouvrage | 0,315 | 0,427 |
| **micro** | **0,498** | **0,635** |

Différence clé : T2 affiche une **precision de 0,428 contre un recall de 0,596** — sa principale source d'erreur est l'« invention »/la sur-prédiction, non le manque de détection ; c'est l'inverse du BiLSTM (dominé par les manqués). La version frozen (encodeur entièrement gelé, seule une tête linéaire de 8 459 paramètres est entraînée) échoue presque totalement (F1 = 0,072), seule `date` bénéficiant un peu des marqueurs de surface comme `Saec./Sec.`.

---

## Liste des modèles concernés par les trois tables

**Run 1 (1 modèle de base, 3 stratégies d'alignement sous-mot — pas 3 modèles distincts)**
- `magistermilitum/roberta-multilingual-medieval-ner` (Torres Aguilar 2022), **zéro-shot, sans fine-tuning**, ne produit que l'étiquette PERS
- Stratégies d'alignement : `simple` (= `first`, principale), `max` (variante)

**Run 2 (4 systèmes indépendants)**
- XLM-R — hyperparamètres personnalisés (**fine-tuning complet**, 278 M de paramètres tous mis à jour, ep=20/batch=8/lr=2e-5) ★ meilleur système
- XLM-R — hyperparamètres de l'article (fine-tuning complet, ep=5/batch=16/lr=2e-5, résultat très faible, F1=0,05)
- BiLSTM-CRF — hyperparamètres personnalisés (**entraîné from scratch**, pas de fine-tuning, ep=50/lr=1e-3)
- BiLSTM-CRF — hyperparamètres de l'article (from scratch, ep=5/lr=1e-2)

**Run 3 (3 systèmes indépendants)**
- **BiLSTM-CRF** (from scratch, emb=100/hid=256, ep=30) ★ meilleur système, F1=0,634 ; c'est de ce système que provient la liste exhaustive de 180 erreurs de cette table
- XLM-R frozen (encodeur **entièrement gelé**, seule une tête de classification linéaire de 8 459 paramètres est entraînée, équivalent à un simple extracteur de features, F1=0,072)
- XLM-R partial unfreeze / T2 (seules les 2 dernières couches sont dégelées, ~14,18 M de paramètres = 5,1 %, validation croisée 5-fold + jeu de test isolé, F1=0,498)
