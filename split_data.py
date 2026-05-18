#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_data.py
=============
Divise les 100 entrées annotées (gold_annotations_with_el.json)
en trois ensembles : train (70) / val (20) / test (10).

Seed fixe = 42 → reproductible.

Sorties dans ./ner_data/ :
  - train.json   → 70 entrées
  - val.json     → 20 entrées
  - test.json    → 10 entrées
  - split_index.json → {entry_id: split} pour traçabilité

Usage :
    python3 split_data.py
"""

import json
import os
import random
from collections import Counter

GOLD_PATH = "./output_inception/gold_annotations_with_el.json"
OUT_DIR   = "./ner_data"
SEED      = 42

# ── Charger les données ───────────────────────────────────────────────────────
with open(GOLD_PATH, encoding="utf-8") as f:
    data = json.load(f)

print(f"[Load] {len(data)} entrées chargées")

# ── Diviser ───────────────────────────────────────────────────────────────────
random.seed(SEED)
indices = list(range(len(data)))
random.shuffle(indices)

train = [data[i] for i in indices[:70]]
val   = [data[i] for i in indices[70:90]]
test  = [data[i] for i in indices[90:]]

# ── Statistiques ──────────────────────────────────────────────────────────────
for split_name, split in [("TRAIN", train), ("VAL", val), ("TEST", test)]:
    counts = Counter(s["label"] for e in split for s in e.get("spans", []))
    total  = sum(counts.values())
    print(f"\n{split_name} ({len(split)} entrées, {total} spans) :")
    for label in ["auteur", "ouvrage", "material", "date", "etat"]:
        print(f"  {label:10s}: {counts[label]}")

# ── Export ────────────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)

for fname, split in [("train.json", train), ("val.json", val), ("test.json", test)]:
    path = os.path.join(OUT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(split, f, ensure_ascii=False, indent=2)
    print(f"\n[Export] {path}  ({len(split)} entrées)")

# Index de traçabilité : entry_id → split
split_index = {}
for e in train: split_index[e["entry_id"]] = "train"
for e in val:   split_index[e["entry_id"]] = "val"
for e in test:  split_index[e["entry_id"]] = "test"

idx_path = os.path.join(OUT_DIR, "split_index.json")
with open(idx_path, "w", encoding="utf-8") as f:
    json.dump(split_index, f, ensure_ascii=False, indent=2)
print(f"[Export] {idx_path}")

print(f"\n[Done] Seed={SEED} → train/val/test reproductibles")
