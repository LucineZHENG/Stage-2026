#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prima_monitor_remaining.py
==========================
Polling service: checks INCEpTION every 2 seconds,
detects new auteur/ouvrage spans, normalizes to nominative form,
queries VIAF + Wikidata, displays results at http://localhost:5051,
and saves EL results to el_results_realtime.jsonl.

Project  : PRIMA-remaining (PROJECT_ID=2, DOCUMENT_ID=29)

Usage:
    python3 prima_monitor_remaining.py

Dependencies:
    pip install flask requests
"""

import difflib as _difflib
import io
import json
import os
import re
import threading
import time
import zipfile
from datetime import datetime

import requests
from flask import Flask, jsonify, render_template_string

INCEPTION_BASE = "http://localhost:8080"
INCEPTION_AUTH = ("admin", "Zrx12345")
PROJECT_ID     = 2
DOCUMENT_ID    = 29
ANNOTATOR      = "admin"
CAT_DICT_PATH  = "./catalogue_dict.json"
EL_SAVE_PATH   = "./output_remaining/el_auteur_ouvrage_remaining.jsonl"

POLL_INTERVAL  = 2
TOP_K          = 3
PORT           = 5051

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

# 三个查找表，从 catalogue_dict.json 加载
# | Trois tables de correspondance chargées depuis catalogue_dict.json
#
# GENITIF_TO_NOM    : 拉丁语作者属格 → 主格  | auteur latin génitif → nominatif
#                     例 "cencii camerarii" → "Cencius Camerarius"
# NOM_CONTAINS      : 意大利语作者主格列表（无属格变化）| auteurs italiens (sans génitif)
#                     例 ("iacopo passavanti", "Iacopo Passavanti")
# OUVRAGE_GEN_TO_NOM: 作品名属格 → 主格  | ouvrage génitif → nominatif
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
            if _ag:
                GENITIF_TO_NOM[_ag.lower()] = _an
            else:
                NOM_CONTAINS.append((_an.lower(), _an))
        _og = (_val.get("ouvrage_genitif")  or "").strip()
        _on = (_val.get("ouvrage_nominatif") or "").strip()
        if _og and _on:
            OUVRAGE_GEN_TO_NOM[_og.lower()] = _on
    print(f"[Init] Dictionary: {len(GENITIF_TO_NOM)} latin authors, "
          f"{len(NOM_CONTAINS)} italian authors, "
          f"{len(OUVRAGE_GEN_TO_NOM)} works")
except Exception as e:
    print(f"[WARN] Cannot load catalogue_dict.json: {e}")


def normalize(text: str, label: str) -> tuple:
    """
    将标注文本规范化为主格形式，返回 (查询词, 方法说明)。
    | Normalise le texte annoté en forme nominative, retourne (terme_requête, méthode).

    auteur 查询逻辑 | Logique pour auteur :
      1. 精确匹配 genitif → nominatif（拉丁语）| correspondance exacte génitif latin
      2. nominatif 包含标注文本（意大利语，无 genitif）| nominatif contient le texte (italien)
      3. 找不到则用原文 | fallback : texte original

    ouvrage 查询逻辑 | Logique pour ouvrage :
      1. 精确匹配 ouvrage_genitif → nominatif
      2. 找不到则用原文 | fallback : texte original
    """
    key = text.strip().lower()
    if label == "auteur":
        if key in GENITIF_TO_NOM:
            return GENITIF_TO_NOM[key], "genitif_exact"
        for nom_lower, nom_original in NOM_CONTAINS:
            if key in nom_lower:
                return nom_original, "nom_contains"
        return text.strip(), "fallback"
    elif label == "ouvrage":
        if key in OUVRAGE_GEN_TO_NOM:
            return OUVRAGE_GEN_TO_NOM[key], "genitif_exact"
        return text.strip(), "fallback"
    return text.strip(), "fallback"


state = {
    "last_span_ids": set(),
    "current_query": None,
    "normalized":    None,
    "norm_method":   None,
    "label":         None,
    "entry_id":      None,
    "raw_line":      None,
    "results":       [],
    "entry_cache":   {},   # {span_text: {label, results, normalized, norm_method}}
    "ms_range":      (0, 0),
    "updated_at":    None,
    "status":        "Waiting for annotations...",
    # Cache entrée courante | Cache de l'entrée courante
    "current_entry": {
        "entry_id": None,
        "raw":      None,
        "ms_range": (0, 0),
        "annotations": {},
    },
}
lock = threading.Lock()


def str_sim(a, b):
    return round(_difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio(), 3)

def time_score(birth, death, ms_range):
    if not ms_range or ms_range == (0, 0): return 0.0
    ms_start, ms_end = ms_range
    if birth is None and death is None: return 0.0
    if death is not None:
        if death <= ms_end:      return 1.0
        if death <= ms_end + 50: return 0.7
        return 0.1
    if birth is not None:
        if birth > ms_end:       return 0.0
        if birth >= ms_start:    return 0.8
        return 0.6
    return 0.0

def combined(s, t):
    if t == 0.0: return round(0.7 * s, 3)
    return round(0.4 * s + 0.6 * t, 3)


_NER_PAT  = re.compile(
    r'<[^>]*NER_PRIMA[^>]+begin="(\d+)"[^>]+end="(\d+)"[^>]+label="([^"]*)"[^>]*/?>',
    re.IGNORECASE)
_SAEC_PAT = re.compile(r'(?:S[ae]{1,2}c(?:ulo)?|Sec(?:olo)?)\.?\s+([ivxlcdm]+)', re.IGNORECASE)


def fetch_xmi_spans():
    url = (f"{INCEPTION_BASE}/api/aero/v1/projects/{PROJECT_ID}"
           f"/documents/{DOCUMENT_ID}/annotations/{ANNOTATOR}")
    try:
        r   = requests.get(url, auth=INCEPTION_AUTH,
                           params={"format": "xmi"}, timeout=8)
        if r.status_code != 200: return [], ""
        z   = zipfile.ZipFile(io.BytesIO(r.content))
        xmi = z.read("admin.xmi").decode("utf-8")
    except Exception:
        return [], ""

    tm = re.search(r'cas:Sofa[^>]*sofaString="(.*?)"(?:\s*/?>|\s+\w)', xmi, re.DOTALL)
    if not tm: return [], ""
    full_text = (tm.group(1)
                 .replace("&#10;", "\n").replace("&#13;", "\r")
                 .replace("&amp;", "&").replace("&lt;", "<")
                 .replace("&gt;", ">").replace("&quot;", '"'))

    spans = []
    for m in _NER_PAT.finditer(xmi):
        begin = int(m.group(1)); end = int(m.group(2)); label = m.group(3)
        span_text = full_text[begin:end] if end <= len(full_text) else ""
        if not span_text or label not in ("auteur", "ouvrage"): continue
        ls = full_text.rfind("\n", 0, begin) + 1
        le = full_text.find("\n", end); le = le if le != -1 else len(full_text)
        line = full_text[ls:le]
        ms_range = (0, 0)
        sm = _SAEC_PAT.search(line)
        if sm: ms_range = CENTURY_MAP.get(sm.group(1).lower(), (0, 0))
        spans.append({"id": f"{begin}-{end}-{label}", "begin": begin,
                      "end": end, "text": span_text, "label": label,
                      "ms_range": ms_range})
    return spans, full_text


# 正则：从 displayForm 解析生卒年
# 处理 "1240?-1292?", "approximately 1240-approximately 1292", "1363-1429" 等格式
# | Regex pour extraire naissance-mort depuis displayForm VIAF
_VIAF_DATE_PAT = re.compile(
    r'(?:approximately\s+)?(\d{3,4})\??[-–]\s*(?:approximately\s+)?(\d{3,4})'
)


def query_viaf(name, ms_range):
    """
    Étape 1 : AutoSuggest → viafid + displayForm (dédoublonnage par viafid)
    Étape 2 : viaf.json → birthDate / deathDate + sources (bibliothèques contributives)
    """
    try:
        r = requests.get(VIAF_SUGGEST, params={"query": name},
                         headers={**HEADERS, "Accept": "application/json"}, timeout=10)
        r.raise_for_status()
        results = r.json().get("result", []) or []
    except Exception:
        return []

    persons = [x for x in results if x.get("nametype") == "personal"]

    # Dédoublonnage par viafid : garder la première occurrence de chaque cluster
    seen_viafids = set()
    unique_persons = []
    for p in persons:
        vid = p.get("viafid", "")
        if vid and vid not in seen_viafids:
            seen_viafids.add(vid)
            unique_persons.append(p)
    persons = unique_persons[:TOP_K + 2]

    if not persons:
        return []

    out = []
    for person in persons:
        viafid = person.get("viafid", "")
        label  = person.get("displayForm", name)
        if not viafid:
            continue

        # Étape 2 : récupérer dates + sources via https://viaf.org/viaf/{id} (Accept: application/json)
        birth, death = None, None
        sources = []
        try:
            r2 = requests.get(
                f"https://viaf.org/viaf/{viafid}",
                headers={**HEADERS, "Accept": "application/json"}, timeout=8)
            if r2.status_code == 200:
                cluster = r2.json().get("ns1:VIAFCluster", {})
                # Dates : format "354-11-13" ou "430-08-28"
                bm = re.search(r'(\d{3,4})', str(cluster.get("ns1:birthDate", "")))
                dm = re.search(r'(\d{3,4})', str(cluster.get("ns1:deathDate", "")))
                if bm: birth = int(bm.group(1))
                if dm: death = int(dm.group(1))
                # Sources : ns1:sources.ns1:source[].content = "BNF|12345"
                raw = cluster.get("ns1:sources", {})
                src_list = raw.get("ns1:source", [])
                if isinstance(src_list, dict):
                    src_list = [src_list]
                seen = set()
                for item in src_list:
                    content = str(item.get("content", ""))
                    lib = content.split("|")[0].strip()
                    if lib and lib not in seen:
                        seen.add(lib)
                        sources.append(lib)
        except Exception:
            pass

        s = str_sim(name, label)
        t = time_score(birth, death, ms_range)
        out.append({"source": "viaf", "label": label,
                    "uri": f"https://viaf.org/viaf/{viafid}",
                    "birth": birth, "death": death,
                    "sources": sources,
                    "str_sim": s, "time_score": t, "score": combined(s, t)})

    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:TOP_K]


def query_wikidata(name, ms_range):
    # 两步查询：wbsearchentities 获取 QID → SPARQL 获取生卒年 + tous les P214
    try:
        r = requests.get(WD_URL, params={
            "action": "wbsearchentities", "search": name,
            "language": "la", "fallbacklanguage": "fr",
            "type": "item", "limit": 8, "format": "json",
        }, headers=HEADERS, timeout=10)
        r.raise_for_status()
        qids = [x["id"] for x in r.json().get("search", [])[:8]]
    except Exception:
        return []
    if not qids: return []
    # SPARQL : toutes les valeurs P214 sans filtrage
    sparql = f"""
