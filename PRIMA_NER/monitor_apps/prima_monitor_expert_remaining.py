#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prima_monitor_expert.py
=======================
Interface de validation experte pour l'Entity Linking PRIMA.
Charge gold_annotations_with_el.json, affiche les résultats EL
pour chaque entrée, et permet à l'expert de :
  - valider / invalider les candidats EL (auteur/ouvrage)
  - confirmer les annotations date/material/etat
  - modifier le label ou le texte d'un span (avec re-requête EL)
  - ajouter ou supprimer des spans
  - naviguer entre les entrées (précédente / suivante)
  - sauvegarder dans el_validated.jsonl

Usage :
    python3 prima_monitor_expert.py

Dependencies :
    pip install flask requests
"""

import difflib as _difflib
import json
import os
import re
import threading
import time
from datetime import datetime

import requests
from flask import Flask, jsonify, render_template_string, request

# ── Configuration ─────────────────────────────────────────────────────────────
GOLD_PATH      = "./output_remaining/gold_annotations_remaining_el.json"
CAT_DICT_PATH  = "./catalogue_dict.json"
VALIDATED_PATH = "./output_remaining/el_validated_remaining.jsonl"
PORT           = 5053
TOP_K          = 3

VIAF_SUGGEST = "https://viaf.org/viaf/AutoSuggest"
WD_URL       = "https://www.wikidata.org/w/api.php"
WD_SPARQL    = "https://query.wikidata.org/sparql"
HEADERS      = {"User-Agent": "PRIMA-Research/1.0 (academic project; github.com/LucineZHENG)"}

CENTURY_MAP = {
    "i":(1,99),"ii":(100,199),"iii":(200,299),"iv":(300,399),
    "v":(400,499),"vi":(500,599),"vii":(600,699),"viii":(700,799),
    "ix":(800,899),"x":(900,999),"xi":(1000,1099),"xii":(1100,1199),
    "xiii":(1200,1299),"xiv":(1300,1399),"xv":(1400,1499),
    "xvi":(1500,1599),"xvii":(1600,1699),"xviii":(1700,1799),
}

# ── Chargement du dictionnaire de normalisation ───────────────────────────────
GENITIF_TO_NOM:     dict = {}
NOM_CONTAINS:       list = []
OUVRAGE_GEN_TO_NOM: dict = {}

try:
    with open(CAT_DICT_PATH, encoding="utf-8") as f:
        _cd = json.load(f)
    for _val in _cd.values():
        _ag = (_val.get("auteur_genitif")  or "").strip()
        _an = (_val.get("auteur_nominatif") or "").strip()
        if _an:
            if _ag: GENITIF_TO_NOM[_ag.lower()] = _an
            else:   NOM_CONTAINS.append((_an.lower(), _an))
        _og = (_val.get("ouvrage_genitif")  or "").strip()
        _on = (_val.get("ouvrage_nominatif") or "").strip()
        if _og and _on: OUVRAGE_GEN_TO_NOM[_og.lower()] = _on
    print(f"[Init] Dictionnaire: {len(GENITIF_TO_NOM)} auteurs latins, "
          f"{len(NOM_CONTAINS)} auteurs italiens, {len(OUVRAGE_GEN_TO_NOM)} ouvrages")
except Exception as e:
    print(f"[WARN] catalogue_dict.json non chargé: {e}")


def normalize(text, label):
    key = text.strip().lower()
    if label == "auteur":
        if key in GENITIF_TO_NOM: return GENITIF_TO_NOM[key], "genitif_exact"
        for nl, no in NOM_CONTAINS:
            if key in nl: return no, "nom_contains"
        return text.strip(), "fallback"
    elif label == "ouvrage":
        if key in OUVRAGE_GEN_TO_NOM: return OUVRAGE_GEN_TO_NOM[key], "genitif_exact"
        return text.strip(), "fallback"
    return text.strip(), "fallback"


# ── Chargement des données gold ───────────────────────────────────────────────
gold_data = []
try:
    with open(GOLD_PATH, encoding="utf-8") as f:
        gold_data = json.load(f)
    print(f"[Init] {len(gold_data)} entrées chargées depuis {GOLD_PATH}")
except Exception as e:
    print(f"[WARN] Impossible de charger {GOLD_PATH}: {e}")

# Index de validation : entry_id → résultat expert
validated = {}

# ── EL : VIAF + Wikidata ──────────────────────────────────────────────────────
def str_sim(a, b):
    return round(_difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio(), 3)

def time_score(birth, death, ms_range):
    if not ms_range or ms_range == [0,0]: return 0.0
    ms_start, ms_end = ms_range
    if birth is None and death is None: return 0.0
    if death is not None:
        if death <= ms_end: return 1.0
        if death <= ms_end + 50: return 0.7
        return 0.1
    if birth is not None:
        if birth > ms_end: return 0.0
        if birth >= ms_start: return 0.8
        return 0.6
    return 0.0

def combined(s, t):
    if t == 0.0: return round(0.7 * s, 3)
    return round(0.4 * s + 0.6 * t, 3)

def query_viaf(name, ms_range):
    try:
        r = requests.get(VIAF_SUGGEST, params={"query": name},
                         headers={**HEADERS, "Accept": "application/json"}, timeout=10)
        r.raise_for_status()
        results = r.json().get("result", []) or []
    except Exception: return []
    persons = [x for x in results if x.get("nametype") == "personal"]
    seen = set(); unique = []
    for p in persons:
        vid = p.get("viafid","")
        if vid and vid not in seen:
            seen.add(vid); unique.append(p)
    persons = unique[:TOP_K+2]
    out = []
    for person in persons:
        viafid = person.get("viafid",""); label = person.get("displayForm", name)
        if not viafid: continue
        birth = death = None; sources = []
        try:
            r2 = requests.get(f"https://viaf.org/viaf/{viafid}",
                              headers={**HEADERS,"Accept":"application/json"}, timeout=8)
            if r2.status_code == 200:
                cluster = r2.json().get("ns1:VIAFCluster",{})
                bm = re.search(r'(\d{3,4})', str(cluster.get("ns1:birthDate","")))
                dm = re.search(r'(\d{3,4})', str(cluster.get("ns1:deathDate","")))
                if bm: birth = int(bm.group(1))
                if dm: death = int(dm.group(1))
                raw = cluster.get("ns1:sources",{})
                src_list = raw.get("ns1:source",[])
                if isinstance(src_list, dict): src_list = [src_list]
                seen_s = set()
                for item in src_list:
                    lib = str(item.get("content","")).split("|")[0].strip()
                    if lib and lib not in seen_s:
                        seen_s.add(lib); sources.append(lib)
        except Exception: pass
        s = str_sim(name, label); t = time_score(birth, death, ms_range)
        out.append({"source":"viaf","label":label,
                    "uri":f"https://viaf.org/viaf/{viafid}",
                    "birth":birth,"death":death,"sources":sources,
                    "str_sim":s,"time_score":t,"score":combined(s,t)})
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:TOP_K]

def query_wikidata(name, ms_range):
    try:
        r = requests.get(WD_URL, params={"action":"wbsearchentities","search":name,
                         "language":"la","uselang":"fr","type":"item",
                         "format":"json","limit":TOP_K+2},
                         headers=HEADERS, timeout=10)
        r.raise_for_status()
        qids = [x["id"] for x in r.json().get("search",[])]
    except Exception: return []
    if not qids: return []
    # SPARQL : toutes les valeurs P214, sans filtrage
    sparql = f"""
