#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_annotations_remaining.py
===============================
Fusionne :
  - admin.json         (export INCEpTION, annotations manuelles des 838 entrées)
  - remaining_entries.json  (métadonnées des 838 entrées)
→ gold_annotations_remaining.json

Les trois fichiers doivent être dans le même dossier (output_remaining/).

Usage :
    python3 merge_annotations_remaining.py
"""

import json
import re
import os
import sys

# ── Chemins (tous dans output_remaining/) ────────────────────────────────────
_HERE          = os.path.dirname(os.path.abspath(__file__))
ADMIN_JSON     = os.path.join(_HERE, "admin.json")
ENTRIES_JSON   = os.path.join(_HERE, "remaining_entries.json")
SOURCE_TXT     = os.path.join(_HERE, "remaining_for_inception.txt")
OUTPUT_JSON    = os.path.join(_HERE, "gold_annotations_remaining.json")

# ── Mappings normalization (cherche dans le dossier parent) ──────────────────
sys.path.insert(0, os.path.join(_HERE, '..'))
try:
    from MAPPING_mfe import SUPPORT_NORM, FORMAT_NORM, MATERIAL_COMBINATIONS, ETAT_NORM
    from MAPPING_date import CENTURIES, PERIODS
    HAS_MAPPING = True
except ImportError:
    HAS_MAPPING = False
    print("[WARN] MAPPING_mfe / MAPPING_date non trouvés, normalisation désactivée")


def normalize_material(text):
    if not HAS_MAPPING:
        return text.strip()
    t = text.strip()
    if t in MATERIAL_COMBINATIONS:
        return MATERIAL_COMBINATIONS[t]
    for k, v in SUPPORT_NORM.items():
        if t == k or t.startswith(k):
            return v
    for k, v in FORMAT_NORM.items():
        if k in t:
            return v
    return t


def normalize_etat(text):
    if not HAS_MAPPING:
        return text.strip()
    t = text.strip().lower()
    for k, v in ETAT_NORM.items():
        if k.lower() in t or t in k.lower():
            return v
    return text.strip()


def auto_normalize(label, text):
    if label == 'material':
        return normalize_material(text)
    elif label == 'etat':
        return normalize_etat(text)
    elif label == 'date':
        return text.strip()
    else:
        return ""  # auteur/ouvrage : normalisé par le monitor


def load_admin_spans(admin_path, source_txt_path):
    """
    Extrait les spans annotés manuellement depuis admin.json,
    les associe à leur entry_id via remaining_for_inception.txt.
    Retourne : dict { entry_id -> list[{label, text, normalized, el_uri}] }
    """
    with open(admin_path, encoding='utf-8') as f:
        data = json.load(f)

    fs = data.get('%FEATURE_STRUCTURES', {})
    fs_list = list(fs.values()) if isinstance(fs, dict) else fs

    # Texte source (sofaString)
    sofa_obj = [f for f in fs_list if isinstance(f, dict) and 'sofaString' in f]
    if not sofa_obj:
        raise ValueError("sofaString introuvable dans admin.json")
    text = sofa_obj[0]['sofaString']

    # NER spans
    ner = [
        f for f in fs_list
        if isinstance(f, dict)
        and 'NER_PRIMA' in f.get('%TYPE', '')
        and f.get('label')
    ]
    print(f"[admin.json] {len(ner)} spans NER trouvés")

    # Mapping offset → entry_id via remaining_for_inception.txt
    with open(source_txt_path, encoding='utf-8') as f:
        lines = [l.rstrip() for l in f if l.strip()]

    offset = 0
    line_map = []
    for line in lines:
        m = re.match(r'^(\d+)', line)
        eid = int(m.group(1)) if m else None
        line_map.append((offset, offset + len(line), eid))
        offset += len(line) + 1

    def get_eid(begin, end):
        for start, stop, eid in line_map:
            if begin >= start and end <= stop:
                return eid
        return None

    result = {}
    skipped = 0
    for a in ner:
        begin = int(a.get('begin', 0))
        end   = int(a.get('end', 0))
        label = a.get('label', '').strip()
        if not label:
            continue
        span_text = text[begin:end].strip()
        eid = get_eid(begin, end)
        if eid is None:
            skipped += 1
            continue
        normalized = auto_normalize(label, span_text)
        result.setdefault(eid, []).append({
            "label":      label,
            "text":       span_text,
            "normalized": normalized,
            "el_uri":     ""
        })

    print(f"[admin.json] {skipped} spans ignorés (hors ligne connue)")
    print(f"[admin.json] {sum(len(v) for v in result.values())} spans associés à {len(result)} entrées")
    return result


def merge():
    # Charger les spans manuels
    admin_spans = load_admin_spans(ADMIN_JSON, SOURCE_TXT)

    # Charger les métadonnées
    with open(ENTRIES_JSON, encoding='utf-8') as f:
        entries = json.load(f)
    print(f"[remaining_entries.json] {len(entries)} entrées chargées")

    # Fusionner
    gold = []
    for entry in entries:
        eid = entry['entry_id']
        new_entry = dict(entry)
        new_entry['spans'] = admin_spans.get(eid, [])
        new_entry['el_results'] = []  # sera rempli par merge_el_remaining.py
        gold.append(new_entry)

    # Sauvegarder
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(gold, f, ensure_ascii=False, indent=2)
    print(f"[Done] → {OUTPUT_JSON}")

    # Statistiques
    from collections import Counter
    counts = Counter(sp['label'] for e in gold for sp in e['spans'])
    total = sum(counts.values())
    print(f"\n[Stats] {total} spans au total :")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")

    no_spans = [e['entry_id'] for e in gold if not e['spans']]
    if no_spans:
        print(f"\n[WARN] {len(no_spans)} entrées sans aucun span : {no_spans[:10]}{'...' if len(no_spans)>10 else ''}")


if __name__ == "__main__":
    merge()