SELECT ?item ?itemLabel ?birth ?death ?viafid WHERE {{
  VALUES ?item {{ {" ".join(f"wd:{q}" for q in qids)} }}
  OPTIONAL {{ ?item wdt:P569 ?birth. }}
  OPTIONAL {{ ?item wdt:P570 ?death. }}
  OPTIONAL {{ ?item wdt:P214 ?viafid. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "la,fr,en". }}
}}"""
    dates_map = {}; label_map = {}
    viaf_ids_map = {}  # qid -> [viafid, ...]
    try:
        r2 = requests.get(WD_SPARQL, params={"query": sparql, "format": "json"},
                          headers={**HEADERS, "Accept": "application/sparql-results+json"},
                          timeout=12)
        for row in r2.json().get("results", {}).get("bindings", []):
            qid = row["item"]["value"].split("/")[-1]
            label_map[qid] = row.get("itemLabel", {}).get("value", qid)
            def _y(s):
                m = re.search(r'[+-]?(\d{3,4})-', s); return int(m.group(1)) if m else None
            if qid not in dates_map:
                dates_map[qid] = (_y(row.get("birth",{}).get("value","")),
                                  _y(row.get("death",{}).get("value","")))
            if "viafid" in row:
                viafid = row["viafid"]["value"]
                if qid not in viaf_ids_map:
                    viaf_ids_map[qid] = []
                if viafid not in viaf_ids_map[qid]:
                    viaf_ids_map[qid].append(viafid)
    except Exception:
        pass
    out = []
    for qid in qids:
        birth, death = dates_map.get(qid, (None, None))
        label = label_map.get(qid, qid)
        viaf_ids = viaf_ids_map.get(qid, [])
        viaf_uri = f"https://viaf.org/viaf/{viaf_ids[0]}" if viaf_ids else None
        s = str_sim(name, label); t = time_score(birth, death, ms_range)
        out.append({"source": "wikidata", "label": label,
                    "uri": f"https://www.wikidata.org/wiki/{qid}",
                    "qid": qid, "birth": birth, "death": death,
                    "viaf_uri": viaf_uri,
                    "viaf_ids": viaf_ids,
                    "str_sim": s, "time_score": t, "score": combined(s, t)})
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:TOP_K]


def save_el_result(raw_line, span_text, normalized, norm_method,
                   label, ms_range, results):
    # 将 EL 查询结果追加写入 JSONL 文件
    # 结构：整条原文在上，下面是标注的 auteur/ouvrage 及 EL 结果
    # | Structure : texte brut de l'entrée, puis span annoté et résultats EL
    import os
    os.makedirs(os.path.dirname(EL_SAVE_PATH), exist_ok=True)
    record = {
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_entry":   raw_line,          # 整条原文 | texte brut complet
        "ms_range":    list(ms_range),
        "annotation": {
            "label":       label,         # auteur 或 ouvrage
            "span_text":   span_text,     # 标注的原文词 | texte annoté
            "normalized":  normalized,    # 规范化主格 | forme nominative
            "norm_method": norm_method,   # 规范化方法 | méthode de normalisation
        },
        "el_results":  results,           # VIAF + Wikidata top-3 候选
    }
    try:
        with open(EL_SAVE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[WARN] Cannot save EL result: {e}")


def monitor_loop():
    # 主监控循环：每 2 秒轮询 INCEpTION，检测新的 auteur/ouvrage 标注
    # | Boucle principale : interroge INCEpTION toutes les 2s, détecte les nouveaux spans
    print(f"[Monitor] Started, polling every {POLL_INTERVAL}s")
    while True:
        try:
            spans, _ = fetch_xmi_spans()
            with lock:
                prev_ids  = state["last_span_ids"]
                curr_ids  = {s["id"] for s in spans}
                new_spans = [s for s in spans if s["id"] not in prev_ids]

            if new_spans:
                target   = new_spans[-1]
                raw_text = target["text"]
                label    = target["label"]
                ms_range = target["ms_range"]

                query_text, norm_method = normalize(raw_text, label)
                print(f"[Monitor] '{raw_text}' [{label}] -> '{query_text}'"
                      f" ({norm_method}) | ms={ms_range}")

                # Localiser la ligne via l'offset begin du span (plus fiable que text matching)
                span_begin = target.get("begin", 0)
                _, _full = fetch_xmi_spans()
                _raw_line = raw_text
                if _full:
                    offset = 0
                    for _ln in _full.split("\n"):
                        line_end = offset + len(_ln)
                        if offset <= span_begin <= line_end:
                            _raw_line = _ln.strip()
                            break
                        offset = line_end + 1  # +1 pour le \n
                # Extraire entry_id depuis la ligne complète (commence par un numéro)
                _eid_m = re.match(r'(\d+)', _raw_line)
                _eid = int(_eid_m.group(1)) if _eid_m else None

                with lock:
                    state["current_query"] = raw_text
                    state["normalized"]    = query_text if query_text != raw_text else None
                    state["norm_method"]   = norm_method
                    state["label"]         = label
                    state["ms_range"]      = ms_range
                    state["results"]       = []
                    state["status"]        = f"Searching: {query_text}..."
                    state["updated_at"]    = datetime.now().strftime("%H:%M:%S")

                results = []
                if label == "auteur":
                    v = query_viaf(query_text, ms_range)
                    w = query_wikidata(query_text, ms_range)
                    merged = v + w
                    merged.sort(key=lambda x: x["score"], reverse=True)
                    results = merged[:TOP_K]
                elif label == "ouvrage":
                    results = query_wikidata(query_text, ms_range)

                with lock:
                    state["results"]       = results
                    state["last_span_ids"] = curr_ids
                    state["status"]        = (
                        f"{len(results)} candidates for '{query_text}'"
                        if results else f"No results for '{query_text}'"
                    )
                    # Si nouvelle entrée → vider le cache avant d'accumuler
                    if state["entry_id"] != _eid:
                        state["entry_cache"] = {}
                        state["entry_id"]    = _eid
                        state["raw_line"]    = _raw_line
                    # Accumuler dans le cache de l'entrée courante
                    state["entry_cache"][raw_text] = {
                        "label":       label,
                        "normalized":  query_text if query_text != raw_text else raw_text,
                        "norm_method": norm_method,
                        "results":     results,
                    }
                print(f"[Monitor] {state['status']}")
            else:
                with lock:
                    state["last_span_ids"] = curr_ids

        except Exception as e:
            with lock:
                state["status"] = f"Error: {e}"
        time.sleep(POLL_INTERVAL)


app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PRIMA Monitor</title>
<style>
:root{--bg:#ffffff;--surf:#f5f5f0;--brd:#d0c8b8;--gold:#8a6500;--gdim:#b8920a;
  --txt:#1a1714;--dim:#6b6355;--grn:#2e7d4f;--org:#c05a00;--red:#a33000;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--txt);font-family:Georgia,serif;
  min-height:100vh;padding:2rem;}
h1{color:var(--gold);font-size:2rem;border-bottom:2px solid var(--brd);
  padding-bottom:.6rem;margin-bottom:.6rem;}
.sub{font-style:italic;color:var(--dim);font-size:1.1rem;margin-bottom:1.4rem;}
#status{font-family:monospace;font-size:1.1rem;color:#b8920a;font-weight:bold;
  margin-bottom:.6rem;min-height:1.6em;}
#query-box{margin-bottom:1rem;}
.qraw{font-size:1.3rem;color:var(--txt);font-style:italic;font-weight:bold;}
.qnorm{font-family:monospace;font-size:1.05rem;color:var(--gdim);margin-top:.3rem;}
.method{font-family:monospace;font-size:.9rem;color:var(--gdim);margin-top:.15rem;}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;}
@media(max-width:600px){.grid{grid-template-columns:1fr;}}
.src{font-family:monospace;font-size:1.1rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--txt);font-weight:bold;margin-bottom:.6rem;}
.card{background:var(--surf);border:1px solid var(--brd);border-radius:6px;
  padding:1rem 1.2rem;margin-bottom:.8rem;}
.cname{font-size:1.25rem;margin-bottom:.3rem;}
.rank{color:var(--gdim);font-size:.8rem;margin-right:.4rem;}
.dates{font-style:italic;color:var(--dim);font-size:1.05rem;margin-bottom:.4rem;}
.scores{display:flex;gap:1rem;font-family:monospace;font-size:.95rem;margin-bottom:.4rem;}
.sc span{display:block;color:var(--dim);font-size:.72rem;}
.uri a{font-family:monospace;font-size:.95rem;color:var(--gdim);
  text-decoration:none;word-break:break-all;}
.uri a:hover{color:var(--gold);}
.sources{font-family:monospace;font-size:.75rem;color:var(--dim);margin-top:.35rem;
  word-break:break-all;}
.viaf-xlink{font-family:monospace;font-size:.78rem;margin-top:.35rem;color:var(--dim);}
.viaf-xlink a{color:var(--gold);text-decoration:none;word-break:break-all;}
.viaf-xlink a:hover{color:var(--grn);}
.viaf-xlink.viaf-match{color:var(--grn);font-weight:bold;}
.viaf-xlink.viaf-match a{color:var(--grn);}
.viaf-none{color:var(--red) !important;}
.empty{color:var(--dim);font-style:italic;font-size:1.1rem;padding:.5rem 0;}
.hi{color:#4caf76;}.mi{color:#e07b3a;}.lo{color:#c94c4c;}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;
  background:var(--grn);margin-right:.4rem;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.25;}}
.ms-info{font-family:monospace;font-size:.9rem;color:var(--gdim);margin-bottom:1rem;}
</style>
</head>
<body>
<h1>PRIMA Monitor</h1>
<p class="sub"><span class="dot"></span>Real-time EL · VIAF + Wikidata · Top-3</p>
<div id="status">Initializing...</div>
<div id="entry-info" style="font-family:monospace;font-size:.8rem;color:var(--gold);margin-bottom:.4rem;min-height:1.2em;"></div>
<div id="query-box"></div>
<div id="ms-info" class="ms-info"></div>
<div style="margin-bottom:1.2rem;display:flex;gap:.8rem;align-items:center;">
  <button onclick="saveResult()" id="btn-save"
    style="background:var(--grn);color:#fff;border:none;border-radius:4px;
           padding:.4rem 1.1rem;font-family:monospace;font-size:.8rem;cursor:pointer;font-weight:bold;">
    Sauvegarder
  </button>
  <span id="save-status" style="font-family:monospace;font-size:.75rem;color:var(--gdim);"></span>
</div>
<div id="entry-cache" style="margin-bottom:1rem;"></div>
<div class="grid">
  <div><div class="src">VIAF</div><div id="viaf"></div></div>
  <div><div class="src">Wikidata</div><div id="wd"></div></div>
</div>
<script>
function sc(v){return v>=0.7?'hi':v>=0.4?'mi':'lo';}
function cards(data,id){
  const el=document.getElementById(id);
  if(!data||!data.length){el.innerHTML='<div class="empty">no results</div>';return;}
  el.innerHTML=data.map((c,i)=>{
    const d=(c.birth||c.death)?`${c.birth||'?'}-${c.death||'?'}`:'dates unknown';
    // Sources block (VIAF only)
    let sourcesHtml='';
    if(c.source==='viaf'&&c.sources&&c.sources.length){
      sourcesHtml=`<div class="sources">sources: ${c.sources.join(' · ')}</div>`;
    }
    // VIAF cross-link block (Wikidata only, P214) — cross-match avec candidats VIAF
    let viafLinkHtml='';
    if(c.source==='wikidata'){
      if(c.viaf_ids && c.viaf_ids.length > 0){
        const viafUris = (window._allCandidates||[]).filter(x=>x.source==='viaf').map(x=>x.uri);
        viafLinkHtml = c.viaf_ids.map(vid => {
          const uri = `https://viaf.org/viaf/${vid}`;
          const matchIdx = viafUris.indexOf(uri);
          if(matchIdx >= 0){
            return `<div class="viaf-xlink viaf-match">✓ VIAF cluster = candidat VIAF #${matchIdx+1} : <a href="${uri}" target="_blank">${uri}</a></div>`;
          } else {
            return `<div class="viaf-xlink">· P214 : <a href="${uri}" target="_blank">${uri}</a></div>`;
          }
        }).join('');
      } else {
        viafLinkHtml=`<div class="viaf-xlink viaf-none">✗ pas de lien VIAF (P214 absent)</div>`;
      }
    }
    return `<div class="card">
      <div class="cname"><span class="rank">#${i+1}</span>${c.label}</div>
      <div class="dates">${d}</div>
      <div class="scores">
        <div class="sc ${sc(c.str_sim)}">${c.str_sim.toFixed(2)}<span>str</span></div>
        <div class="sc ${sc(c.time_score)}">${c.time_score.toFixed(2)}<span>tps</span></div>
        <div class="sc ${sc(c.score)}"><b>${c.score.toFixed(2)}</b><span>score</span></div>
      </div>
      <div class="uri"><a href="${c.uri}" target="_blank">${c.uri}</a></div>
      ${sourcesHtml}${viafLinkHtml}
    </div>`;
  }).join('');
}
async function poll(){
  try{
    const d=await(await fetch('/api/state')).json();
    document.getElementById('status').textContent=d.status||'';
    // Afficher le numéro d'entrée et la ligne brute
    const ei=document.getElementById('entry-info');
    ei.style.fontWeight='bold'; ei.textContent=d.entry_id?`Entrée #${d.entry_id}  —  ${d.raw_line||''}`:'';
    // Afficher la requête courante
    const qb=document.getElementById('query-box');
    if(d.current_query){
      let html=`<div class="qraw">"${d.current_query}"</div>`;
      if(d.normalized&&d.normalized!==d.current_query)
        html+=`<div class="qnorm">nominatif: ${d.normalized}</div>`
             +`<div class="method">method: ${d.norm_method||''}</div>`;
      qb.innerHTML=html;
    } else qb.innerHTML='';
    const ms=document.getElementById('ms-info');
    ms.textContent=d.ms_range&&d.ms_range[0]
      ?`ms. century: ${d.ms_range[0]}-${d.ms_range[1]}`:'';
    // Résultats de la requête courante
    window._allCandidates = d.results || [];
    const viaf=(d.results||[]).filter(x=>x.source==='viaf');
    const wd=(d.results||[]).filter(x=>x.source==='wikidata');
    cards(viaf,'viaf'); cards(wd,'wd');
    // Afficher le cache de l'entrée courante (toutes les annotations déjà interrogées)
    const cache=d.entry_cache||{};
    const cacheDiv=document.getElementById('entry-cache');
    const entries=Object.entries(cache);
    if(entries.length>0){
      let html='';
      for(const[span,v] of entries){
        const best=v.results&&v.results.length?v.results[0]:null;
        html+=`<div style="margin-bottom:.5rem;padding:.5rem;background:var(--surf);border:1px solid var(--brd);border-radius:4px;">`;
        html+=`<span style="color:var(--gold);font-family:monospace;font-size:.75rem;">[${v.label}]</span> `;
        html+=`<span style="font-style:italic;">"${span}"</span>`;
        if(v.normalized&&v.normalized!==span)
          html+=` <span style="color:var(--gdim);font-size:.75rem;">→ ${v.normalized}</span>`;
        if(best)
          html+=`<div style="font-family:monospace;font-size:.7rem;color:var(--dim);margin-top:.2rem;">`;
          html+=`#1 ${best.label} | <a href="${best.uri}" target="_blank" style="color:var(--gdim);">${best.uri}</a></div>`;
        html+=`</div>`;
      }
      cacheDiv.innerHTML=html;
    } else {
      cacheDiv.innerHTML='';
    }
  }catch(e){}
}
poll();setInterval(poll,1500);

async function saveResult(){
  const btn=document.getElementById('btn-save');
  const st=document.getElementById('save-status');
  btn.disabled=true;
  try{
    const r=await fetch('/api/save',{method:'POST'});
    const d=await r.json();
    st.textContent=d.success?'✓ Sauvegardé':'✗ Erreur';
    st.style.color=d.success?'#2e7d4f':'#a33000';
    st.style.fontWeight='bold';
    st.style.fontSize='1rem';
    setTimeout(()=>{st.textContent='';},4000);
  }catch(e){st.textContent='Erreur';}
  btn.disabled=false;
}

</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)



@app.route("/api/state")
def api_state():
    with lock:
        return jsonify({
            "status":        state["status"],
            "current_query": state["current_query"],
            "normalized":    state["normalized"],
            "norm_method":   state["norm_method"],
            "label":         state["label"],
            "entry_id":      state["entry_id"],
            "raw_line":      state["raw_line"],
            "results":       state["results"],
            "entry_cache":   state["entry_cache"],
            "ms_range":      list(state["ms_range"]),
            "updated_at":    state["updated_at"],
        })


@app.route("/api/save", methods=["POST"])
def api_save():
    """Sauvegarde tous les résultats EL de l'entrée courante dans el_auteur_ouvrage.jsonl"""
    with lock:
        entry_id    = state.get("entry_id")
        raw_line    = state.get("raw_line")
        ms          = state.get("ms_range", (0, 0))
        entry_cache = dict(state.get("entry_cache", {}))
    if not entry_id:
        return jsonify({"success": False})
    record = {
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "entry_id":   entry_id,
        "raw_line":   raw_line,
        "ms_range":   list(ms),
        "annotations": [
            {
                "span_text":   span_text,
                "label":       v["label"],
                "normalized":  v["normalized"],
                "norm_method": v["norm_method"],
                "el_results":  v["results"],
            }
            for span_text, v in entry_cache.items()
        ],
    }
    try:
        os.makedirs(os.path.dirname(EL_SAVE_PATH), exist_ok=True)
        with open(EL_SAVE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        n = len(record["annotations"])
        print(f"[Save] Entrée #{entry_id} → {n} annotation(s) sauvegardées")
        return jsonify({"success": True})
    except Exception as e:
        print(f"[WARN] Save failed: {e}")
        return jsonify({"success": False})

if __name__ == "__main__":
    # 启动时自动创建输出目录 | Création automatique du dossier de sortie au démarrage
    import os as _os
    _os.makedirs(_os.path.dirname(EL_SAVE_PATH), exist_ok=True)
    print("=" * 55)
    print("  PRIMA Monitor")
    print(f"  Interface: http://localhost:{PORT}")
    print(f"  Polling  : every {POLL_INTERVAL}s")
    print(f"  Saving EL: {EL_SAVE_PATH}")
    print("=" * 55)
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=PORT, debug=False)
