#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_remaining.py
====================
Génère les fichiers à importer dans INCEpTION pour les entrées
NON encore annotées (= tout le catalogue moins les 100 entrées gold).

Sorties dans ./output_remaining/ :
  - remaining_for_inception.txt   → texte brut, 1 ligne/entrée (import INCEpTION)
  - remaining_guide.tsv           → guide annotateur (entry_id, raw, fr, zh, auteurs, titres)
  - remaining_entries.json        → métadonnées complètes (pour inject_annotations.py)

Usage :
    python3 prepare_remaining.py

Prérequis (même dossier) :
    catalogue.txt
    catalogue_dict.json
    Catalogo_I_Riccardiana_221-320.json
    Catalogo_II_Riccardiana_321-420.json
    Catalogo_III_Riccardiana_421-520.json
    Catalogo_IV_Riccardiana_1002-1700.json
    gold_annotations_with_el.json
"""

import json
import os
import re

# ── Chemins ──────────────────────────────────────────────────────────────────
CATALOGUE_TXT  = "./catalogue.txt"
GOLD_PATH      = "./output_inception/gold_annotations_with_el.json"
CAT_DICT_PATH  = "./catalogue_dict.json"
JSON_FILES = [
    ("Catalogo_I_Riccardiana_221-320.json",   "Catalogo_I"),
    ("Catalogo_II_Riccardiana_321-420.json",  "Catalogo_II"),
    ("Catalogo_III_Riccardiana_421-520.json", "Catalogo_III"),
    ("Catalogo_IV_Riccardiana_1002-1700.json","Catalogo_IV"),
]
OUT_DIR = "./output_remaining"

# ── Siècles romains → (début, fin) ───────────────────────────────────────────
CENTURIES_MAP = {
    'i':(1,99),'ii':(100,199),'iii':(200,299),'iv':(300,399),
    'v':(400,499),'vi':(500,599),'vii':(600,699),'viii':(700,799),
    'ix':(800,899),'x':(900,999),'xi':(1000,1099),'xii':(1100,1199),
    'xiii':(1200,1299),'xiv':(1300,1399),'xv':(1400,1499),
    'xvi':(1500,1599),'xvii':(1600,1699),'xviii':(1700,1799),
}
_SAEC_PAT = re.compile(r'(?:S[ae]{1,2}c(?:ulo)?|Sec(?:olo)?)\.?\s+([ivxlcdm]+)', re.IGNORECASE)

def ms_century_range(raw_text):
    m = _SAEC_PAT.search(raw_text)
    if m:
        return CENTURIES_MAP.get(m.group(1).lower(), (0, 0))
    return (0, 0)

# ── 1. Charger catalogue.txt ─────────────────────────────────────────────────
cat_lines = {}
with open(CATALOGUE_TXT, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip()
        if not line:
            continue
        m = re.match(r'^(\d+)', line)
        if m:
            eid = int(m.group(1))
            if eid not in cat_lines:  # garder première occurrence si doublon
                cat_lines[eid] = line

print(f"[catalogue.txt] {len(cat_lines)} entrées uniques")

# ── 2. Charger les entry_ids déjà annotés (gold) ─────────────────────────────
with open(GOLD_PATH, encoding="utf-8") as f:
    gold = json.load(f)
gold_ids = {e["entry_id"] for e in gold}
print(f"[gold] {len(gold_ids)} entrées déjà annotées → à exclure")

# ── 3. Charger les 4 JSON Riccardiana ────────────────────────────────────────
def ms_entry_id(ms):
    sig = ms.get("shelf_mark", {}).get("signature", "")
    m = re.search(r'(\d+)', sig)
    return int(m.group(1)) if m else None

def extract_fields(ms):
    """Extrait material, date, auteurs, titres depuis un manuscrit JSON."""
    phys = ms.get("physical_description", {})
    content = ms.get("content", [])
    if isinstance(content, dict):
        content = [content]
    material  = phys.get("material", "")
    date_raw  = phys.get("date", "")
    authors   = []
    titles    = []
    seen_a = set(); seen_t = set()
    for item in (content or []):
        if not isinstance(item, dict):
            continue
        # auteur
        for key in ("author", "auteur", "attributed_author"):
            v = (item.get(key) or "").strip()
            if v and v not in seen_a:
                seen_a.add(v); authors.append(v)
        # titre
        for key in ("attributed_title", "title", "titre"):
            v = (item.get(key) or "").strip()
            if v and v not in seen_t:
                seen_t.add(v); titles.append(v)
    return material, date_raw, authors, titles

# Index JSON : entry_id → (source_file_label, ms_dict)
json_index = {}
for fname, label in JSON_FILES:
    with open(fname, encoding="utf-8") as f:
        d = json.load(f)
    for ms in d["manuscripts"]:
        eid = ms_entry_id(ms)
        if eid and eid not in json_index:
            json_index[eid] = (label, ms)

print(f"[JSON] {len(json_index)} entrées indexées")

# ── 4. Charger catalogue_dict pour traductions ───────────────────────────────
cat_dict = {}
try:
    with open(CAT_DICT_PATH, encoding="utf-8") as f:
        cat_dict = json.load(f)
    print(f"[catalogue_dict] {len(cat_dict)} entrées chargées")
except Exception as e:
    print(f"[WARN] catalogue_dict non chargé: {e}")

def get_translations(eid):
    key = str(eid)
    if key in cat_dict:
        entry = cat_dict[key]
        return (entry.get("traduction_fr", "") or "",
                entry.get("traduction_zh", "") or "")
    return "", ""

# ── 5. Construire la liste des entrées restantes ──────────────────────────────
remaining = []
for eid in sorted(cat_lines.keys()):
    if eid in gold_ids:
        continue
    if eid not in json_index:
        continue  # pas dans les JSON → ignorer
    raw = cat_lines[eid]
    label, ms = json_index[eid]
    material, date_raw, authors, titles = extract_fields(ms)
    tr_fr, tr_zh = get_translations(eid)
    ms_range = ms_century_range(raw)
    remaining.append({
        "entry_id":    eid,
        "source_file": label,
        "raw":         raw,
        "traduction_fr": tr_fr,
        "traduction_zh": tr_zh,
        "json_material": material,
        "json_date":     date_raw,
        "ms_century_range": list(ms_range),
        "json_authors":  authors,
        "json_titles":   titles,
    })

print(f"[Remaining] {len(remaining)} entrées à annoter")

# ── 6. Export ─────────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)

# 6a. Texte brut pour INCEpTION (1 ligne par entrée)
txt_path = os.path.join(OUT_DIR, "remaining_for_inception.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    for e in remaining:
        f.write(e["raw"] + "\n")
print(f"[Export] {txt_path}  ({len(remaining)} lignes)")

# 6b. Guide annotateur TSV
tsv_path = os.path.join(OUT_DIR, "remaining_guide.tsv")
cols = ["entry_id","source_file","raw","traduction_fr","traduction_zh",
        "json_authors","json_titles","json_material","json_date","ms_century_range"]
with open(tsv_path, "w", encoding="utf-8") as f:
    f.write("\t".join(cols) + "\n")
    for e in remaining:
        row = [
            str(e["entry_id"]),
            e["source_file"],
            e["raw"],
            e["traduction_fr"],
            e["traduction_zh"],
            "; ".join(e["json_authors"]),
            "; ".join(e["json_titles"]),
            e["json_material"],
            e["json_date"],
            f"{e['ms_century_range'][0]}-{e['ms_century_range'][1]}",
        ]
        f.write("\t".join(row) + "\n")
print(f"[Export] {tsv_path}")

# 6c. JSON complet (pour inject_annotations.py)
json_path = os.path.join(OUT_DIR, "remaining_entries.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(remaining, f, ensure_ascii=False, indent=2)
print(f"[Export] {json_path}")

print(f"\n[Done] {len(remaining)} entrées prêtes pour INCEpTION")
print(f"       → Importer : {txt_path}")
print(f"       → Guide    : {tsv_path}")
