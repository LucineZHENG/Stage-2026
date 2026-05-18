#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_report.py
===============
Génère un rapport détaillé des ensembles train/val/test :
- Composition (entry_id, raw, spans)
- Statistiques par label
- Caractéristiques des données

Sortie : ner_data/split_report.md

Usage :
    python3 split_report.py
"""

import json
import os
from collections import Counter

GOLD_PATH = "./output_inception/gold_annotations_with_el.json"
IDX_PATH  = "./ner_data/split_index.json"
OUT_PATH  = "./ner_data/split_report.md"

with open(GOLD_PATH, encoding="utf-8") as f:
    data = json.load(f)
with open(IDX_PATH, encoding="utf-8") as f:
    split_index = json.load(f)

# Regrouper par split
splits = {"train": [], "val": [], "test": []}
for e in data:
    s = split_index.get(str(e["entry_id"]) if str(e["entry_id"]) in split_index
                        else e["entry_id"])
    if s:
        splits[s].append(e)

lines = []
lines.append("# Rapport de division des données — PRIMA NER\n")
lines.append(f"Seed : 42 | Total : 100 entrées | Train : 70 / Val : 20 / Test : 10\n")
lines.append(f"Source : `gold_annotations_with_el.json`\n")

for split_name in ["train", "val", "test"]:
    entries = splits[split_name]
    label_counts = Counter(s["label"] for e in entries for s in e.get("spans", []))
    total_spans  = sum(label_counts.values())

    # Longueurs des textes
    lengths = [len(e["raw"].split()) for e in entries]
    avg_len = sum(lengths) / len(lengths)
    min_len = min(lengths)
    max_len = max(lengths)

    # Siècles représentés
    centuries = Counter()
    for e in entries:
        r = e.get("ms_century_range", [0,0])
        if r and r[0]:
            centuries[f"{r[0]}–{r[1]}"] += 1

    # Fichiers sources
    sources = Counter(e.get("source_file","?") for e in entries)

    lines.append(f"\n---\n\n## {split_name.upper()} — {len(entries)} entrées\n")

    # Stats spans
    lines.append("### Distribution des labels\n")
    lines.append("| Label | Nb spans | % |\n|---|---|---|")
    for label in ["auteur", "ouvrage", "material", "date", "etat"]:
        n = label_counts[label]
        pct = 100 * n / total_spans if total_spans else 0
        lines.append(f"| {label} | {n} | {pct:.1f}% |")
    lines.append(f"| **Total** | **{total_spans}** | 100% |")

    # Caractéristiques
    lines.append("\n### Caractéristiques\n")
    lines.append(f"- Longueur moyenne des entrées : **{avg_len:.1f} tokens** (min {min_len}, max {max_len})")
    lines.append(f"- Spans par entrée (moyenne) : **{total_spans/len(entries):.1f}**")
    lines.append(f"- Entrées avec `auteur` : **{sum(1 for e in entries if any(s['label']=='auteur' for s in e.get('spans',[])))}**")
    lines.append(f"- Entrées avec `ouvrage` : **{sum(1 for e in entries if any(s['label']=='ouvrage' for s in e.get('spans',[])))}**")
    lines.append(f"- Entrées avec `etat` : **{sum(1 for e in entries if any(s['label']=='etat' for s in e.get('spans',[])))}**")

    # Siècles
    lines.append("\n### Siècles des manuscrits\n")
    lines.append("| Siècle | Nb entrées |\n|---|---|")
    for cent, n in sorted(centuries.items()):
        lines.append(f"| {cent} | {n} |")

    # Fichiers sources
    lines.append("\n### Fichiers sources\n")
    lines.append("| Fichier | Nb entrées |\n|---|---|")
    for src, n in sorted(sources.items()):
        lines.append(f"| {src} | {n} |")

    # Liste des entry_ids
    ids = sorted(e["entry_id"] for e in entries)
    lines.append(f"\n### Entry IDs ({len(ids)})\n")
    lines.append("`" + ", ".join(str(i) for i in ids) + "`")

    # Détail entrées
    lines.append("\n### Détail des entrées\n")
    lines.append("| entry_id | Texte brut | Labels |\n|---|---|---|")
    for e in sorted(entries, key=lambda x: x["entry_id"]):
        raw = e["raw"][:80] + "…" if len(e["raw"]) > 80 else e["raw"]
        raw = raw.replace("|", "\\|")
        labels = ", ".join(f"{s['label']}({s['text'][:20]})" for s in e.get("spans", []))
        lines.append(f"| {e['entry_id']} | {raw} | {labels} |")

os.makedirs("ner_data", exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"[Done] → {OUT_PATH}")
