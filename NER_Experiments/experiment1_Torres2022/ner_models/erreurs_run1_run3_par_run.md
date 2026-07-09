# Run 1 – Run 3 : liste des erreurs, une table par run

> **Mise à jour de cette version.** Les tables 1 (Run 1) et 3 (Run 3 · BiLSTM) sont désormais générées de façon programmatique directement à partir des données réelles de votre dépôt GitHub (`LucineZHENG/Stage-2026`) — Run 1 à partir de `prima_run1_zero_shot/prima_run1_v2_pers_refined/test_results_strategies.json`, Run 3 à partir de `prima_run3_full_data/.../bilstm_crf/logs/test_results.json`. Ces deux fichiers contiennent, pour chaque entrée, le champ complet `raw` (le texte intégral de l'entrée du catalogue) ; la colonne « Item : numéro et contenu » reprend maintenant ce texte réel et complet, et non plus une approximation construite en assemblant les spans. La détection des erreurs (manqué / inventé / frontière / confusion) est calculée automatiquement par un script comparant `gold_spans` et `pred_spans` par décalage de caractères — ce n'est plus une compilation manuelle.
>
> Ce calcul programmatique fait passer le total d'erreurs de Run 3 de 180 (chiffre de l'annexe) à 186 (l'écart vient de la façon dont les occurrences répétées d'un même texte sont localisées par le script ; cela n'affecte ni le type ni le contenu des erreurs). Répartition : manqué = 91, frontière = 61, inventé = 16, frontière+label = 13, confusion label = 5 ; par entité : ouvrage 78, auteur 59, material 22, etat 17, date 10.
>
> Pour Run 2 et pour les systèmes XLM-R de Run 3 (frozen / partial), la reconstruction des spans dans le champ `details` reste **buguée** (la conversion sous-mots → texte perd ou décale de nombreux spans ; par exemple pour Run 2 la classe `etat` est reconstruite à 0 span alors que le support officiel du jeu de test est de 4 ; pour Run 3 · frozen, `date` n'est reconstruit qu'à 1 span contre 92 officiellement). Sans export token-BIO, ce bloc **ne permet pas de liste d'erreurs fiable, span par span** — la table 2 ci-dessous s'en tient donc, pour ces systèmes, à une explication factuelle + aux métriques agrégées + une solution de correction (cette partie n'a pas été modifiée).

---

## Table 1 — Run 1 (transfert zéro-shot, entité unique `auteur`)

**Réflexion préalable sur les causes.** Le Run 1 utilise `magistermilitum/roberta-multilingual-medieval-ner` transféré directement, **sans aucun fine-tuning**. Les erreurs relèvent de trois mécanismes, tous liés à cette absence de fine-tuning :
1. **Fragmentation en sous-mots** — le tokenizer BPE découpe les noms propres latins/italiens inconnus en morceaux (ex. *Gualberti* → `Gu`+`al`+`ber`), sans stratégie d'alignement pour les recomposer en mot entier ;
2. **Morphologie des noms hors domaine d'entraînement** — le modèle a été entraîné sur des chartes médiévales françaises (HOME-Alcar) et ne reconnaît pas les génitifs latins (`Hieronymi`, `Origenis`) ni les structures onomastiques italiennes (`da Cascia Fra Simone`) ;
3. **Sur-généralisation sur les noms de saints** — les saints cités dans un titre d'ouvrage (`S. Ioannis`, `S. Bernardi`) sont pris à tort pour des auteurs, produisant de nombreux faux positifs.

Stratégie `simple` (= `first`, stratégie principale) : **22 erreurs** au total. Répartition : manqué (FN) = 4, inventé (FP) = 12 (dont 3 fragments sous-mots de ≤3 caractères : `al`/`ber`/`os`), frontière = 6.

| Run | Item : numéro et contenu (raw) | Span et étiquette gold correspondante | Résultat de la prédiction |
|---|---|---|---|
| Run 1 | 1298 : 1298 da Cascia Fra Simone, volgarizzamento ed Esposizione dei Vangeli. Cod. cart. fol. Sec. XV sul princ. | `da Cascia Fra Simone` (auteur) | — (manqué) |
| Run 1 | 276 : 276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec. XII in fol. in fine mutilus, sed eleganter scriptus, ac bene servatus. | `Hieronymi` (auteur) | — (manqué) |
| Run 1 | 276 : 276 Hieronymi translatio de Tractatu Origenis in Epithalamicis. Cod. membr. Saec. XII in fol. in fine mutilus, sed eleganter scriptus, ac bene servatus. | `Origenis` (auteur) | — (manqué) |
| Run 1 | 333 : 333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV. | — (pas d'entité gold) | `Ioannis` (PERS) — inventé (FP) |
| Run 1 | 333 : 333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV. | — (pas d'entité gold) | `Gu` (PERS) — inventé (FP) |
| Run 1 | 333 : 333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV. | — (pas d'entité gold) | `al` (PERS) — inventé (FP) |
| Run 1 | 333 : 333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV. | — (pas d'entité gold) | `ber` (PERS) — inventé (FP) |
| Run 1 | 333 : 333 Vitae S. Ioannis Gualberti Abbatis, S. Bernardi et aliorum. Cod. membr. in. 8. Saec. XV. | — (pas d'entité gold) | `Bernard` (PERS) — inventé (FP) |
| Run 1 | 338 : 338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV. | `Leonis Urbevetani` (auteur) | `Leonis Urbe` (PERS) — frontière |
| Run 1 | 351 : 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod. chart. in quarto Saec. XV. | `Basilii` (auteur) | `Basil` (PERS) — frontière |
| Run 1 | 351 : 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod. chart. in quarto Saec. XV. | `Marsilii Ficini` (auteur) | `silii Fi` (PERS) — frontière |
| Run 1 | 351 : 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod. chart. in quarto Saec. XV. | — (pas d'entité gold) | `Mar` (PERS) — inventé (FP) |
| Run 1 | 235 : 235 Origenes, super vetus Testamentum. Cod. membr. in fol. Saec. XV in fine mutilus. | `Origenes` (auteur) | — (manqué) |
| Run 1 | 286 : 286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mutilus in principio | `S. Ephraem` (auteur) | `phra` (PERS) — frontière |
| Run 1 | 286 : 286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mutilus in principio | `Chrysostomi` (auteur) | `rys` (PERS) — frontière |
| Run 1 | 286 : 286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mutilus in principio | — (pas d'entité gold) | `E` (PERS) — inventé (FP) |
| Run 1 | 286 : 286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mutilus in principio | — (pas d'entité gold) | `Ch` (PERS) — inventé (FP) |
| Run 1 | 286 : 286 S. Ephraem, et Chrysostomi opera quaedam. Cod. chart. in quarto Saec. XV Aggiunte: mutilus in principio | — (pas d'entité gold) | `os` (PERS) — inventé (FP) |
| Run 1 | 1232 : 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa a Tommaso Spinelli. In cornice. | `Boccaccii` (auteur) | `cacci` (PERS) — frontière |
| Run 1 | 1232 : 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa a Tommaso Spinelli. In cornice. | — (pas d'entité gold) | `Boc` (PERS) — inventé (FP) |
| Run 1 | 1232 : 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa a Tommaso Spinelli. In cornice. | — (pas d'entité gold) | `Antoni` (PERS) — inventé (FP) |
| Run 1 | 1232 : 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa a Tommaso Spinelli. In cornice. | — (pas d'entité gold) | `Tommaso Spinelli` (PERS) — inventé (FP) |

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

Régularités des erreurs du BiLSTM-CRF (parmi 186 erreurs, comptage programmatique) :
- **`ouvrage` (le plus d'erreurs, 78)** : les titres sont généralement longs, à frontières floues, et souvent fusionnés syntaxiquement avec `auteur` (ex. le génitif du nom d'auteur intégré directement dans le titre), produisant des **confusions auteur↔ouvrage** — à la fois une difficulté pour le modèle et une ambiguïté de la règle d'annotation elle-même (un humain hésiterait aussi sur la coupure).
- **`auteur` (59 erreurs)** : concentrées autour des **titres honorifiques et des génitifs latins** (`S.`, `Fra`, `Abbatis`, terminaisons `-i`/`-is`) : la frontière gauche/droite du nom est instable.
- **`etat` (17 erreurs, majoritairement des manqués)** : classe rare (seulement 22 spans en test), formulations de l'état de conservation très ouvertes (« mancante »/« guasto »/« difettoso » et variantes), rappel naturellement faible.
- **`material` (22 erreurs) / `date` (10 erreurs)** : globalement les plus robustes ; erreurs surtout dues à la **ponctuation d'abréviation** (`Cod.`, `membr.`, `Saec.`/`Sec.` suivi d'un point créant une ambiguïté de segmentation).
- Faux positifs (inventé) modérés (16) : le BiLSTM « manque » globalement plus qu'il n'« invente » (precision 0,675 > recall 0,598, chiffres officiels seqeval).

**Table ci-dessous : les 186 erreurs du BiLSTM-CRF (calculées par comparaison programmatique de `gold_spans`/`pred_spans`, fiable, exhaustive — la colonne Item contient le texte `raw` complet de l'entrée) :**

| Run | Item : numéro et contenu (raw) | Span et étiquette gold correspondante | Résultat de la prédiction |
|---|---|---|---|
| Run 3·BiLSTM | 1053 : 1053 Grazia Maestro. Esposizione sopra Dante Cod. cartac. in fol. Sec. XV. Aggiunte: è del Boccaccio | `Grazia Maestro.` (auteur) | `Grazia Maestro. Esposizione sopra Dante` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1053 : 1053 Grazia Maestro. Esposizione sopra Dante Cod. cartac. in fol. Sec. XV. Aggiunte: è del Boccaccio | `Esposizione sopra Dante` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1070 : 1070 Boccaccio, Corbaccio, e vita di Dante. Cod. cart. in fol. Sec. XV in mezzo e in fine mancante. | `in mezzo e in fine mancante.` (etat) | — (manqué) |
| Run 3·BiLSTM | 314 : 314 Constitutiones hospitalis domus Dei Flor. Cod. Membr. Saec. XV in quarto. | `Cod. Membr.` (material) | `Membr.` (material) — frontière |
| Run 3·BiLSTM | 314 : 314 Constitutiones hospitalis domus Dei Flor. Cod. Membr. Saec. XV in quarto. | `Saec. XV in quarto.` (date) | `Saec. XV` (date) — frontière |
| Run 3·BiLSTM | 1064 : 1064 Boccaccio, il Filostrato e il Corbaccio. Cod. cart. Sec. XV. | `il Filostrato e il Corbaccio.` (ouvrage) | `il Filostrato e il` (ouvrage) — frontière |
| Run 3·BiLSTM | 1382 : 1382 Lucidario; volgarizz. delle Pistole di S. Paolo; esposizione sopra le quattro Virtù estratte da Valerio Massimo ec. Cod. cart. in fol. Sec. XV. | `Lucidario;` (ouvrage) | `Lucidario; volgarizz. delle` (ouvrage) — frontière |
| Run 3·BiLSTM | 1382 : 1382 Lucidario; volgarizz. delle Pistole di S. Paolo; esposizione sopra le quattro Virtù estratte da Valerio Massimo ec. Cod. cart. in fol. Sec. XV. | `volgarizz. delle Pistole di S. Paolo;` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1382 : 1382 Lucidario; volgarizz. delle Pistole di S. Paolo; esposizione sopra le quattro Virtù estratte da Valerio Massimo ec. Cod. cart. in fol. Sec. XV. | `esposizione sopra le quattro Virtù` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1159 : 1159 Cicerone, della memoria artificiale volgar. Boccaccio, lettera a Messer Pino de’ Rossi ec. Cod. cartac. in quarto Sec. XV. | `Cicerone,` (auteur) | `Cicerone, della memoria artificiale` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1159 : 1159 Cicerone, della memoria artificiale volgar. Boccaccio, lettera a Messer Pino de’ Rossi ec. Cod. cartac. in quarto Sec. XV. | `della memoria artificiale volgar.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1159 : 1159 Cicerone, della memoria artificiale volgar. Boccaccio, lettera a Messer Pino de’ Rossi ec. Cod. cartac. in quarto Sec. XV. | `Boccaccio,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1159 : 1159 Cicerone, della memoria artificiale volgar. Boccaccio, lettera a Messer Pino de’ Rossi ec. Cod. cartac. in quarto Sec. XV. | `lettera a Messer Pino de’ Rossi` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1652 : 1652 Sannazaro, il Parto della Vergine, tradotto in versi Toscani da Alessandro Leti. Leri. Cod. cart. in fol. Sec. XVIII. | `Sannazaro,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1652 : 1652 Sannazaro, il Parto della Vergine, tradotto in versi Toscani da Alessandro Leti. Leri. Cod. cart. in fol. Sec. XVIII. | `Alessandro Leti. Leri.` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1645 : 1645 Catone Versi volgarizzati. S. Bernardo, Epistole. Delle sei maniere del parlare d’Albertano da Brescia, ossia Trattato Terzo &c. Cod. cart. in fol. Sec. XV. | `Catone` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1645 : 1645 Catone Versi volgarizzati. S. Bernardo, Epistole. Delle sei maniere del parlare d’Albertano da Brescia, ossia Trattato Terzo &c. Cod. cart. in fol. Sec. XV. | `Versi volgarizzati.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1645 : 1645 Catone Versi volgarizzati. S. Bernardo, Epistole. Delle sei maniere del parlare d’Albertano da Brescia, ossia Trattato Terzo &c. Cod. cart. in fol. Sec. XV. | `S. Bernardo,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1645 : 1645 Catone Versi volgarizzati. S. Bernardo, Epistole. Delle sei maniere del parlare d’Albertano da Brescia, ossia Trattato Terzo &c. Cod. cart. in fol. Sec. XV. | `Epistole.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1645 : 1645 Catone Versi volgarizzati. S. Bernardo, Epistole. Delle sei maniere del parlare d’Albertano da Brescia, ossia Trattato Terzo &c. Cod. cart. in fol. Sec. XV. | `Delle sei maniere del parlare` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 226 : 226 Lectionarium secundum anni circulum. Cod. membr. in fol. max Saec. XI in fine mutilus. | `Lectionarium secundum anni circulum.` (ouvrage) | `Lectionarium secundum anni circulum.` (auteur) — confusion label |
| Run 3·BiLSTM | 226 : 226 Lectionarium secundum anni circulum. Cod. membr. in fol. max Saec. XI in fine mutilus. | `Cod. membr. in fol. max` (material) | `Cod. membr. in fol.` (material) — frontière |
| Run 3·BiLSTM | 1678 : 1678 S. Caterina, Lettere. Cod. membr. in fol. Sec. XV. mancante in fine. | `S. Caterina,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1678 : 1678 S. Caterina, Lettere. Cod. membr. in fol. Sec. XV. mancante in fine. | `Lettere.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 334 : 334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV. | `Iustiniani Leonardi,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 334 : 334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV. | `vita S. Nicolai.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 334 : 334 Iustiniani Leonardi, vita S. Nicolai. Cod membr. in 8 Saec. XV. | `Cod membr. in 8` (material) | `membr.` (material) — frontière |
| Run 3·BiLSTM | 493 : 493 P. Virgilii Maronis opera Cod. chartac. in fol. Saec XV. | `P. Virgilii Maronis` (auteur) | `P. Virgilii Maronis opera` (auteur) — frontière |
| Run 3·BiLSTM | 493 : 493 P. Virgilii Maronis opera Cod. chartac. in fol. Saec XV. | `opera` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 493 : 493 P. Virgilii Maronis opera Cod. chartac. in fol. Saec XV. | `chartac.` (material) | `Cod. chartac. in fol.` (material) — frontière |
| Run 3·BiLSTM | 493 : 493 P. Virgilii Maronis opera Cod. chartac. in fol. Saec XV. | — (pas d'entité gold) | `Saec XV.` (date) — inventé (FP) |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `Congiura di Catilina.` (ouvrage) | `Congiura di Catilina. Orazione` (ouvrage) — frontière |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `Orazione` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `Tullio` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `contro Catilina.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `Aristotile` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `Etica.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `Sallustio` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `la Guerra Giugurtina,` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1538 : 1538 Congiura di Catilina. Orazione di Tullio contro Catilina. Aristotile Etica. Epistole varie Canoniche. Evangelio di S. Matteo. Albertano. Lettere varie. Sallustio la Guerra Giugurtina, e molte altre cose di sommo pregio. Cod. membran. in fol. Sec. XV. sul principio ricco di miniature. | `ricco di miniature.` (etat) | — (manqué) |
| Run 3·BiLSTM | 409 : 409 Juvencii de vita Christi, heroico carmine. Sedulii sacrorum carminum Libri IV Codex membr. in quarto Saec. XV. | `de vita Christi,` (ouvrage) | `de vita Christi, heroico carmine. Sedulii sacrorum carminum Libri` (ouvrage) — frontière |
| Run 3·BiLSTM | 409 : 409 Juvencii de vita Christi, heroico carmine. Sedulii sacrorum carminum Libri IV Codex membr. in quarto Saec. XV. | `Sedulii` (auteur) | — (manqué) |
| Run 3·BiLSTM | 409 : 409 Juvencii de vita Christi, heroico carmine. Sedulii sacrorum carminum Libri IV Codex membr. in quarto Saec. XV. | `sacrorum carminum Libri IV` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1409 : 1409 S. Agostino Sermoni Volgari, e Meditazioni della Vita di Gesù Cristo. Cod. cartac. in quarto Sec. XV. | `Sermoni Volgari,` (ouvrage) | `Sermoni Volgari, e Meditazioni della Vita di Gesù Cristo.` (ouvrage) — frontière |
| Run 3·BiLSTM | 1409 : 1409 S. Agostino Sermoni Volgari, e Meditazioni della Vita di Gesù Cristo. Cod. cartac. in quarto Sec. XV. | `Meditazioni della Vita di Gesù Cristo.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1554 : 1554 T. Livio, la prima Deca volgarizzata. Cod. cart. in fol. Sec XIV. | `Cod. cart. in fol.` (material) | `cart.` (material) — frontière |
| Run 3·BiLSTM | 1458 : 1458 Laurentii Albrish Ode sapphica ad Euterpen. Cod. membr. in octavo Saec. XV. | `Laurentii Albrish` (auteur) | `Laurentii Albrish Ode sapphica ad Euterpen.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1458 : 1458 Laurentii Albrish Ode sapphica ad Euterpen. Cod. membr. in octavo Saec. XV. | `Ode sapphica ad Euterpen.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 361 : 361 Carmina ad Callistum III. Cod. membr. in quarto Saec. XV. | `Cod. membr. in quarto` (material) | `membr.` (material) — frontière |
| Run 3·BiLSTM | 1313 : 1313 S. Agostino Sermoni, e Pistola di S. Girolamo. Cod. cart. in fol. Sec. XV difettoso e guasto. | `Sermoni,` (ouvrage) | `Sermoni, e` (ouvrage) — frontière |
| Run 3·BiLSTM | 1313 : 1313 S. Agostino Sermoni, e Pistola di S. Girolamo. Cod. cart. in fol. Sec. XV difettoso e guasto. | `Pistola` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1313 : 1313 S. Agostino Sermoni, e Pistola di S. Girolamo. Cod. cart. in fol. Sec. XV difettoso e guasto. | `S. Girolamo.` (auteur) | `S.` (auteur) — frontière |
| Run 3·BiLSTM | 1313 : 1313 S. Agostino Sermoni, e Pistola di S. Girolamo. Cod. cart. in fol. Sec. XV difettoso e guasto. | `difettoso e guasto.` (etat) | — (manqué) |
| Run 3·BiLSTM | 1060 : 1060 Barberino Francesco, documenti d’ amore. Boccaccio, amorosa visione. Cod cart. in fol. sec. XV sul princip. manc. in princip. Aggiunte: e non è vero | `Barberino Francesco,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1060 : 1060 Barberino Francesco, documenti d’ amore. Boccaccio, amorosa visione. Cod cart. in fol. sec. XV sul princip. manc. in princip. Aggiunte: e non è vero | `documenti d’ amore.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1060 : 1060 Barberino Francesco, documenti d’ amore. Boccaccio, amorosa visione. Cod cart. in fol. sec. XV sul princip. manc. in princip. Aggiunte: e non è vero | `amorosa visione.` (ouvrage) | `amorosa` (ouvrage) — frontière |
| Run 3·BiLSTM | 1060 : 1060 Barberino Francesco, documenti d’ amore. Boccaccio, amorosa visione. Cod cart. in fol. sec. XV sul princip. manc. in princip. Aggiunte: e non è vero | `manc. in princip.` (etat) | — (manqué) |
| Run 3·BiLSTM | 1361 : 1361 Girolamo S. Pistole e Vita di esso. Cod. cart. in fol. Sec. XV manc. in princ. | `Girolamo S.` (auteur) | `Girolamo S. Pistole e Vita di esso.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1361 : 1361 Girolamo S. Pistole e Vita di esso. Cod. cart. in fol. Sec. XV manc. in princ. | `Pistole e Vita` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1361 : 1361 Girolamo S. Pistole e Vita di esso. Cod. cart. in fol. Sec. XV manc. in princ. | `Sec. XV manc. in` (date) | `Sec. XV` (date) — frontière |
| Run 3·BiLSTM | 1374 : 1374 Gregorio S. Omelie. Cod cart. in fol. Sec. XV sul princ. | `Gregorio S.` (auteur) | `Gregorio S. Omelie.` (auteur) — frontière |
| Run 3·BiLSTM | 1374 : 1374 Gregorio S. Omelie. Cod cart. in fol. Sec. XV sul princ. | `Omelie.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1602 : 1602 Cicerone, degli Oficj, volgarizzato. Cod. memb. in quarto Sec. XV. nitidissimo. | `Cicerone,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1602 : 1602 Cicerone, degli Oficj, volgarizzato. Cod. memb. in quarto Sec. XV. nitidissimo. | `degli Oficj,` (ouvrage) | `degli Oficj, volgarizzato.` (ouvrage) — frontière |
| Run 3·BiLSTM | 1602 : 1602 Cicerone, degli Oficj, volgarizzato. Cod. memb. in quarto Sec. XV. nitidissimo. | — (pas d'entité gold) | `nitidissimo.` (etat) — inventé (FP) |
| Run 3·BiLSTM | 499 : 499 Ciceronis Orationes in Verrem. Cod. elegantissimiis membran. Saec. XV fuit Poggii scribae Pontificii. | `membran.` (material) | `Cod. elegantissimiis membran.` (material) — frontière |
| Run 3·BiLSTM | 1280 : 1280 Leggenda di S. Domitilla. Romanzo antico d’incerto Autore Autografo. Cod. cartac. fol. | `Leggenda di S. Domitilla.` (ouvrage) | `Leggenda di S. Domitilla. Romanzo` (ouvrage) — frontière |
| Run 3·BiLSTM | 1280 : 1280 Leggenda di S. Domitilla. Romanzo antico d’incerto Autore Autografo. Cod. cartac. fol. | `Romanzo antico d’incerto Autore` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1280 : 1280 Leggenda di S. Domitilla. Romanzo antico d’incerto Autore Autografo. Cod. cartac. fol. | `cartac.` (material) | `cartac. fol.` (material) — frontière |
| Run 3·BiLSTM | 470 : 470 S. Bonaventurae Dialogus. Cod. chartac in 16. Saec. XV. | `S. Bonaventurae` (auteur) | `S. Bonaventurae Dialogus.` (auteur) — frontière |
| Run 3·BiLSTM | 470 : 470 S. Bonaventurae Dialogus. Cod. chartac in 16. Saec. XV. | `Dialogus.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 470 : 470 S. Bonaventurae Dialogus. Cod. chartac in 16. Saec. XV. | `Cod. chartac in 16.` (material) | `chartac` (material) — frontière |
| Run 3·BiLSTM | 1079 : 1079 Boccaccio e Leonardo Aretino, Vita di Dante. Cod. cart. in fol. Sec. XV. | `Boccaccio` (auteur) | `Boccaccio e` (ouvrage) — confusion label |
| Run 3·BiLSTM | 1079 : 1079 Boccaccio e Leonardo Aretino, Vita di Dante. Cod. cart. in fol. Sec. XV. | — (pas d'entité gold) | `Vita di Dante.` (ouvrage) — inventé (FP) |
| Run 3·BiLSTM | 261 : 261 Exempla SS. Patrum. Conciones Quadragesimales ec. Cod. chart. in fol. Saec. XIV. | `Exempla SS. Patrum.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 261 : 261 Exempla SS. Patrum. Conciones Quadragesimales ec. Cod. chart. in fol. Saec. XIV. | `Conciones Quadragesimales` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1261 : 1261 Bernardo S. Sermoni sulla cantica volgarizzati. Cod. cart. in fol. Sec. XIV. in fine macchiato alquanto dall’acqua. | `in fine macchiato alquanto dall’acqua.` (etat) | — (manqué) |
| Run 3·BiLSTM | 1261 : 1261 Bernardo S. Sermoni sulla cantica volgarizzati. Cod. cart. in fol. Sec. XIV. in fine macchiato alquanto dall’acqua. | — (pas d'entité gold) | `in` (etat) — inventé (FP) |
| Run 3·BiLSTM | 1165 : 1165 Villa nova (Arnoldi de) et alior. Tractatus Alchimiae. Cod. chartac. in fol. Saec. XV. | `Tractatus Alchimiae.` (ouvrage) | `Villa nova (Arnoldi de) et alior. Tractatus Alchimiae.` (ouvrage) — frontière |
| Run 3·BiLSTM | 1576 : 1576 Ovidio, Metamorfosi volgarizzate. Cod. cartac. in fil. Sec. XV. si aggiunge il prima libro delle Stanze del Poliziano. | — (pas d'entité gold) | `Ovidio,` (auteur) — inventé (FP) |
| Run 3·BiLSTM | 1576 : 1576 Ovidio, Metamorfosi volgarizzate. Cod. cartac. in fil. Sec. XV. si aggiunge il prima libro delle Stanze del Poliziano. | — (pas d'entité gold) | `Metamorfosi volgarizzate.` (ouvrage) — inventé (FP) |
| Run 3·BiLSTM | 461 : 461 Officium B. M. Virginis. Cod. membr. In octavo Saec. XV cum picturis. Aggiunte: 461 Manca, vedi nota Rigoli. Sostituito con Pensieri di Mario Pieri, autografo. “Pieri Mario, Miei pensieri, Parti I e II. secolo XIX”. Firmato E. R. | `cum picturis.` (etat) | — (manqué) |
| Run 3·BiLSTM | 1341 : 1341 Vita di Gesù Cristo e di Maria Vergine. Leggenda di S. Cecilia e Margherita. Cod. cartac. in fol. Sec. XIV sul fine mancante in mezzo. | `Vita di Gesù Cristo e di Maria Vergine.` (ouvrage) | `Vita di Gesù Cristo e di Maria` (ouvrage) — frontière |
| Run 3·BiLSTM | 1341 : 1341 Vita di Gesù Cristo e di Maria Vergine. Leggenda di S. Cecilia e Margherita. Cod. cartac. in fol. Sec. XIV sul fine mancante in mezzo. | `Leggenda di S. Cecilia e Margherita.` (ouvrage) | `S.` (auteur) — frontière+label |
| Run 3·BiLSTM | 1341 : 1341 Vita di Gesù Cristo e di Maria Vergine. Leggenda di S. Cecilia e Margherita. Cod. cartac. in fol. Sec. XIV sul fine mancante in mezzo. | — (pas d'entité gold) | `mancante in mezzo.` (etat) — inventé (FP) |
| Run 3·BiLSTM | 1042 : 1042 Convito di Dante. Cod. cart. in fol. Secolo XV. | `Convito` (ouvrage) | `Convito di Dante.` (ouvrage) — frontière |
| Run 3·BiLSTM | 1042 : 1042 Convito di Dante. Cod. cart. in fol. Secolo XV. | `Dante.` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1625 : 1625 S. Agostino, Sermoni volgarizzati da Fra Agostino da Scarperia. Cod. cartac. in quarto Sec. XV | `Sermoni volgarizzati` (ouvrage) | `Sermoni` (ouvrage) — frontière |
| Run 3·BiLSTM | 1625 : 1625 S. Agostino, Sermoni volgarizzati da Fra Agostino da Scarperia. Cod. cartac. in quarto Sec. XV | `Fra Agostino da Scarperia.` (auteur) | `Fra Agostino da` (auteur) — frontière |
| Run 3·BiLSTM | 1232 : 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa a Tommaso Spinelli. In cornice. | `Boccaccii` (auteur) | `Boccaccii Eclogae ad Donatum Apenninigenam.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1232 : 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa a Tommaso Spinelli. In cornice. | `Eclogae ad Donatum Apenninigenam.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1232 : 1232 Boccaccii Eclogae ad Donatum Apenninigenam. Cod. mem. in 8. Saec. XIV. Aggiunte: 1232 bis Antoninus, Lettera autografa a Tommaso Spinelli. In cornice. | `Cod. mem. in 8.` (material) | `mem.` (material) — frontière |
| Run 3·BiLSTM | 1081 : 1081 Boccaccio, Corbaccio. Volgarizzamento dell’epistole d’Ovidio. Cod. cart. in fol Sec. XV. Aggiunte: mutilo | `mutilo` (date) | — (manqué) |
| Run 3·BiLSTM | 338 : 338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV. | `Leonis Urbevetani` (auteur) | `Leonis Urbevetani chronicon et alia.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 338 : 338 Leonis Urbevetani chronicon et alia. Cod. membr. Saec XIV. | `chronicon et alia.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1690 : 1690 Passione di Cristo, come sopra. Cod. car. in quarto Sec. XV. | `Passione di Cristo,` (ouvrage) | `Passione di Cristo, come sopra.` (ouvrage) — frontière |
| Run 3·BiLSTM | 1033 : 1033 Dante la Divina commedia &c. Cod. memb. in fol. con chiose interlineari latine, l’autor delle quali ha posto in fine la data del 1404. Cod. membr. in fol. colla prima pagina rifatta da mano posteriore. | `memb.` (material) | — (manqué) |
| Run 3·BiLSTM | 1033 : 1033 Dante la Divina commedia &c. Cod. memb. in fol. con chiose interlineari latine, l’autor delle quali ha posto in fine la data del 1404. Cod. membr. in fol. colla prima pagina rifatta da mano posteriore. | `1404.` (date) | — (manqué) |
| Run 3·BiLSTM | 1033 : 1033 Dante la Divina commedia &c. Cod. memb. in fol. con chiose interlineari latine, l’autor delle quali ha posto in fine la data del 1404. Cod. membr. in fol. colla prima pagina rifatta da mano posteriore. | — (pas d'entité gold) | `membr.` (material) — inventé (FP) |
| Run 3·BiLSTM | 1527 : 1527 1528 Nardi, Storia Fiorentina. Cod. cart. in fol del Sec. XVI. vol. 2. Originale. | `Nardi,` (auteur) | `1528 Nardi, Storia Fiorentina.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1527 : 1527 1528 Nardi, Storia Fiorentina. Cod. cart. in fol del Sec. XVI. vol. 2. Originale. | `Storia Fiorentina.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1527 : 1527 1528 Nardi, Storia Fiorentina. Cod. cart. in fol del Sec. XVI. vol. 2. Originale. | `Originale.` (etat) | — (manqué) |
| Run 3·BiLSTM | 393 : 393 Idem. | — (pas d'entité gold) | `Idem.` (ouvrage) — inventé (FP) |
| Run 3·BiLSTM | 300 : 300 Missale. Accedunt alia quaedam ad Conciliorum, et Pontificum canones pertinentia. Cod. membr. in quarto Saec. XII in. sed initio mutilus. | `Cod. membr. in quarto` (material) | `membr.` (material) — frontière |
| Run 3·BiLSTM | 300 : 300 Missale. Accedunt alia quaedam ad Conciliorum, et Pontificum canones pertinentia. Cod. membr. in quarto Saec. XII in. sed initio mutilus. | `Saec. XII in.` (date) | `Saec. XII` (date) — frontière |
| Run 3·BiLSTM | 300 : 300 Missale. Accedunt alia quaedam ad Conciliorum, et Pontificum canones pertinentia. Cod. membr. in quarto Saec. XII in. sed initio mutilus. | `sed initio mutilus.` (etat) | `initio mutilus.` (etat) — frontière |
| Run 3·BiLSTM | 1683 : 1683 Fagioli Baccio, del Giudizio finale. Regola morale e ascetica. Cod. cartac. in fol. Sec. XV e XVI. | `Fagioli Baccio,` (auteur) | `Fagioli Baccio, del Giudizio finale. Regola morale e ascetica.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1683 : 1683 Fagioli Baccio, del Giudizio finale. Regola morale e ascetica. Cod. cartac. in fol. Sec. XV e XVI. | `del Giudizio finale. Regola morale e ascetica.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1683 : 1683 Fagioli Baccio, del Giudizio finale. Regola morale e ascetica. Cod. cartac. in fol. Sec. XV e XVI. | `Sec. XV e XVI.` (date) | `Sec. XV` (date) — frontière |
| Run 3·BiLSTM | 1451 : 1451 Hegesippi Epitome Josephi Antiquitatum. Cod. membr. in 12 Saec. XV. | `Hegesippi` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1575 : 1575 Ovidio, Metamorfosi volgarizzate. Cod. cartac. in fol. Sec XV. | — (pas d'entité gold) | `Ovidio,` (auteur) — inventé (FP) |
| Run 3·BiLSTM | 1523 : 1523 Boezio della Consolazione volgarizzato da M. Alberto da Firenze. Cod. membr. in fol. Sec. XV. | `Boezio` (auteur) | `Boezio della Consolazione volgarizzato` (auteur) — frontière |
| Run 3·BiLSTM | 1523 : 1523 Boezio della Consolazione volgarizzato da M. Alberto da Firenze. Cod. membr. in fol. Sec. XV. | `della Consolazione volgarizzato` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1523 : 1523 Boezio della Consolazione volgarizzato da M. Alberto da Firenze. Cod. membr. in fol. Sec. XV. | `M. Alberto da Firenze.` (auteur) | `Alberto da Firenze.` (auteur) — frontière |
| Run 3·BiLSTM | 1523 : 1523 Boezio della Consolazione volgarizzato da M. Alberto da Firenze. Cod. membr. in fol. Sec. XV. | — (pas d'entité gold) | `M.` (auteur) — inventé (FP) |
| Run 3·BiLSTM | 225 : 225 Passionarium Sanctorum. Cod. Membran in fol. Atlantico. Saec. XI nitidissime scriptus | `Cod. Membran in fol. Atlantico.` (material) | `Cod. Membran in fol.` (material) — frontière |
| Run 3·BiLSTM | 1650 : 1650 Sallustio, della Guerra Catilinaria, e Giugurtina, volgarizzato da Fra Bartolommeo da S Concordio &c. Cod. membr. in fol. Sec. XV. | `Sallustio,` (auteur) | `Sallustio, della Guerra Catilinaria, e Giugurtina,` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1650 : 1650 Sallustio, della Guerra Catilinaria, e Giugurtina, volgarizzato da Fra Bartolommeo da S Concordio &c. Cod. membr. in fol. Sec. XV. | `Fra Bartolommeo da S Concordio` (auteur) | `Bartolommeo da` (auteur) — frontière |
| Run 3·BiLSTM | 1650 : 1650 Sallustio, della Guerra Catilinaria, e Giugurtina, volgarizzato da Fra Bartolommeo da S Concordio &c. Cod. membr. in fol. Sec. XV. | — (pas d'entité gold) | `Fra` (auteur) — inventé (FP) |
| Run 3·BiLSTM | 1650 : 1650 Sallustio, della Guerra Catilinaria, e Giugurtina, volgarizzato da Fra Bartolommeo da S Concordio &c. Cod. membr. in fol. Sec. XV. | — (pas d'entité gold) | `S` (auteur) — inventé (FP) |
| Run 3·BiLSTM | 1154 : 1154 Salutati Coluccio, Simoni Sardini da Siena, Francesco Malacarne da Firenze ed altri rimatori antichi poesie diverse. Cod membr. in fol. Sec. XV nitidissimo. | `Salutati Coluccio,` (auteur) | `Salutati Coluccio, Simoni Sardini` (ouvrage) — confusion label |
| Run 3·BiLSTM | 1154 : 1154 Salutati Coluccio, Simoni Sardini da Siena, Francesco Malacarne da Firenze ed altri rimatori antichi poesie diverse. Cod membr. in fol. Sec. XV nitidissimo. | `Simoni Sardini da Siena,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1154 : 1154 Salutati Coluccio, Simoni Sardini da Siena, Francesco Malacarne da Firenze ed altri rimatori antichi poesie diverse. Cod membr. in fol. Sec. XV nitidissimo. | `Francesco Malacarne da Firenze` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1154 : 1154 Salutati Coluccio, Simoni Sardini da Siena, Francesco Malacarne da Firenze ed altri rimatori antichi poesie diverse. Cod membr. in fol. Sec. XV nitidissimo. | `poesie diverse.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1154 : 1154 Salutati Coluccio, Simoni Sardini da Siena, Francesco Malacarne da Firenze ed altri rimatori antichi poesie diverse. Cod membr. in fol. Sec. XV nitidissimo. | `nitidissimo.` (etat) | — (manqué) |
| Run 3·BiLSTM | 399 : 399 Excerpta ex Pererio in Sacram Scripturam. Accedit Tractatus Della Povertà Religiosa. Cod. chart in fol. Saec. XVII. | `Excerpta ex` (ouvrage) | `Excerpta ex Pererio in Sacram` (ouvrage) — frontière |
| Run 3·BiLSTM | 399 : 399 Excerpta ex Pererio in Sacram Scripturam. Accedit Tractatus Della Povertà Religiosa. Cod. chart in fol. Saec. XVII. | `Pererio` (auteur) | — (manqué) |
| Run 3·BiLSTM | 399 : 399 Excerpta ex Pererio in Sacram Scripturam. Accedit Tractatus Della Povertà Religiosa. Cod. chart in fol. Saec. XVII. | `in Sacram Scripturam.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 399 : 399 Excerpta ex Pererio in Sacram Scripturam. Accedit Tractatus Della Povertà Religiosa. Cod. chart in fol. Saec. XVII. | `Tractatus Della Povertà Religiosa.` (ouvrage) | `Della` (ouvrage) — frontière |
| Run 3·BiLSTM | 1686 : 1686 Istruzioni Catechistiche ec. Cod. cartac. in quart. Sec. XV. | `Istruzioni Catechistiche` (ouvrage) | `Istruzioni Catechistiche ec.` (ouvrage) — frontière |
| Run 3·BiLSTM | 1455 : 1455 Basilii S. Oratio ad Religiotos Iuvenes, a Leonardo Arretino translata. Cod. membr. in octavo Saec. XV. in fine mutilus. | `Basilii S.` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1455 : 1455 Basilii S. Oratio ad Religiotos Iuvenes, a Leonardo Arretino translata. Cod. membr. in octavo Saec. XV. in fine mutilus. | `Oratio ad Religiotos Iuvenes,` (ouvrage) | `Oratio ad Religiotos` (ouvrage) — frontière |
| Run 3·BiLSTM | 1455 : 1455 Basilii S. Oratio ad Religiotos Iuvenes, a Leonardo Arretino translata. Cod. membr. in octavo Saec. XV. in fine mutilus. | `Leonardo Arretino` (auteur) | `Leonardo` (auteur) — frontière |
| Run 3·BiLSTM | 1455 : 1455 Basilii S. Oratio ad Religiotos Iuvenes, a Leonardo Arretino translata. Cod. membr. in octavo Saec. XV. in fine mutilus. | `Saec. XV. in` (date) | `Saec. XV.` (date) — frontière |
| Run 3·BiLSTM | 1455 : 1455 Basilii S. Oratio ad Religiotos Iuvenes, a Leonardo Arretino translata. Cod. membr. in octavo Saec. XV. in fine mutilus. | — (pas d'entité gold) | `in fine mutilus.` (etat) — inventé (FP) |
| Run 3·BiLSTM | 1397 : 1397 Revelazioni celestiali. Cod. membr. in fol. Sec. XIV. | `Revelazioni celestiali.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1470 : 1470 Girolamo S. Salterio abbreviato. Cod. membr. in ottavo Sec. XV. | `Girolamo S.` (auteur) | `Girolamo S. Salterio abbreviato.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1470 : 1470 Girolamo S. Salterio abbreviato. Cod. membr. in ottavo Sec. XV. | `Salterio abbreviato.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 371 : 371 Hidelberti Episcopi, Epistolae. Cod. membr. in octavo Saec XII. | `Hidelberti Episcopi,` (auteur) | `Hidelberti Episcopi, Epistolae.` (auteur) — frontière |
| Run 3·BiLSTM | 371 : 371 Hidelberti Episcopi, Epistolae. Cod. membr. in octavo Saec XII. | `Epistolae.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1289 : 1289 Vite di Santi. Cod. cartac. fol. Saec. XIV in fine, mancante in princ. mezzo, e fine. | `cartac.` (ouvrage) | `cartac.` (material) — confusion label |
| Run 3·BiLSTM | 327 : 327 Computus ecclesiasticus &c Cod. membr. in quarto Saec XIV. | `Computus ecclesiasticus` (ouvrage) | `Computus ecclesiasticus &c` (ouvrage) — frontière |
| Run 3·BiLSTM | 1339 : 1339 S. Gregorio Murali Volgarizzaci. Cod. cart. fol. Sec. XV. | `S. Gregorio` (auteur) | `S. Gregorio Murali Volgarizzaci.` (auteur) — frontière |
| Run 3·BiLSTM | 1339 : 1339 S. Gregorio Murali Volgarizzaci. Cod. cart. fol. Sec. XV. | `Murali Volgarizzaci.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1219 : 1219 Dondis de Iohannis, de modo vivendi tempore Pestis. Cod. membr. in quarto Saec. XIV. | `Dondis de Iohannis,` (auteur) | `de Iohannis, de modo vivendi tempore Pestis.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 1219 : 1219 Dondis de Iohannis, de modo vivendi tempore Pestis. Cod. membr. in quarto Saec. XIV. | `de modo vivendi tempore Pestis.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1219 : 1219 Dondis de Iohannis, de modo vivendi tempore Pestis. Cod. membr. in quarto Saec. XIV. | — (pas d'entité gold) | `Dondis` (auteur) — inventé (FP) |
| Run 3·BiLSTM | 397 : 397 Chronica Martiniana.Cod. membr. in quarto Saec. XV Accedit Chronologia Imperatorum usque ad Fridericum II. | `Chronica Martiniana.Cod.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 397 : 397 Chronica Martiniana.Cod. membr. in quarto Saec. XV Accedit Chronologia Imperatorum usque ad Fridericum II. | `membr.` (material) | — (manqué) |
| Run 3·BiLSTM | 351 : 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod. chart. in quarto Saec. XV. | `Basilii,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 351 : 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod. chart. in quarto Saec. XV. | `oratio ad juvenes` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 351 : 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod. chart. in quarto Saec. XV. | `Marsilii Ficini` (auteur) | — (manqué) |
| Run 3·BiLSTM | 351 : 351 Basilii, Sancti, oratio ad juvenes de huma nioribus studii, et Marsilii Ficini de quatuor Sectis philosophorum. Cod. chart. in quarto Saec. XV. | `Cod. chart. in quarto` (material) | `chart.` (material) — frontière |
| Run 3·BiLSTM | 250 : 250 Hieremiae Compendium Moralium. Cod. chart. in fol. Saec. XV. | `Hieremiae` (auteur) | `Hieremiae Compendium Moralium.` (ouvrage) — frontière+label |
| Run 3·BiLSTM | 250 : 250 Hieremiae Compendium Moralium. Cod. chart. in fol. Saec. XV. | `Compendium Moralium.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 250 : 250 Hieremiae Compendium Moralium. Cod. chart. in fol. Saec. XV. | `Cod. chart. in fol.` (material) | `chart.` (material) — frontière |
| Run 3·BiLSTM | 456 : 456 Officium B. M. Virginis, et Mortuorum Cod. membr. in octavo Saec. XV cum picturis. | `Cod. membr. in octavo` (material) | `membr.` (material) — frontière |
| Run 3·BiLSTM | 1127 : 1127 Petrarca, e Dante Rime. Cod. cartac. in quarto Sec. XV. | `Dante` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1127 : 1127 Petrarca, e Dante Rime. Cod. cartac. in quarto Sec. XV. | `Rime.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 503 : 503 Ciceronis Epistolae ad familiares Cod partim membr. partim chartac. Saec. XV. | `Cod partim membr. partim chartac.` (material) | `Cod partim membr. partim` (material) — frontière |
| Run 3·BiLSTM | 1273 : 1273 Meditazioni della Vita di Gesù Cristo. (S. Bonaventura) Cavalca Specchio de’ Peccati. Cod. cart. fol. Sec. XV sul principio. | `Cavalca` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1674 : 1674 Fra Guido, Fiorità d’Italia, ed istorie, e discorsi diversi. Cod. cart. in fol. Sec. XV. sul principio, mancante. | `Fra Guido,` (auteur) | — (manqué) |
| Run 3·BiLSTM | 1674 : 1674 Fra Guido, Fiorità d’Italia, ed istorie, e discorsi diversi. Cod. cart. in fol. Sec. XV. sul principio, mancante. | `Fiorità d’Italia, ed istorie, e discorsi diversi.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1674 : 1674 Fra Guido, Fiorità d’Italia, ed istorie, e discorsi diversi. Cod. cart. in fol. Sec. XV. sul principio, mancante. | `Sec. XV. sul principio,` (date) | `Sec. XV.` (date) — frontière |
| Run 3·BiLSTM | 1674 : 1674 Fra Guido, Fiorità d’Italia, ed istorie, e discorsi diversi. Cod. cart. in fol. Sec. XV. sul principio, mancante. | `mancante.` (etat) | — (manqué) |
| Run 3·BiLSTM | 1497 : 1497 Ciatini, Giovanni, Traduzione in terza rima dei sette Salmi Penitenziali, ed altro. Cod. cart. in ottavo Sec. XVI. | `Traduzione in terza rima dei sette Salmi Penitenziali,` (ouvrage) | `Traduzione` (ouvrage) — frontière |
| Run 3·BiLSTM | 1426 : 1426 Vergiere (ossia Giardino) di Consolazione. Estratto di Morali di S. Gregorio sopra Iob ec. Cod. cartac. in quarto Sec. XV. | `Vergiere (ossia Giardino) di Consolazione.` (ouvrage) | `Vergiere (ossia Giardino) di Consolazione. Estratto di` (ouvrage) — frontière |
| Run 3·BiLSTM | 1426 : 1426 Vergiere (ossia Giardino) di Consolazione. Estratto di Morali di S. Gregorio sopra Iob ec. Cod. cartac. in quarto Sec. XV. | `Estratto di Morali` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 1426 : 1426 Vergiere (ossia Giardino) di Consolazione. Estratto di Morali di S. Gregorio sopra Iob ec. Cod. cartac. in quarto Sec. XV. | `sopra Iob` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 227 : 227 Quatuor Evangelia. Cod. membr. in fol. Saec. XIV optime servatus, et elegantissime exaratus. | `Quatuor Evangelia.` (ouvrage) | `227 Quatuor Evangelia.` (ouvrage) — frontière |
| Run 3·BiLSTM | 227 : 227 Quatuor Evangelia. Cod. membr. in fol. Saec. XIV optime servatus, et elegantissime exaratus. | `optime servatus,` (etat) | `optime servatus, et elegantissime exaratus.` (etat) — frontière |
| Run 3·BiLSTM | 1493 : 1493 Viaggio del Gran Duca Ferdinando I. nel 1621. Cod. cartac. in ottavo di poche pagine. | `Viaggio del Gran Duca Ferdinando I.` (ouvrage) | `Viaggio del Gran Duca` (ouvrage) — frontière |
| Run 3·BiLSTM | 1493 : 1493 Viaggio del Gran Duca Ferdinando I. nel 1621. Cod. cartac. in ottavo di poche pagine. | `1621.` (date) | — (manqué) |
| Run 3·BiLSTM | 278 : 278 S. Augustini, Confessione. Cod. membr. in fol. Saec. XV. | `S. Augustini,` (auteur) | `S. Augustini, Confessione.` (auteur) — frontière |
| Run 3·BiLSTM | 278 : 278 S. Augustini, Confessione. Cod. membr. in fol. Saec. XV. | `Confessione.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 403 : 403 Palatii Ioh. Historia Cardinalium Florentinorum. Accedunt Excerpta ex Tracta u Politic. Ioh. Cavalcanti. Cod: chartac. in fol. Saec. XVIII. | `chartac.` (material) | — (manqué) |
| Run 3·BiLSTM | 433 : 433 Biblia Sacra. Cod. memb. in octavo Saec. XIV in tenuissimis membranis. Aggiunte: 433 Manca; sostituto con Cod. arm. sec. XVI. Grammatica di Giovanni … [sic] cartaceo in 12 (“Prima parla della Grammatica della lingua letter. Armena, ossia ‘forma’ della suddetta lingua. Libretto di D. Giovanni … [sic] di cc. 28). Firmato E. R. | `in tenuissimis membranis.` (etat) | — (manqué) |
| Run 3·BiLSTM | 476 : 476 Petrarcae Francisci. Septem Psalmi Poenitentiales latinis versibus redditi. Cod. membr. in octavo Saec. XV. | `Petrarcae Francisci.` (auteur) | — (manqué) |
| Run 3·BiLSTM | 476 : 476 Petrarcae Francisci. Septem Psalmi Poenitentiales latinis versibus redditi. Cod. membr. in octavo Saec. XV. | `Septem Psalmi Poenitentiales latinis versibus redditi.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 476 : 476 Petrarcae Francisci. Septem Psalmi Poenitentiales latinis versibus redditi. Cod. membr. in octavo Saec. XV. | — (pas d'entité gold) | `476` (ouvrage) — inventé (FP) |
| Run 3·BiLSTM | 417 : 417 Landini Christophori Dialogi de Anima. Cod. chartac. in quarto Saec. XV Autographus | `Landini Christophori` (auteur) | `Landini Christophori Dialogi de Anima.` (ouvrage) — confusion label |
| Run 3·BiLSTM | 417 : 417 Landini Christophori Dialogi de Anima. Cod. chartac. in quarto Saec. XV Autographus | `Dialogi de Anima.` (ouvrage) | — (manqué) |
| Run 3·BiLSTM | 417 : 417 Landini Christophori Dialogi de Anima. Cod. chartac. in quarto Saec. XV Autographus | `Cod. chartac. in quarto` (material) | `chartac.` (material) — frontière |
| Run 3·BiLSTM | 242 : 242 Gregorii PP. Homiliae in Ezechielem Prophetam. Cod. membr. in fol. Saec. XII in fine mutilus ut videtur. | `Gregorii PP.` (auteur) | — (manqué) |
| Run 3·BiLSTM | 242 : 242 Gregorii PP. Homiliae in Ezechielem Prophetam. Cod. membr. in fol. Saec. XII in fine mutilus ut videtur. | `Cod. membr.` (material) | `Cod. membr. in fol.` (material) — frontière |
| Run 3·BiLSTM | 1386 : 1386 Leggendario di Santi. Cod. cartac. in fol. Sec. XV. manc. in princ. e in fine. | `manc. in princ. e in fine.` (etat) | — (manqué) |

*(Note : les 186 lignes ci-dessus proviennent d'un script qui lit directement `test_results.json` du dépôt — les 93 entrées de test avec leurs `gold_spans`/`pred_spans` — et les compare par décalage de caractères ; il ne s'agit plus d'une recopie manuelle, donc le texte de chaque entrée est intégral, sans troncature.)*

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
- **BiLSTM-CRF** (from scratch, emb=100/hid=256, ep=30) ★ meilleur système, F1=0,634 ; c'est de ce système, via son `test_results.json` réel, que provient la liste exhaustive de 186 erreurs (avec texte intégral) de cette table
- XLM-R frozen (encodeur **entièrement gelé**, seule une tête de classification linéaire de 8 459 paramètres est entraînée, équivalent à un simple extracteur de features, F1=0,072)
- XLM-R partial unfreeze / T2 (seules les 2 dernières couches sont dégelées, ~14,18 M de paramètres = 5,1 %, validation croisée 5-fold + jeu de test isolé, F1=0,498)