SELECT ?item ?itemLabel ?birth ?death ?viafid WHERE {{
  VALUES ?item {{ {" ".join(f"wd:{q}" for q in qids)} }}
  OPTIONAL {{ ?item wdt:P569 ?birth. }}
  OPTIONAL {{ ?item wdt:P570 ?death. }}
  OPTIONAL {{ ?item wdt:P214 ?viafid. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "la,fr,en". }}
}}
"""
    dates_map = {}; label_map = {}
    viaf_ids_map = {}  # qid -> [viafid, ...]
    try:
        r2 = requests.get(WD_SPARQL, params={"query":sparql,"format":"json"},
                          headers={**HEADERS,"Accept":"application/sparql-results+json"}, timeout=15)
        for row in r2.json().get("results",{}).get("bindings",[]):
            qid = row["item"]["value"].split("/")[-1]
            label_map[qid] = row.get("itemLabel",{}).get("value",qid)
            def _y(s):
                m = re.search(r'[+-]?(\d{3,4})-',s); return int(m.group(1)) if m else None
            if qid not in dates_map:
                dates_map[qid] = (_y(row.get("birth",{}).get("value","")),
                                  _y(row.get("death",{}).get("value","")))
            if "viafid" in row:
                viafid = row["viafid"]["value"]
                if qid not in viaf_ids_map:
                    viaf_ids_map[qid] = []
                if viafid not in viaf_ids_map[qid]:
                    viaf_ids_map[qid].append(viafid)
    except Exception: pass
    out = []
    for qid in qids:
        birth, death = dates_map.get(qid,(None,None))
        label = label_map.get(qid, qid)
        viaf_ids = viaf_ids_map.get(qid, [])
        viaf_uri = f"https://viaf.org/viaf/{viaf_ids[0]}" if viaf_ids else None
        s = str_sim(name, label); t = time_score(birth, death, ms_range)
        out.append({"source":"wikidata","label":label,
                    "uri":f"https://www.wikidata.org/wiki/{qid}",
                    "qid":qid,"birth":birth,"death":death,
                    "viaf_uri":viaf_uri,
                    "viaf_ids":viaf_ids,   # liste complète (refcount >= 1, triée)
                    "str_sim":s,"time_score":t,"score":combined(s,t)})
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:TOP_K]

def query_el(name, label, ms_range):
    if label == "auteur":
        viaf = query_viaf(name, ms_range)
        wd   = query_wikidata(name, ms_range)
        return viaf + wd
    elif label == "ouvrage":
        wd   = query_wikidata(name, ms_range)
        viaf = query_viaf(name, ms_range)
        return wd + viaf
    return []

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
os.makedirs(os.path.dirname(VALIDATED_PATH), exist_ok=True)

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/entries")
def api_entries():
    return jsonify([{"entry_id": e["entry_id"], "raw": e["raw"]} for e in gold_data])

@app.route("/api/entry/<int:entry_id>")
def api_entry(entry_id):
    entry = next((e for e in gold_data if e["entry_id"] == entry_id), None)
    if not entry: return jsonify({"error": "not found"}), 404
    result = dict(entry)
    # Ajouter l'état de validation si existant
    result["validated"] = validated.get(entry_id, {})
    return jsonify(result)

@app.route("/api/requery", methods=["POST"])
def api_requery():
    """Re-interroge VIAF + Wikidata pour un span modifié."""
    data = request.json
    text     = data.get("text","").strip()
    label    = data.get("label","auteur")
    ms_range = data.get("ms_range",[0,0])
    norm, method = normalize(text, label)
    results = query_el(norm, label, ms_range)
    return jsonify({"normalized": norm, "norm_method": method, "results": results})

@app.route("/api/validate", methods=["POST"])
def api_validate():
    """Sauvegarde la validation experte — format gold_annotations_with_el.json + CSV."""
    data     = request.json
    entry_id = data.get("entry_id")
    if not entry_id: return jsonify({"success": False})

    validation = data.get("validation", {})
    validated[entry_id] = validation

    # Récupérer l'entrée gold originale
    gold_entry = next((e for e in gold_data if e["entry_id"] == entry_id), {})

    # Construire spans validés (format gold)
    validated_spans = []
    for sv in validation.get("spans", []):
        span = {
            "label":      sv.get("label",""),
            "text":       sv.get("text",""),
            "normalized": sv.get("normalized",""),
            "el_uri":     sv.get("selectedUri") or "",
            "aucun":      sv.get("aucun", False),
            "valid":      sv.get("valid"),          # true/false/null pour date/material/etat
            "expert_validated": True,
        }
        validated_spans.append(span)

    # Construire el_results validés
    validated_el = []
    for sv in validation.get("spans", []):
        if sv.get("label") in ("auteur","ouvrage"):
            validated_el.append({
                "span_text":    sv.get("text",""),
                "label":        sv.get("label",""),
                "normalized":   sv.get("normalized",""),
                "selected_uri": sv.get("selectedUri"),
                "aucun":        sv.get("aucun", False),
            })

    # Record au format gold
    record = {
        "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "entry_id":          entry_id,
        "source_file":       gold_entry.get("source_file",""),
        "raw":               gold_entry.get("raw",""),
        "traduction_fr":     gold_entry.get("traduction_fr",""),
        "ms_century_range":  gold_entry.get("ms_century_range",[]),
        "date_comparison":   gold_entry.get("date_comparison",{}),
        "spans":             validated_spans,
        "el_results":        gold_entry.get("el_results",[]),  # résultats EL originaux
        "el_validated":      validated_el,                      # choix expert
    }

    try:
        # 1. JSONL (append)
        os.makedirs(os.path.dirname(VALIDATED_PATH), exist_ok=True)
        with open(VALIDATED_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # 2. JSON complet (réécriture à chaque save)
        json_path = VALIDATED_PATH.replace(".jsonl", "_full.json")
        all_records = []
        with open(VALIDATED_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    all_records.append(json.loads(line))
        # Dédoublonner par entry_id (garder le dernier)
        seen = {}
        for r in all_records:
            seen[r["entry_id"]] = r
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(list(seen.values()), f, ensure_ascii=False, indent=2)

        # 3. CSV
        csv_path = VALIDATED_PATH.replace(".jsonl", ".csv")
        import csv
        csv_rows = []
        for r in seen.values():
            for sp in r.get("spans",[]):
                csv_rows.append({
                    "entry_id":      r["entry_id"],
                    "raw":           r["raw"],
                    "label":         sp.get("label",""),
                    "text":          sp.get("text",""),
                    "normalized":    sp.get("normalized",""),
                    "el_uri":        sp.get("el_uri",""),
                    "aucun":         sp.get("aucun",""),
                    "valid":         sp.get("valid",""),
                    "traduction_fr": r.get("traduction_fr",""),
                    "ms_century":    f"{r['ms_century_range'][0]}-{r['ms_century_range'][1]}" if r.get("ms_century_range") else "",
                    "timestamp":     r.get("timestamp",""),
                })
        if csv_rows:
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
                w.writeheader()
                w.writerows(csv_rows)

        print(f"[Save] Entrée #{entry_id} validée → JSONL + JSON + CSV")
        return jsonify({"success": True})
    except Exception as e:
        print(f"[WARN] Save failed: {e}")
        return jsonify({"success": False})

@app.route("/api/validated_ids")
def api_validated_ids():
    return jsonify(list(validated.keys()))

# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>PRIMA Expert</title>
<style>
:root{--bg:#ffffff;--surf:#f5f5f0;--surf2:#eeede8;--brd:#d0c8b8;
  --gold:#8a6500;--gdim:#b8920a;--grn:#2e7d4f;--grndim:#1e5234;
  --dim:#6b6355;--txt:#1a1714;--red:#a33000;--orange:#c05a00;
  --blue:#1a5a9a;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--txt);font-family:Georgia,serif;
  min-height:100vh;padding:2rem;max-width:1300px;margin:0 auto;}
h1{color:var(--gold);font-size:2rem;border-bottom:2px solid var(--brd);
  padding-bottom:.6rem;margin-bottom:.6rem;}
.sub{font-style:italic;color:var(--dim);font-size:1.1rem;margin-bottom:1.4rem;
  font-family:monospace;}

/* Navigation */
.nav-bar{display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;
  padding:.7rem 1rem;background:var(--surf);border:1px solid var(--brd);border-radius:6px;}
.nav-btn{background:var(--surf2);color:var(--txt);border:1px solid var(--brd);
  border-radius:4px;padding:.35rem .9rem;font-family:monospace;font-size:.85rem;
  cursor:pointer;}
.nav-btn:hover{border-color:var(--gold);color:var(--gold);}
.nav-btn:disabled{opacity:.4;cursor:not-allowed;}
.nav-progress{font-family:monospace;font-size:.85rem;color:var(--gdim);}
.nav-select{background:var(--surf2);color:var(--txt);border:1px solid var(--brd);
  border-radius:4px;padding:.3rem .5rem;font-family:monospace;font-size:.82rem;}
.validated-badge{background:var(--grn);color:#fff;font-family:monospace;
  font-size:.7rem;padding:.1rem .4rem;border-radius:3px;margin-left:.5rem;}

/* Entry header */
.entry-header{background:var(--surf);border:1px solid var(--brd);border-radius:6px;
  padding:1rem 1.2rem;margin-bottom:1rem;}
.entry-id{color:var(--gdim);font-family:monospace;font-size:.88rem;
  font-weight:bold;margin-bottom:.5rem;}
.entry-raw{font-family:monospace;font-size:.95rem;line-height:1.6;
  margin-bottom:.7rem;color:var(--txt);}
.entry-tr{color:var(--dim);font-size:.9rem;font-style:italic;margin-bottom:.7rem;}

/* Date info */
.date-block{border-radius:4px;padding:.6rem .9rem;margin-bottom:.6rem;
  font-family:monospace;font-size:.85rem;}
.date-coherent{background:#eaf5ee;border:1px solid #a8d5b8;}
.date-incoherent{background:#fdf0ee;border:1px solid #e0b8b0;}
.coherent-badge{color:var(--grn);font-weight:bold;}
.incoherent-badge{color:var(--red);font-weight:bold;}
.date-row{margin-top:.3rem;color:var(--dim);}
.date-val{color:var(--txt);font-weight:bold;}

/* Détails toggle */
.details-btn{background:none;border:1px solid var(--brd);color:var(--dim);
  border-radius:3px;padding:.2rem .7rem;font-size:.8rem;cursor:pointer;
  font-family:monospace;margin-bottom:.6rem;}
.details-btn:hover{color:var(--gold);border-color:var(--gold);}
.details-panel{display:none;background:var(--surf2);border:1px solid var(--brd);
  border-radius:4px;padding:.7rem;font-family:monospace;font-size:.82rem;
  color:var(--dim);margin-bottom:.8rem;line-height:1.7;}
.details-panel.open{display:block;}

/* Spans */
.spans-area{margin-bottom:1.2rem;}
.span-block{background:var(--surf);border:1px solid var(--brd);border-radius:6px;
  padding:1rem 1.2rem;margin-bottom:.9rem;}
.span-header{display:flex;align-items:center;gap:.7rem;margin-bottom:.7rem;flex-wrap:wrap;}
.span-label-badge{font-family:monospace;font-size:.78rem;padding:.15rem .45rem;
  border-radius:3px;font-weight:bold;}
.lbl-auteur{background:#e8f0e0;color:#3a6a1a;border:1px solid #8ab86a;}
.lbl-ouvrage{background:#e0e8f5;color:#1a3a7a;border:1px solid #6a8ab8;}
.lbl-date{background:#f5ece0;color:#7a4a1a;border:1px solid #c0906a;}
.lbl-material{background:#ece0f5;color:#5a1a7a;border:1px solid #9a6ab8;}
.lbl-etat{background:#f5e0ea;color:#7a1a4a;border:1px solid #c06a8a;}
.span-text{font-style:italic;font-size:1rem;color:var(--txt);}
.span-norm{font-family:monospace;font-size:.8rem;color:var(--gdim);}

/* Inputs d'édition */
.edit-row{display:flex;gap:.5rem;align-items:center;margin-top:.5rem;flex-wrap:wrap;}
.edit-input{background:#fff;color:var(--txt);border:1px solid var(--brd);
  border-radius:4px;padding:.3rem .6rem;font-family:monospace;font-size:.85rem;width:230px;}
.edit-input:focus{outline:none;border-color:var(--gold);}
.label-select{background:#fff;color:var(--txt);border:1px solid var(--brd);
  border-radius:4px;padding:.3rem .5rem;font-family:monospace;font-size:.85rem;}
.requery-btn{background:var(--gdim);color:#fff;border:none;border-radius:4px;
  padding:.3rem .9rem;font-family:monospace;font-size:.8rem;cursor:pointer;}
.requery-btn:hover{background:var(--gold);}
.modifier-btn{background:#f0f4ff;color:var(--blue);border:1px solid #b0c0e0;
  border-radius:4px;padding:.25rem .6rem;font-family:monospace;font-size:.78rem;cursor:pointer;}
.modifier-btn:hover{background:#ddeaff;}
.modifier-btn.active{background:var(--blue);color:#fff;border-color:var(--blue);}
.delete-btn{background:#fdf0ee;color:var(--red);border:1px solid #e0b8b0;
  border-radius:4px;padding:.25rem .6rem;font-family:monospace;font-size:.78rem;cursor:pointer;}
.delete-btn:hover{background:#fad8d0;}

/* Validation simple */
.simple-valid{display:flex;gap:.5rem;margin-top:.7rem;align-items:center;}
.vbtn{border:none;border-radius:4px;padding:.35rem .9rem;font-family:monospace;
  font-size:.85rem;cursor:pointer;font-weight:bold;border:1px solid var(--brd);}
.vbtn-ok{background:#eaf5ee;color:var(--grn);}
.vbtn-ok.active{background:var(--grn);color:#fff;border-color:var(--grn);}
.vbtn-ko{background:#fdf0ee;color:var(--red);}
.vbtn-ko.active{background:var(--red);color:#fff;border-color:var(--red);}

/* EL candidates */
.el-section{margin-top:.9rem;}
.el-src-title{font-family:monospace;font-size:1.05rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--txt);font-weight:bold;margin-bottom:.6rem;
  margin-top:.8rem;}
.el-grid{display:grid;grid-template-columns:1fr 1fr;gap:.7rem;}
.el-card{background:var(--surf);border:1px solid var(--brd);border-radius:6px;
  padding:1rem 1.1rem;}
.el-card.selected{border-color:var(--grn);background:#eaf5ee;}
.el-card.rejected{opacity:.5;}
.el-cname{font-size:1.2rem;margin-bottom:.25rem;color:var(--txt);}
.el-rank{color:var(--gdim);font-size:.8rem;margin-right:.35rem;}
.el-dates{font-style:italic;color:var(--dim);font-size:1rem;margin-bottom:.35rem;}
.el-scores{display:flex;gap:1rem;font-family:monospace;font-size:.95rem;margin-bottom:.35rem;}
.sc{display:flex;flex-direction:column;align-items:center;}
.sc span{display:block;color:var(--dim);font-size:.7rem;}
.hi{color:#4caf76;}.mi{color:#e07b3a;}.lo{color:#c94c4c;}
.el-uri{font-family:monospace;font-size:.88rem;word-break:break-all;margin-bottom:.3rem;}
.el-uri a{color:var(--gdim);text-decoration:none;}
.el-uri a:hover{color:var(--gold);}
.el-sources{font-family:monospace;font-size:.72rem;color:var(--dim);margin-bottom:.3rem;
  word-break:break-all;}
.el-viaflink{font-family:monospace;font-size:.75rem;margin-bottom:.3rem;}
.el-viaflink.ok{color:var(--grn);}
.el-viaflink.no{color:var(--red);}
.el-viaflink.dim{color:var(--dim);}
.val-btn{width:100%;margin-top:.5rem;padding:.35rem;border:1px solid var(--brd);
  border-radius:4px;font-family:monospace;font-size:.8rem;cursor:pointer;
  background:var(--surf2);color:var(--dim);}
.val-btn:hover{border-color:var(--gold);color:var(--gold);}
.val-btn.validated{background:var(--grn);color:#fff;border-color:var(--grn);}
.aucun-btn{margin-top:.6rem;width:100%;padding:.3rem;border:1px solid var(--brd);
  border-radius:4px;font-family:monospace;font-size:.78rem;cursor:pointer;
  background:var(--surf2);color:var(--dim);}
.aucun-btn:hover{border-color:var(--red);color:var(--red);}
.aucun-btn.active{background:#fdf0ee;color:var(--red);border-color:var(--red);}
.empty{color:var(--dim);font-style:italic;font-size:1rem;padding:.4rem 0;}

/* Nouveau span */
.add-span-block{background:var(--surf);border:1px dashed var(--brd);border-radius:6px;
  padding:.9rem 1.2rem;margin-bottom:.9rem;}
.add-span-title{font-family:monospace;font-size:.82rem;color:var(--gdim);margin-bottom:.6rem;}
.add-btn{background:var(--grn);color:#fff;border:none;border-radius:4px;
  padding:.35rem 1rem;font-family:monospace;font-size:.82rem;cursor:pointer;}
.add-btn:hover{background:var(--grndim);}

/* Actions */
.actions{display:flex;gap:.8rem;align-items:center;margin-top:1.2rem;
  padding:1rem 1.2rem;background:var(--surf);border:1px solid var(--brd);border-radius:6px;}
.save-btn{background:var(--grn);color:#fff;border:none;border-radius:4px;
  padding:.45rem 1.4rem;font-family:monospace;font-size:.9rem;cursor:pointer;
  font-weight:bold;}
.save-btn:hover{background:var(--grndim);}
.save-status{font-family:monospace;font-size:.82rem;color:var(--gdim);}
</style>
</head>
<body>
<h1>PRIMA Expert</h1>
<p class="sub"><span class="dot" style="display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--grn);margin-right:.4rem;"></span>Validation experte · EL · VIAF + Wikidata · Top-3</p>

<!-- Navigation -->
<div class="nav-bar">
  <button class="nav-btn" id="btn-prev" onclick="navigate(-1)">◀ Précédente</button>
  <button class="nav-btn" id="btn-next" onclick="navigate(1)">Suivante ▶</button>
  <span class="nav-progress" id="nav-progress"></span>
  <select class="nav-select" id="entry-select" onchange="goToEntry(this.value)"></select>
</div>

<!-- Contenu principal -->
<div id="main-content"></div>

<script>
let entries = [];
let currentIdx = 0;
let currentEntry = null;
let spanStates = {}; // {spanIdx: {valid: null/true/false, selectedUri: null/uri}}
let newSpans = [];   // spans ajoutés par l'expert
let validatedIds = new Set();

// ── Initialisation ────────────────────────────────────────────────────────────
async function init() {
  const r = await fetch('/api/entries');
  entries = await r.json();
  const vr = await fetch('/api/validated_ids');
  const vids = await vr.json();
  validatedIds = new Set(vids);

  const sel = document.getElementById('entry-select');
  entries.forEach((e, i) => {
    const opt = document.createElement('option');
    opt.value = i;
    const isVal = validatedIds.has(e.entry_id);
    opt.textContent = `${isVal ? '✓ ' : ''}#${e.entry_id} — ${e.raw.substring(0,50)}…`;
    opt.style.color = isVal ? '#2e7d4f' : '#6b6355';
    opt.style.background = isVal ? '#d4edda' : '';
    opt.style.fontWeight = isVal ? 'bold' : 'normal';
    sel.appendChild(opt);
  });

  updateProgress();
  await loadEntry(0);
}

function updateProgress() {
  document.getElementById('nav-progress').textContent =
    `Entrée ${currentIdx+1} / ${entries.length}  |  Validées: ${validatedIds.size}`;
  document.getElementById('btn-prev').disabled = currentIdx === 0;
  document.getElementById('btn-next').disabled = currentIdx === entries.length - 1;
  document.getElementById('entry-select').value = currentIdx;
  // Mettre à jour les couleurs du select
  const sel = document.getElementById('entry-select');
  Array.from(sel.options).forEach((opt, i) => {
    const eid = entries[i] ? entries[i].entry_id : null;
    const isVal = eid && validatedIds.has(eid);
    opt.style.color = isVal ? '#2e7d4f' : '#6b6355';
    opt.style.fontWeight = isVal ? 'bold' : 'normal';
    // Mettre à jour le préfixe ✓
    const raw = entries[i] ? entries[i].raw.substring(0,50) : '';
    opt.textContent = `${isVal ? '✓ ' : ''}#${eid} — ${raw}…`;
  });
}

async function navigate(dir) {
  const newIdx = currentIdx + dir;
  if (newIdx < 0 || newIdx >= entries.length) return;
  await loadEntry(newIdx);
}

async function goToEntry(idx) {
  await loadEntry(parseInt(idx));
}

async function loadEntry(idx) {
  currentIdx = idx;
  spanStates = {};
  newSpans = [];
  const eid = entries[idx].entry_id;
  const r = await fetch(`/api/entry/${eid}`);
  currentEntry = await r.json();
  renderEntry();
  updateProgress();
}

// ── Rendu principal ────────────────────────────────────────────────────────────
function renderEntry() {
  if (!currentEntry) return;
  const e = currentEntry;
  const isValidated = validatedIds.has(e.entry_id);
  let html = '';

  // En-tête
  html += `<div class="entry-header">`;
  html += `<div class="entry-id">Entrée #${e.entry_id} — ${e.source_file||''}`;
  if (isValidated) html += `<span class="validated-badge">✓ Validée</span>`;
  html += `</div>`;
  html += `<div class="entry-raw" id="entry-raw-text" style="cursor:text;user-select:text;" onmouseup="onRawSelect()">${e.raw||''}</div>`;
  if (e.traduction_fr)
    html += `<div class="entry-tr">🇫🇷 ${e.traduction_fr}</div>`;

  // Date info
  const dc = e.date_comparison || {};
  if (dc.date_from_text || dc.date_from_json) {
    const coh = dc.coherent;
    html += `<div class="date-block ${coh?'date-coherent':'date-incoherent'}">`;
    html += `<span class="${coh?'coherent-badge':'incoherent-badge'}">${coh?'✓ Dates cohérentes':'✗ Dates incohérentes'}</span>`;
    if (dc.date_from_text)
      html += `<div class="date-row">Texte : <span class="date-val">${dc.date_from_text}</span>${dc.date_from_text_norm?' → '+dc.date_from_text_norm:''}</div>`;
    if (dc.date_from_json)
      html += `<div class="date-row">JSON  : <span class="date-val">${dc.date_from_json}</span>${dc.date_from_json_norm?' → '+dc.date_from_json_norm:''}</div>`;
    html += `</div>`;
  }

  // Bouton détails supprimé — infos intégrées dans les spans
  html += `</div>`; // entry-header

  // Spans — ordre : etat, material, date, auteur, ouvrage
  const SPAN_ORDER = ['etat','material','date','auteur','ouvrage'];
  const sortedSpans = [...(e.spans || [])].sort((a,b) => {
    const ai = SPAN_ORDER.indexOf(a.label); const bi = SPAN_ORDER.indexOf(b.label);
    return (ai===-1?99:ai) - (bi===-1?99:bi);
  });
  // Ajouter un span — avant la liste des spans existants
  html += `<div class="add-span-block">`;
  html += `<div class="add-span-title">+ Ajouter un span</div>`;
  html += `<div class="edit-row">`;
  html += `<input class="edit-input" id="new-span-text" placeholder="Texte du span…">`;
  html += `<select class="label-select" id="new-span-label">`;
  ['auteur','ouvrage','date','material','etat'].forEach(l =>
    { html += `<option value="${l}">${l}</option>`; });
  html += `</select>`;
  html += `<button class="add-btn" onclick="addSpan()">Ajouter</button>`;
  html += `</div>`;
  // Nouveaux spans ajoutés — avec bouton Supprimer
  if (newSpans.length > 0) {
    html += `<div style="margin-top:.7rem;border-top:1px solid var(--brd);padding-top:.6rem;">`;
    newSpans.forEach((span, i) => {
      html += `<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.35rem;font-family:monospace;font-size:.85rem;">`;
      html += `<span class="span-label-badge lbl-${span.label}">${span.label}</span>`;
      html += `<span style="font-style:italic;">"${span.text}"</span>`;
      html += `<button class="delete-btn" data-newi="${i}"
        onclick="deleteNewSpan(this.dataset.newi)">✕ Supprimer</button>`;
      html += `</div>`;
    });
    html += `</div>`;
  }
  html += `</div>`;

  // Debug panel spanStates — après Ajouter un span
  html += `<div style="margin-bottom:.8rem;">`;
  html += `<button onclick="toggleDebug()" style="background:none;border:1px solid var(--brd);color:var(--dim);border-radius:3px;padding:.2rem .7rem;font-size:.78rem;font-family:monospace;cursor:pointer;">🔍 Voir spanStates</button>`;
  html += `<div id="debug-panel" style="display:none;margin-top:.4rem;background:#f8f7f2;border:1px solid var(--brd);border-radius:4px;padding:.7rem;font-family:monospace;font-size:.75rem;white-space:pre-wrap;color:var(--dim);max-height:200px;overflow:auto;"></div>`;
  html += `</div>`;

  // Spans existants
  html += `<div class="spans-area" id="spans-area">`;
  sortedSpans.forEach((span) => {
    const key = span.label + '||' + span.text;
    html += renderSpan(span, key, e);
  });
  html += `</div>`;

  // Actions
  html += `<div class="actions">`;
  html += `<button class="save-btn" onclick="saveValidation()">Sauvegarder</button>`;
  html += `<span class="save-status" id="save-status"></span>`;
  html += `</div>`;

  document.getElementById('main-content').innerHTML = html;
  refreshDebug();
}

function renderSpan(span, idx, entry, isNew=false) {
  const lblClass = `lbl-${span.label}`;
  const key = String(idx);
  const state = spanStates[key] || {valid: null, selectedUri: null, aucun: false};
  const msRange = entry.ms_century_range || [0,0];
  let html = `<div class="span-block" id="span-block-${idx}">`;

  // Header
  html += `<div class="span-header">`;
  html += `<span class="span-label-badge ${lblClass}">${span.label}</span>`;
  html += `<span class="span-text">"${span.text}"</span>`;
  if (span.normalized && span.normalized !== span.text)
    html += `<span class="span-norm">→ ${span.normalized}</span>`;
  if (!isNew) {
    html += `<button class="delete-btn" data-spankey="${idx.replace(/"/g,'&quot;')}"
      onclick="deleteSpan(this.dataset.spankey)">✕ Supprimer</button>`;
    html += `<button class="modifier-btn" data-spankey="${idx.replace(/"/g,'&quot;')}"
      onclick="activateModify(this.dataset.spankey)"
      title="Sélectionnez un texte dans l'entrée pour modifier ce span">✎ Modifier</button>`;
  }
  html += `</div>`;

  // Édition — Re-interroger seulement pour auteur/ouvrage
  html += `<div class="edit-row">`;
  html += `<input class="edit-input" id="edit-text-${idx}" value="${span.text}" placeholder="Texte…" readonly style="opacity:.7;cursor:not-allowed;">`;
  html += `<select class="label-select" id="edit-label-${idx}">`;
  ['auteur','ouvrage','date','material','etat'].forEach(l =>
    { html += `<option value="${l}"${l===span.label?' selected':''}>${l}</option>`; });
  html += `</select>`;
  if (['auteur','ouvrage'].includes(span.label)) {
    html += `<button class="requery-btn"
      data-spankey="${idx.replace(/"/g,'&quot;')}"
      data-msrange="${JSON.stringify(msRange).replace(/"/g,'&quot;')}"
      onclick="requery(this.dataset.spankey, JSON.parse(this.dataset.msrange))">↺ Re-interroger</button>`;
  }
  html += `</div>`;

  // Validation selon le type
  if (['auteur','ouvrage'].includes(span.label)) {
    // EL candidates depuis el_results
    const elData = (entry.el_results || []).find(r => r.span_text === span.text);
    const candidates = elData ? elData.el_results : [];
    const viafCands = candidates.filter(c => c.source === 'viaf');
    const wdCands   = candidates.filter(c => c.source === 'wikidata');
    const total = candidates.length;

    html += `<div class="el-section" id="el-section-${idx}">`;
    // nominatif + method (comme dans prima_monitor)
    const elMeta = (entry.el_results || []).find(r => r.span_text === span.text);
    if (elMeta && elMeta.normalized && elMeta.normalized !== span.text)
      html += `<div class="qnorm" style="font-family:monospace;font-size:1rem;color:var(--gdim);margin-bottom:.15rem;">nominatif: ${elMeta.normalized}</div>`;
    if (elMeta && elMeta.norm_method) {
      const methodLabels = {
        'genitif_exact': 'génitif latin : nominatif (correspondance exacte)',
        'nom_contains':  'nominatif trouvé par inclusion',
        'fallback':      'requête directe : aucune normalisation',
      };
      const methodDisplay = methodLabels[elMeta.norm_method] || elMeta.norm_method;
      html += `<div class="method" style="font-family:monospace;font-size:.85rem;color:var(--gdim);margin-bottom:.6rem;">méthode: ${methodDisplay}</div>`;
    }
    // Ligne "N candidats pour 'xxx'" comme dans prima_monitor
    html += `<div style="font-family:monospace;font-size:1.05rem;color:var(--gdim);
      font-weight:bold;margin-bottom:.7rem;margin-top:.5rem;">`;
    html += total > 0
      ? `${total} candidat${total>1?'s':''} pour '${span.normalized||span.text}'`
      : `Aucun candidat pour '${span.normalized||span.text}'`;
    html += `</div>`;
    // Injecter les URIs VIAF dans state pour le cross-match côté WD
    state._viafCandUris = viafCands.map(c => c.uri);
    html += renderCandidates(viafCands, 'VIAF', idx, state);
    html += renderCandidates(wdCands, 'Wikidata', idx, state);
    html += `<button class="aucun-btn ${state.aucun?'active':''}"
      data-spankey="${idx.replace(/"/g,'&quot;')}"
      onclick="setAucun(this.dataset.spankey)">
      Aucun résultat correct</button>`;
    const hasSelection = !!(state.viafUri || state.wdUri || state.aucun);
    html += `<button class="val-btn ${hasSelection?'validated':''}"
      style="margin-top:.6rem;width:100%;"
      data-spankey="${idx.replace(/"/g,'&quot;')}"
      onclick="confirmEntity(this.dataset.spankey)">
      ${hasSelection ? '✓ Validé' : 'Valider'}</button>`;
    html += `</div>`;
  } else {
    // Simple Valider
    html += `<div class="simple-valid">`;
    html += `<button class="vbtn vbtn-ok ${state.valid===true?'active':''}"
      data-spankey="${idx.replace(/"/g,'&quot;')}" data-val="true"
      onclick="setSimpleValid(this.dataset.spankey, true)">✓ Valider</button>`;
    html += `</div>`;
  }

  html += `</div>`; // span-block
  return html;
}

function renderCandidates(candidates, source, spanIdx, state) {
  const srcKey = source === 'VIAF' ? 'viafUri' : 'wdUri';
  const selectedUri = state[srcKey] || null;
  let html = `<div class="el-src-title">${source}</div>`;
  if (!candidates.length) {
    html += `<div style="font-family:monospace;font-size:.8rem;color:var(--dim);margin-bottom:.5rem;">no results</div>`;
    return html;
  }
  html += `<div class="el-grid">`;
  candidates.forEach((c, i) => {
    const isSelected = selectedUri === c.uri;
    const isRejected = selectedUri && selectedUri !== c.uri;
    const d = (c.birth||c.death) ? `${c.birth||'?'}–${c.death||'?'}` : 'dates unknown';
    const spanKeyEnc = spanIdx.replace(/"/g,'&quot;');
    const uriEnc = c.uri.replace(/"/g,'&quot;');
    html += `<div class="el-card ${isSelected?'selected':''} ${isRejected&&!isSelected?'rejected':''}"
      style="cursor:pointer;"
      data-spankey="${spanKeyEnc}"
      data-uri="${uriEnc}"
      data-src="${source}"
      onclick="selectCandidateCard(this)">`;
    html += `<div class="el-cname"><span style="color:var(--dim);font-size:.75rem;">#${i+1} </span>${c.label}</div>`;
    html += `<div class="el-dates">${d}</div>`;
    html += `<div class="el-scores">`;
    html += `<div class="sc ${sc(c.str_sim)}">${c.str_sim.toFixed(2)}<span>str</span></div>`;
    html += `<div class="sc ${sc(c.time_score)}">${c.time_score.toFixed(2)}<span>tps</span></div>`;
    html += `<div class="sc ${sc(c.score)}"><b>${c.score.toFixed(2)}</b><span>score</span></div>`;
    html += `</div>`;
    html += `<div class="el-uri"><a href="${c.uri}" target="_blank" onclick="event.stopPropagation()">${c.uri}</a></div>`;
    if (c.source==='viaf' && c.sources && c.sources.length)
      html += `<div class="el-sources">sources: ${c.sources.slice(0,8).join(' · ')}${c.sources.length>8?' …':''}</div>`;
    if (c.source==='wikidata') {
      if (c.source === 'wikidata') {
        if (c.viaf_ids && c.viaf_ids.length > 0) {
          // Comparer avec les URIs des candidats VIAF
          const viafUris = (state._viafCandUris || []);
          c.viaf_ids.forEach((vid, vi) => {
            const uri = `https://viaf.org/viaf/${vid}`;
            const matchIdx = viafUris.indexOf(uri);
            const matched = matchIdx >= 0;
            html += `<div class="el-viaflink ${matched?'ok':'dim'}">`;
            if (matched) {
              html += `✓ VIAF cluster = candidat VIAF #${matchIdx+1} : `;
            } else {
              html += `· P214 : `;
            }
            html += `<a href="${uri}" target="_blank" onclick="event.stopPropagation()">${uri}</a>`;
            html += `</div>`;
          });
        } else {
          html += `<div class="el-viaflink no">✗ pas de lien VIAF (P214 absent ou deprecated)</div>`;
        }
      }
    }
    html += `</div>`;
  });
  html += `</div>`;
  return html;
}

function sc(v){return v>=0.7?'hi':v>=0.4?'mi':'lo';}

// ── Interactions ──────────────────────────────────────────────────────────────
function toggleDetails() {
  const p = document.getElementById('details-panel');
  p.classList.toggle('open');
}

function selectCandidateCard(el) {
  const spanIdx = el.dataset.spankey;
  const uri = el.dataset.uri;
  const src = el.dataset.src; // 'VIAF' ou 'Wikidata'
  const key = String(spanIdx);
  if (!spanStates[key]) spanStates[key] = {};
  const srcKey = src === 'VIAF' ? 'viafUri' : 'wdUri';
  // Toggle : re-clic sur le même = désélection
  if (spanStates[key][srcKey] === uri) {
    spanStates[key][srcKey] = null;
  } else {
    spanStates[key][srcKey] = uri;
    spanStates[key].aucun = false;
  }
  // selectedUri = priorité VIAF, sinon WD (pour compatibilité avec sauvegarde)
  spanStates[key].selectedUri = spanStates[key].viafUri || spanStates[key].wdUri || null;
  renderEntry();
}

function confirmSource(spanIdx, src) {
  // Le bouton Valider sous le groupe confirme la sélection (visuellement déjà faite)
  // Pas d'action supplémentaire nécessaire, la sélection est déjà dans spanStates
  // On peut juste re-render pour feedback visuel
  renderEntry();
}

function selectCandidate(spanIdx, uri) {
  // Compatibilité ancienne API (non utilisée mais conservée)
  const key = String(spanIdx);
  if (!spanStates[key]) spanStates[key] = {};
  spanStates[key].selectedUri = spanStates[key].selectedUri === uri ? null : uri;
  spanStates[key].aucun = false;
  renderEntry();
}

function confirmEntity(spanIdx) {
  renderEntry();
}

function setAucun(spanIdx) {
  const key = String(spanIdx);
  if (!spanStates[key]) spanStates[key] = {};
  spanStates[key].aucun = !spanStates[key].aucun;
  if (spanStates[key].aucun) spanStates[key].selectedUri = null;
  renderEntry();
}

function setSimpleValid(spanIdx, val) {
  const key = String(spanIdx);
  if (!spanStates[key]) spanStates[key] = {};
  spanStates[key].valid = spanStates[key].valid === val ? null : val;
  renderEntry();
}

let modifyTarget = null; // {spanKey, type:'existing'|'new'} ou null = mode Ajouter

function onRawSelect() {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed) return;
  // Nettoyer : supprimer sauts de ligne et espaces multiples
  const txt = sel.toString().split(String.fromCharCode(10)).join(' ').split(String.fromCharCode(13)).join(' ').replace(/  +/g,' ').trim();
  if (!txt) return;

  if (modifyTarget) {
    // Mode Modifier : mettre à jour le span ciblé
    const {spanKey} = modifyTarget;
    const inputEl = document.getElementById(`edit-text-${spanKey}`);
    if (inputEl) {
      inputEl.value = txt;
      // Mettre à jour le span dans currentEntry
      if (String(spanKey).startsWith('new_')) {
        const i = parseInt(spanKey.replace('new_',''));
        if (newSpans[i]) newSpans[i].text = txt;
      } else {
        const [label, oldText] = spanKey.split('||');
        const sp = (currentEntry.spans||[]).find(s => s.label===label && s.text===oldText);
        if (sp) sp.text = txt;
      }
      // Flash visuel sur le span ciblé
      const block = document.getElementById(`span-block-${spanKey}`);
      if (block) { block.style.outline = '2px solid var(--gold)'; setTimeout(()=>{block.style.outline='';},1500); }
    }
    modifyTarget = null;
    // Réinitialiser le curseur
    document.getElementById('entry-raw-text').style.cursor = 'text';
    document.querySelectorAll('.modifier-btn').forEach(b => b.classList.remove('active'));
    renderEntry();
  } else {
    // Mode Ajouter : remplir le champ new-span-text
    const input = document.getElementById('new-span-text');
    if (input) {
      input.value = txt;
      input.style.borderColor = 'var(--gold)';
      setTimeout(() => { input.style.borderColor = ''; }, 1500);
    }
  }
}

function activateModify(spanKey) {
  modifyTarget = {spanKey};
  // Curseur crosshair pour indiquer le mode sélection
  const rawEl = document.getElementById('entry-raw-text');
  if (rawEl) rawEl.style.cursor = 'crosshair';
  // Mettre le bouton en actif
  document.querySelectorAll('.modifier-btn').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`.modifier-btn[data-spankey="${spanKey}"]`);
  if (btn) btn.classList.add('active');
}

function toggleDebug() {
  const panel = document.getElementById('debug-panel');
  if (!panel) return;
  if (panel.style.display === 'none') {
    panel.style.display = 'block';
    panel.textContent = JSON.stringify(spanStates, null, 2);
  } else {
    panel.style.display = 'none';
  }
}

function refreshDebug() {
  const panel = document.getElementById('debug-panel');
  if (panel && panel.style.display !== 'none') {
    panel.textContent = JSON.stringify(spanStates, null, 2);
  }
}

function deleteNewSpan(i) {
  newSpans.splice(parseInt(i), 1);
  renderEntry();
}

function deleteSpan(spanKey) {
  if (!confirm('Supprimer ce span ?')) return;
  if (String(spanKey).startsWith('new_')) {
    const i = parseInt(spanKey.replace('new_',''));
    newSpans.splice(i, 1);
  } else {
    // spanKey = "label||text"
    const [label, text] = spanKey.split('||');
    const idx = (currentEntry.spans||[]).findIndex(s => s.label===label && s.text===text);
    if (idx >= 0) currentEntry.spans.splice(idx, 1);
  }
  renderEntry();
}

async function requery(spanKey, msRange) {
  const textEl  = document.getElementById(`edit-text-${spanKey}`);
  const labelEl = document.getElementById(`edit-label-${spanKey}`);
  if (!textEl || !labelEl) return;
  const text  = textEl.value.trim();
  const label = labelEl.value;

  // Afficher SEARCHING
  const elSection = document.getElementById(`el-section-${spanKey}`);
  if (elSection) elSection.innerHTML = '<div style="font-family:monospace;font-size:.9rem;color:var(--gdim);padding:.5rem 0;">🔍 SEARCHING…</div>';

  // Mettre à jour le span local
  if (String(spanKey).startsWith('new_')) {
    const i = parseInt(spanKey.replace('new_',''));
    newSpans[i] = {...newSpans[i], text, label};
  } else {
    const [oldLabel, oldText] = spanKey.split('||');
    const idx = (currentEntry.spans||[]).findIndex(s => s.label===oldLabel && s.text===oldText);
    if (idx >= 0) currentEntry.spans[idx] = {...currentEntry.spans[idx], text, label};
  }

  // Re-interroger le backend
  const r = await fetch('/api/requery', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({text, label, ms_range: msRange})
  });
  const data = await r.json();

  // Mettre à jour el_results dans currentEntry
  if (!currentEntry.el_results) currentEntry.el_results = [];
  const existing = currentEntry.el_results.findIndex(r => r.span_text === text);
  const newEl = {span_text: text, label, normalized: data.normalized,
                 norm_method: data.norm_method, el_results: data.results};
  if (existing >= 0) currentEntry.el_results[existing] = newEl;
  else currentEntry.el_results.push(newEl);

  // Reset validation pour ce span
  const newKey = label + '||' + text;
  spanStates[newKey] = {};
  renderEntry();
}

async function addSpan() {
  const text  = document.getElementById('new-span-text').value.trim();
  const label = document.getElementById('new-span-label').value;
  if (!text) return;
  const span = {text, label, normalized: text};
  newSpans.push(span);
  renderEntry();
  // Auto-requery
  const idx = `new_${newSpans.length-1}`;
  const msRange = currentEntry.ms_century_range || [0,0];
  await requery(idx, msRange);
}

async function saveValidation() {
  const btn = document.getElementById('save-status');
  // Construire l'objet de validation
  const spans = [...(currentEntry.spans||[]), ...newSpans];
  const validation = {
    spans: spans.map((span) => {
      const key = span.label + '||' + span.text;
      const st = spanStates[key] || {};
      return {
        text:        span.text,
        label:       span.label,
        normalized:  span.normalized || span.text,
        selectedUri: st.selectedUri || null,
        aucun:       st.aucun || false,
        valid:       st.valid !== undefined ? st.valid : null,
      };
    }),
    newSpans: newSpans.map((s,i) => ({...s, ...spanStates[`new_${i}`]})),
    notes: '',
  };

  const r = await fetch('/api/validate', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({entry_id: currentEntry.entry_id, validation})
  });
  const data = await r.json();
  if (data.success) {
    validatedIds.add(currentEntry.entry_id);
    btn.textContent = '✓ Sauvegardé';
    btn.style.color = '#4caf76';
    updateProgress();
    setTimeout(async () => {
      btn.textContent = '';
      if (currentIdx < entries.length - 1) await navigate(1);
    }, 800);
  } else {
    btn.textContent = '✗ Erreur';
    btn.style.color = '#c94c4c';
  }
}

init();
</script>
</body>
</html>"""

if __name__ == "__main__":
    os.makedirs(os.path.dirname(VALIDATED_PATH), exist_ok=True)
    print("=" * 55)
    print("  PRIMA Monitor — Version Expert (Remaining)")
    print(f"  Interface : http://localhost:{PORT}")
    print(f"  Données   : {GOLD_PATH}")
    print(f"  Sortie    : {VALIDATED_PATH}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=PORT, debug=False)
