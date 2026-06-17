#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_and_split_all.py
======================
Fusionne les 100 entrées annotées (gold_annotations_with_el.json, déjà
divisées en train/val/test) et les 838 entrées restantes
(gold_annotations_remaining_el.json) pour constituer un corpus complet
de 938 entrées, puis le divise en train/val/test selon la même logique
que split_data.py (ratio 70/20/10 %, seed=42).

Différences de format entre les deux sources :
  - Champ entrée absent dans la nouvelle source :
      json_date_norm, date_comparison  → mis à None/[] si absent
  - Champ span absent dans la nouvelle source :
      norm_method                       → mis à "" si absent
  - Champ span présent seulement dans la nouvelle source :
      el_results (dans chaque span)     → conservé, mis à [] si absent
  - Entrées sans spans (ex. entry 393 "Idem.") → conservées mais
    exclues du calcul des métriques NER.

Sorties dans ./ner_data_all/ :
  train.json, val.json, test.json, split_index.json

Usage :
    python3 merge_and_split_all.py
"""

import json
import os
import random
from collections import Counter

# ── Chemins ───────────────────────────────────────────────────────────────────
OLD_TRAIN  = "./ner_data/train.json"
OLD_VAL    = "./ner_data/val.json"
OLD_TEST   = "./ner_data/test.json"
NEW_PATH   = "./gold_annotations_remaining_el.json"
OUT_DIR    = "./ner_data_all"
SEED       = 42

# ── 1. Chargement ─────────────────────────────────────────────────────────────
print("[1/4] Chargement des données...")

old_entries = []
for path in [OLD_TRAIN, OLD_VAL, OLD_TEST]:
    part = json.load(open(path, encoding="utf-8"))
    old_entries.extend(part)
print(f"  Ancien corpus (gold 100) : {len(old_entries)} entrées")

new_entries = json.load(open(NEW_PATH, encoding="utf-8"))
print(f"  Nouveau corpus (remaining) : {len(new_entries)} entrées")

# Vérification : pas de doublon sur entry_id
old_ids = {e["entry_id"] for e in old_entries}
new_ids = {e["entry_id"] for e in new_entries}
overlap = old_ids & new_ids
if overlap:
    print(f"  ⚠️  {len(overlap)} entry_id en commun — vérifier !")
else:
    print("  ✓ Pas de doublon entry_id entre les deux sources")


# ── 2. Normalisation du format ────────────────────────────────────────────────
print("\n[2/4] Normalisation du format...")

def normalize_entry(entry, source="old"):
    """
    Unifie le format des entrées des deux sources.

    Champs ajoutés si absents (source 'new' n'a pas ces champs) :
      - json_date_norm : normalisations de dates  → None
      - date_comparison : comparaison de dates    → []

    Champs de spans normalisés :
      - norm_method (absent dans 'new')            → ""
      - el_results  (absent dans certains spans 'old') → []
    """
    e = dict(entry)  # copie superficielle

    # Champs manquants dans la source 'new'
    if "json_date_norm" not in e:
        e["json_date_norm"] = None
    if "date_comparison" not in e:
        e["date_comparison"] = []

    # Normalisation des spans
    normalized_spans = []
    for span in e.get("spans", []):
        s = dict(span)
        if "norm_method" not in s:
            s["norm_method"] = ""       # absent dans 'new'
        if "el_results" not in s:
            s["el_results"] = []        # absent dans 'old'
        normalized_spans.append(s)
    e["spans"] = normalized_spans

    # Marqueur de source pour traçabilité
    e["_source"] = source

    return e

old_normalized = [normalize_entry(e, "gold_100")       for e in old_entries]
new_normalized = [normalize_entry(e, "remaining_838")  for e in new_entries]

all_entries = old_normalized + new_normalized
print(f"  Total après fusion : {len(all_entries)} entrées")

# Statistiques globales
label_counts = Counter(
    s["label"] for e in all_entries for s in e.get("spans", [])
)
print(f"  Spans totaux : {sum(label_counts.values())}")
for label in ["auteur", "ouvrage", "material", "date", "etat"]:
    print(f"    {label:10s}: {label_counts[label]}")
no_spans = sum(1 for e in all_entries if not e.get("spans"))
print(f"  Entrées sans spans : {no_spans}")


# ── 3. Division train/val/test ────────────────────────────────────────────────
print("\n[3/4] Division des données (seed=42, ratio 70/20/10 %)...")

random.seed(SEED)
indices = list(range(len(all_entries)))
random.shuffle(indices)

n_total = len(all_entries)          # 938
n_train = int(n_total * 0.70)      # 656
n_val   = int(n_total * 0.10)      # 93
# Le reste va au test (pour avoir un test set suffisant)
# Mais on peut aussi faire 70/20/10 strict :
n_train = round(n_total * 0.70)    # 657
n_val   = round(n_total * 0.20)    # 188
# test = reste
n_test  = n_total - n_train - n_val  # 93

train = [all_entries[i] for i in indices[:n_train]]
val   = [all_entries[i] for i in indices[n_train:n_train + n_val]]
test  = [all_entries[i] for i in indices[n_train + n_val:]]

print(f"  train : {len(train)} entrées ({100*len(train)/n_total:.1f}%)")
print(f"  val   : {len(val)}   entrées ({100*len(val)/n_total:.1f}%)")
print(f"  test  : {len(test)}  entrées ({100*len(test)/n_total:.1f}%)")

for split_name, split in [("TRAIN", train), ("VAL", val), ("TEST", test)]:
    counts = Counter(s["label"] for e in split for s in e.get("spans", []))
    total  = sum(counts.values())
    print(f"\n  {split_name} ({len(split)} entrées, {total} spans) :")
    for label in ["auteur", "ouvrage", "material", "date", "etat"]:
        print(f"    {label:10s}: {counts[label]}")


# ── 4. Export ─────────────────────────────────────────────────────────────────
print("\n[4/4] Export...")
os.makedirs(OUT_DIR, exist_ok=True)

for fname, split in [("train.json", train), ("val.json", val), ("test.json", test)]:
    path = os.path.join(OUT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(split, f, ensure_ascii=False, indent=2)
    print(f"  → {path}  ({len(split)} entrées)")

# Index de traçabilité
split_index = {}
for e in train: split_index[str(e["entry_id"])] = "train"
for e in val:   split_index[str(e["entry_id"])] = "val"
for e in test:  split_index[str(e["entry_id"])] = "test"

idx_path = os.path.join(OUT_DIR, "split_index.json")
with open(idx_path, "w", encoding="utf-8") as f:
    json.dump(split_index, f, ensure_ascii=False, indent=2)
print(f"  → {idx_path}")

print(f"\n[Done] Seed={SEED} | {len(train)} train / {len(val)} val / {len(test)} test")
