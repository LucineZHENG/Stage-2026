#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_el_remaining.py
======================
Fusionne les résultats EL (VIAF + Wikidata) dans gold_annotations_remaining.json.

Logique :
  - Lit el_auteur_ouvrage_remaining.jsonl (2055 lignes, doublons possibles)
  - Déduplique par (entry_id, span_text, label) en gardant le record le plus récent
  - Pour chaque span auteur/ouvrage dans gold_annotations_remaining.json,
    injecte el_results et el_uri (URI du meilleur candidat, score le plus élevé)
  - Les spans material/date/etat ne sont pas concernés par l'EL

Usage :
    python3 merge_el_remaining.py

Fichiers requis (dans output_remaining/) :
  - gold_annotations_remaining.json   (généré par merge_annotations_remaining.py)
  - el_auteur_ouvrage_remaining.jsonl (sauvegardé par prima_monitor_remaining.py)

Sortie :
  - gold_annotations_remaining_el.json
"""

import json
import os

_HERE       = os.path.dirname(os.path.abspath(__file__))
GOLD_JSON   = os.path.join(_HERE, "gold_annotations_remaining.json")
EL_JSONL    = os.path.join(_HERE, "el_auteur_ouvrage_remaining.jsonl")
OUTPUT_JSON = os.path.join(_HERE, "gold_annotations_remaining_el.json")


def load_el_index(el_path):
    """
    Charge el_auteur_ouvrage_remaining.jsonl et déduplique.
    Retourne : dict { (entry_id, span_text, label) -> annotation_dict }
    En cas de doublon, garde le record avec le timestamp le plus récent.
    """
    index = {}  # (entry_id, span_text, label) -> (timestamp, ann_dict)
    total_lines = 0
    with open(el_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_lines += 1
            rec = json.loads(line)
            eid = rec['entry_id']
            ts  = rec['timestamp']
            for ann in rec.get('annotations', []):
                key = (eid, ann['span_text'], ann['label'])
                if key not in index or ts > index[key][0]:
                    index[key] = (ts, ann)

    result = {k: v[1] for k, v in index.items()}
    print(f"[EL] {total_lines} lignes lues → {len(result)} annotations uniques après déduplication")
    return result


def best_uri(el_results):
    """Retourne l'URI du candidat avec le score le plus élevé, ou '' si vide."""
    if not el_results:
        return ""
    best = max(el_results, key=lambda x: x.get('score', 0))
    return best.get('uri', '')


def merge():
    # Charger l'index EL
    el_index = load_el_index(EL_JSONL)

    # Charger gold
    with open(GOLD_JSON, encoding='utf-8') as f:
        gold = json.load(f)
    print(f"[Gold] {len(gold)} entrées chargées")

    # Stats
    matched = 0
    unmatched = 0
    total_auteur_ouvrage = 0

    for entry in gold:
        eid = entry['entry_id']
        new_spans = []
        for span in entry.get('spans', []):
            label = span['label']
            if label in ('auteur', 'ouvrage'):
                total_auteur_ouvrage += 1
                key = (eid, span['text'], label)
                if key in el_index:
                    ann = el_index[key]
                    span['el_results'] = ann.get('el_results', [])
                    span['el_uri']     = best_uri(span['el_results'])
                    # Récupérer normalized du monitor si disponible
                    if ann.get('normalized'):
                        span['normalized'] = ann['normalized']
                    matched += 1
                else:
                    span['el_results'] = []
                    span['el_uri']     = ''
                    unmatched += 1
            else:
                # material / date / etat : pas d'EL
                span['el_results'] = []
                span['el_uri']     = ''
            new_spans.append(span)
        entry['spans'] = new_spans

    # Sauvegarder
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(gold, f, ensure_ascii=False, indent=2)
    print(f"[Done] → {OUTPUT_JSON}")

    # Statistiques
    print(f"\n[Stats EL]")
    print(f"  Spans auteur/ouvrage total : {total_auteur_ouvrage}")
    print(f"  Matchés dans EL index      : {matched}")
    print(f"  Non matchés (pas de EL)    : {unmatched}")

    with_uri = sum(
        1 for e in gold for sp in e['spans']
        if sp.get('el_uri')
    )
    print(f"  Spans avec el_uri non vide : {with_uri}")


if __name__ == "__main__":
    merge()
