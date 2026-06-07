#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_el.py
===========
1. 读取 el_auteur_ouvrage.jsonl，按 entry_id 取最后一条（去重）
2. 将 EL 结果填入 gold_annotations.json：
   - el_results 字段：完整 top-3 候选列表
   - spans[].normalized / spans[].el_uri：填入 #1 候选的规范化形式和 URI
3. 输出 gold_annotations_with_el.json

Usage:
    python3 merge_el.py
"""

import json

JSONL_PATH  = "./output_EL/el_auteur_ouvrage.jsonl"
GOLD_PATH   = "./gold_annotations.json"
OUTPUT_PATH = "./gold_annotations_with_el.json"

# ── Étape 1 : lire le JSONL, garder la dernière entrée par entry_id ──────────
last_by_id = {}
with open(JSONL_PATH, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        eid = rec["entry_id"]
        last_by_id[eid] = rec  # écrase → on garde la dernière

print(f"[JSONL] {len(last_by_id)} entrées uniques après déduplication")

# Construire un index : entry_id → {span_text → annotation}
el_index = {}   # {entry_id: {span_text_lower: annotation_dict}}
for eid, rec in last_by_id.items():
    el_index[eid] = {}
    for ann in rec.get("annotations", []):
        key = ann["span_text"].strip().lower()
        el_index[eid][key] = ann

# ── Étape 2 : charger gold_annotations.json ──────────────────────────────────
with open(GOLD_PATH, encoding="utf-8") as f:
    gold = json.load(f)

print(f"[Gold] {len(gold)} entrées chargées")

filled = 0
for entry in gold:
    eid = entry["entry_id"]
    if eid not in el_index:
        continue

    ann_map = el_index[eid]

    # Remplir el_results (liste complète des annotations EL de cette entrée)
    entry["el_results"] = last_by_id[eid].get("annotations", [])

    # Remplir spans[].normalized et spans[].el_uri pour auteur/ouvrage
    for span in entry.get("spans", []):
        if span["label"] not in ("auteur", "ouvrage"):
            continue
        key = span["text"].strip().lower()
        if key not in ann_map:
            continue
        ann = ann_map[key]
        # normalized : forme nominative
        span["normalized"] = ann.get("normalized", "")
        # el_uri : URI du candidat #1 (score le plus élevé)
        results = ann.get("el_results", [])
        if results:
            span["el_uri"] = results[0]["uri"]
        # norm_method en bonus
        span["norm_method"] = ann.get("norm_method", "")

    filled += 1

print(f"[Merge] {filled} entrées enrichies avec EL")

# ── Étape 3 : sauvegarder ────────────────────────────────────────────────────
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(gold, f, ensure_ascii=False, indent=2)

print(f"[Done] → {OUTPUT_PATH}")

# ── Résumé rapide ─────────────────────────────────────────────────────────────
total_spans = sum(
    len([s for s in e.get("spans", []) if s["label"] in ("auteur","ouvrage")])
    for e in gold
)
filled_uris = sum(
    len([s for s in e.get("spans", []) if s["label"] in ("auteur","ouvrage") and s.get("el_uri")])
    for e in gold
)
print(f"[Stats] spans auteur/ouvrage : {total_spans} total, {filled_uris} avec el_uri, {total_spans-filled_uris} sans résultat EL")
