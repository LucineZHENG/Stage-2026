#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prima_pipeline.py  –  Pipeline complet PRIMA
=============================================
1. Lit les 4 fichiers JSON Riccardiana
2. Tire aléatoirement 25 entrées PAR fichier (= 100 au total)
   → uniquement les entrées présentes dans catalogue.txt
3. Pour chaque entrée :
   - Extrait auteur / ouvrage / material / date / état depuis le texte brut
   - Interroge VIAF + Wikidata pour Entity Linking
   - Calcule un score de vraisemblance auteur ↔ date du ms.
4. Exporte :
   - webanno_preannotation.tsv  → à importer dans INCEpTION (Format : WebAnno TSV 3)
   - annotation_guide.tsv       → aide à la lecture (FR + ZH + champs JSON)
   - el_report.json             → résultats Entity Linking complets
   - webanno_preannotation.tsv  → pré-annotation WebAnno TSV 3.3 (import INCEpTION)

Usage :
  python prima_pipeline.py \
    --json_dir  /chemin/vers/jsons \
    --catalogue catalogue.txt \
    --cat_dict  catalogue_dict.json \
    --sample    25 \
    --seed      42 \
    --out_dir   ./output_inception \
    [--no_api]
"""

import argparse
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[WARN] 'requests' non installé → mode --no_api forcé.", file=sys.stderr)



# ═══════════════════════════════════════════════════════════════════════════════
# 1b.  MAPPING DATE  (depuis MAPPING.py)
# ═══════════════════════════════════════════════════════════════════════════════

# Siècles romains (minuscules) → (année_début_siècle, année_fin_siècle)
CENTURIES_MAP = {
    'i':      (1,    99),
    'ii':     (100,  199),
    'iii':    (200,  299),
    'iv':     (300,  399),
    'v':      (400,  499),
    'vi':     (500,  599),
    'vii':    (600,  699),
    'viii':   (700,  799),
    'ix':     (800,  899),
    'x':      (900,  999),
    'xi':     (1000, 1099),
    'xii':    (1100, 1199),
    'xiii':   (1200, 1299),
    'xiv':    (1300, 1399),
    'xv':     (1400, 1499),
    'xvi':    (1500, 1599),
    'xvii':   (1600, 1699),
    'xviii':  (1700, 1799),
    'xix':    (1800, 1899),
    'xx':     (1900, 1999),
}

# Périodes descriptives → (offset_début, offset_fin) dans le siècle
# Ordre : du plus spécifique au plus général
PERIODS_MAP = [
    # Quarts — du plus spécifique
    (['primo quarto',  'primi 25 anni'],              ( 0,  24)),
    (['secondo quarto'],                               (25,  49)),
    (['terzo quarto'],                                 (50,  74)),
    (['ultimo quarto', 'ultimi 25 anni'],              (75,  99)),
    # Décennies
    (['primo decennio', 'primi anni', 'initiis',
      'inizio', 'principio', 'in.', 'inc.', 'ineun.', 'ineunte'], (0, 9)),
    (['secondo decennio'],                             (10,  19)),
    (['ultimi venti anni', "ultimi vent'anni"],       (80,  99)),
    (['ultimo trentennio'],                            (70,  99)),
    (['ultimi anni', 'fine', 'tardo', 'ex.'],         (90,  99)),
    (['primi decenni'],                                ( 0,  29)),
    # Moitiés — IMPORTANT : les formes longues avant 'metà' seul
    (['seconda metà', 'ii metà'],                     (50,  99)),
    (['prima metà',   'i metà'],                      ( 0,  49)),
    (['metà', 'med.'],                                 (40,  59)),
]

MONTHS_MAP = {
    'gennaio': '01', 'ianuario': '01',
    'febbraio': '02',
    'marzo': '03',
    'aprile': '04', 'apr.': '04',
    'maggio': '05',
    'giugno': '06',
    'luglio': '07',
    'agosto': '08',
    'settembre': '09',
    'ottobre': '10', 'ott.': '10',
    'novembre': '11', 'nov.': '11',
    'dicembre': '12', 'decembre': '12', 'dic.': '12',
}


def parse_date_range(date_str: str) -> tuple:
    """
    Convertit une chaîne de date JSON italienne en (year_start, year_end).

    Exemples :
      'Sec. XII seconda metà (1151-1200)'  → (1150, 1199)
      'Sec. XV primo quarto (1401-1425)'   → (1400, 1424)
      'Sec. XIV (1300-1399)'               → (1300, 1399)
      '1265-1268 circa'                    → (1265, 1268)
      'Saec. XIII'                         → (1200, 1299)   ← texte brut catalogue
      'XVe s. (début)'                     → (1400, 1409)   ← déjà normalisé

    Retourne (0, 0) si non reconnu.
    """
    if not date_str:
        return (0, 0)

    s = date_str.strip().lower()

    # ── 1. Plage explicite entre parenthèses, ex. (1151-1200) ──────────────
    m_explicit = re.search(r'(\d{3,4})\s*[-–]\s*(\d{3,4})', s)
    if m_explicit:
        return (int(m_explicit.group(1)), int(m_explicit.group(2)))

    # ── 2. Année unique, ex. '1265 circa' ───────────────────────────────────
    m_single = re.match(r'(\d{3,4})\s*(?:circa|ca\.?)?', s)
    if m_single and not re.search(r'[ivxlcdm]', s):
        y = int(m_single.group(1))
        return (y, y)

    # ── 3. Siècle romain + période descriptive ──────────────────────────────
    # Cherche le siècle : Sec. XII / Saec. XV / XIVe s. / XIV
    roman_pat = re.search(
        r'(?:(?:sec(?:ulo)?|saec(?:ulo)?)\.\s*([ivxlcdm]+)|(?<![a-z])([ivxlcdm]+)(?:e\s+s\.?)?)(?![a-z])', s)
    if not roman_pat:
        return (0, 0)

    century_key = (roman_pat.group(1) or roman_pat.group(2) or '').lower()
    if century_key not in CENTURIES_MAP:
        return (0, 0)

    c_start, c_end = CENTURIES_MAP[century_key]
    century_len = c_end - c_start + 1   # toujours 100

    # Cherche une période dans le reste de la chaîne
    for keywords, (off_start, off_end) in PERIODS_MAP:
        for kw in keywords:
            if kw in s:
                return (c_start + off_start, c_start + off_end)

    # Aucune période → siècle entier
    return (c_start, c_end)


def normalize_date_label(date_str: str) -> str:
    """
    Produit un label lisible + la plage d'années calculée.

    Exemples :
      'Saec. XV'                 → 'XVe s.  [1400–1499]'
      'Sec. XII seconda metà'    → 'XIIe s. (seconde moitié)  [1150–1199]'
      'Saec. XIII in.'           → 'XIIIe s. (début)  [1200–1209]'
    """
    if not date_str:
        return ""

    s = date_str.strip().lower()

    # Siècle romain
    roman_pat = re.search(
        r'(?:(?:sec(?:ulo)?|saec(?:ulo)?)\.\s*([ivxlcdm]+)|(?<![a-z])([ivxlcdm]+)(?:e\s+s\.?)?)(?![a-z])', s)
    roman_upper = (roman_pat.group(1) or roman_pat.group(2) or '').upper() if roman_pat else ""

    # Période en français
    period_fr = ""
    for keywords, (off_start, off_end) in PERIODS_MAP:
        for kw in keywords:
            if kw in s:
                if off_start == 0  and off_end == 9:   period_fr = "(début)"
                elif off_start == 90 and off_end == 99: period_fr = "(fin)"
                elif off_start == 0  and off_end == 49: period_fr = "(1re moitié)"
                elif off_start == 50 and off_end == 99: period_fr = "(2e moitié)"
                elif off_start == 40 and off_end == 59: period_fr = "(milieu)"
                elif off_start == 0  and off_end == 24: period_fr = "(1er quart)"
                elif off_start == 25 and off_end == 49: period_fr = "(2e quart)"
                elif off_start == 50 and off_end == 74: period_fr = "(3e quart)"
                elif off_start == 75 and off_end == 99: period_fr = "(dernier quart)"
                else: period_fr = f"(+{off_start}–+{off_end})"
                break
        if period_fr:
            break

    # Plage d'années
    y_start, y_end = parse_date_range(date_str)
    years_str = f"[{y_start}–{y_end}]" if y_start else ""

    parts = [p for p in [f"{roman_upper}e s." if roman_upper else "",
                          period_fr, years_str] if p]
    return "  ".join(parts) if parts else date_str


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  PATTERNS REGEX  (NER rule-based)
# ═══════════════════════════════════════════════════════════════════════════════

_SUPPORT_RE = re.compile(
    r'\bCod(?:ex|ices)?[.,]?\s*'          # Cod. / Cod, / Codex  (virgule possible)
    r'(?:partim\s+)?'                      # "Cod partim membr."
    r'(?P<support>'
    r'membran(?:ac(?:eus|ea)?)?\.?'        # membranaceus / membranac. / membran.
    r'|membr\.?|memb\.?|mem\.?'            # membr. / memb. / mem.
    r'|chart(?:ac(?:eus|ea)?)?\.?'         # chartaceus / chartac. / chart.
    r'|chartc\.?'                          # chartc. (coquille)
    r'|cartac?\.?'                         # cartac. / cart.
    r'|char\.?|car\.?'                     # char. / car.
    r'|Membran\.?'                         # Membran. (majuscule)
    r')',
    re.IGNORECASE,
)
_FORMAT_RE = re.compile(
    r'(?:\bin\s*\.?\s*|\.\s+)'            # "in " / "in. " / ". " (forme italienne sans "in")
    r'(?P<format>'
    r'fol(?:io)?\.?\s*(?:atlantico\.?|max(?:imo)?\.?|min(?:imo)?\.?)?'  # fol. / folio / fol. max / fol. atlantico
    r'|quarto|4[°.]?'                      # quarto / 4 / 4.
    r'|octavo|8[°.]?'                      # octavo / 8. / 8°
    r'|16[°.,]?'                           # in 16 / in 16. / in 16,
    r'|12[°.]?'                            # in 12
    r')(?!\w)',                            # pas suivi d'une lettre (évite "fine", "fide"...)
    re.IGNORECASE,
)
_DATE_RE = re.compile(
    r'(?:S[ae]{1,2}c(?:ulo)?|Sec(?:olo)?)\.?\s+'  # Saec. / Sec. / Seac. (coquille)
    r'(?P<century>[IVXLCDM]+\.?)'
    r'(?:\s*(?P<period>in\.|ex\.|med\.)(?!\s*fol))?',  # period seulement si pas suivi de "fol"
    re.IGNORECASE,
)
_ETAT_RE = re.compile(
    r'(?P<etat>'
    # ── Latin ──────────────────────────────────────────────────────────
    r'optime\s+servatus'
    r'|bene\s+servatus'
    r'|(?:initio|in\s+fine)\s+mutilus'
    r'|mutilus(?:\s+in\s+(?:principio|fine))?'
    r'|initio\s+et\s+(?:medio\s+)?mutilus'       # initio et medio mutilus
    r'|initio\s+et\s+fine\s+mutilus'
    r'|mancus\s+et\s+imperfectus'
    r'|valde\s+mutilus'
    r'|nitidissime\s+(?:exaratus|scriptus)'
    r'|elegantissime\s+exaratus'
    r'|quantivis\s+pretii'
    r'|(?:MS\.?\s*)?Archetypus'
    # ── Italien ────────────────────────────────────────────────────────
    r'|mancante\s+in\s+(?:principio|fine)'        # mancante in principio/fine
    r'|manc(?:ante)?\.\s+in\s+(?:principio|fine)' # manc. in fine
    r'|mancante\s+di\s+\S+'                       # mancante di una pagina
    r'|non\s+(?:terminato|finito)\s+di\s+scrivere'# non finito di scrivere
    r'|lacero\s+nella\s+\S+\s+carta'              # lacero nella prima carta
    r'|lacero'
    r'|assai\s+guasto'
    r'|guasto'
    r')',
    re.IGNORECASE,
)

CENTURY_MAP = {
    "I": (1,100), "II": (101,200), "III": (201,300), "IV": (301,400),
    "V": (401,500), "VI": (501,600), "VII": (601,700), "VIII": (701,800),
    "IX": (801,900), "X": (901,1000), "XI": (1001,1100), "XII": (1101,1200),
    "XIII": (1201,1300), "XIV": (1301,1400), "XV": (1401,1500),
    "XVI": (1501,1600), "XVII": (1601,1700), "XVIII": (1701,1800),
}

# Normalisation material et etat — importée depuis MAPPING_mfe.py
try:
    from MAPPING_mfe import (SUPPORT_NORM as MATERIAL_NORM_FULL,
                              FORMAT_NORM  as FORMAT_NORM_FULL,
                              ETAT_NORM    as ETAT_NORM_FULL,
                              MATERIAL_COMBINATIONS)
    _HAS_MAPPING_MFE = True
except ImportError:
    _HAS_MAPPING_MFE = False
    MATERIAL_NORM_FULL = {}
    FORMAT_NORM_FULL   = {}
    ETAT_NORM_FULL     = {}
    MATERIAL_COMBINATIONS = {}

# Fallback (clés courtes) si MAPPING_mfe non disponible
MATERIAL_NORM = {
    "membr": "Cod. membr.", "membran": "Cod. membr.",
    "membranac": "Cod. membranac.", "membranaceus": "Cod. membranaceus",
    "chart": "Cod. chart.", "chartac": "Cod. chart.",
}
FORMAT_NORM = {
    "fol": "in fol.", "folio": "in folio", "quarto": "in quarto",
    "8°": "in 8°", "octavo": "in octavo",
    "fol. atlantico": "in fol. atlantico", "fol. max": "in fol. max.",
}

# Correspondance date JSON (italien) → label normalisé  [utilise MAPPING]
def normalize_json_date(date_str: str) -> str:
    """Délègue à normalize_date_label() qui utilise PERIODS_MAP / CENTURIES_MAP."""
    return normalize_date_label(date_str)


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  STRUCTURES DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Span:
    start: int
    end: int
    text: str
    label: str       # auteur | ouvrage | material | date | etat
    normalized: str = ""


@dataclass
class ELCandidate:
    source: str          # "viaf" | "wikidata"
    identifier: str
    label: str
    birth: Optional[int] = None
    death: Optional[int] = None
    score: float = 0.0       # vraisemblance temporelle
    note: str = ""
    str_sim: float = 0.0     # similarité de chaîne (nom requête ↔ label)
    combined: float = 0.0    # score combiné final (classement top-k)


@dataclass
class Entry:
    entry_id: int
    source_file: str           # nom du fichier JSON d'origine
    raw_text: str              # texte brut du catalogue (1 ligne)
    traduction_fr: str = ""
    traduction_zh: str = ""
    # Depuis le JSON Riccardiana
    json_material: str = ""
    json_date: str = ""
    json_date_norm: str = ""
    json_authors: list = field(default_factory=list)   # list[str]
    json_titles: list = field(default_factory=list)    # list[str]
    # NER sur le texte brut
    spans: list = field(default_factory=list)          # list[Span]
    ms_century_range: tuple = field(default_factory=tuple)
    # Entity Linking
    el_results: list = field(default_factory=list)     # list[ELCandidate]


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  CHARGEMENT DES DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

JSON_FILES = [
    "Catalogo_I_Riccardiana_221-320.json",
    "Catalogo_II_Riccardiana_321-420.json",
    "Catalogo_III_Riccardiana_421-520.json",
    "Catalogo_IV_Riccardiana_1002-1700.json",
]


def load_catalogue(path: str) -> dict[int, str]:
    cat = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            m = re.match(r'^(\d+)\s+', line)
            if m:
                cat[int(m.group(1))] = line
    return cat


def load_cat_dict(path: str) -> dict[int, dict]:
    """catalogue_dict.json → {entry_id: {traduction_fr, traduction_zh, ...}}"""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    result = {}
    for key, val in raw.items():
        m = re.match(r'^(\d+)\s+', key)
        if m:
            result[int(m.group(1))] = val
    return result


def load_json_file(path: str) -> list[dict]:
    """Retourne la liste des manuscripts depuis un fichier JSON Riccardiana."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("manuscripts", [])


def ms_entry_id(manuscript: dict) -> Optional[int]:
    """Extrait le numéro entier depuis shelf_mark.signature ('Ricc. 247' → 247)."""
    sig = manuscript.get("shelf_mark", {}).get("signature", "")
    m = re.search(r'(\d+)', sig)
    return int(m.group(1)) if m else None


def extract_json_fields(manuscript: dict) -> dict:
    """Extrait material, date, authors, titles depuis un manuscrit JSON."""
    phys = manuscript.get("physical_description", {})
    material = phys.get("material", "")
    date_raw = phys.get("date", "")

    authors, titles = [], []
    for content_item in manuscript.get("content", []):
        a = content_item.get("author", "").strip()
        t = (content_item.get("attributed_title", "") or
             content_item.get("title", "")).strip()
        if a:
            authors.append(a)
        if t:
            titles.append(t)

    return {
        "material": material,
        "date_raw": date_raw,
        "date_norm": normalize_json_date(date_raw),
        "authors": list(dict.fromkeys(authors)),   # dédoublonnage ordre conservé
        "titles": list(dict.fromkeys(titles)),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  ÉCHANTILLONNAGE
# ═══════════════════════════════════════════════════════════════════════════════

def sample_from_files(json_dir: str, catalogue: dict[int, str],
                      n: int, seed: int) -> list[tuple[str, dict]]:
    """
    Pour chaque fichier JSON, tire exactement n entrées uniques.

    Structure réelle des JSON Riccardiana :
    - Pas de doublon entre fichiers (plages d'IDs disjointes)
    - Un même entry_id peut apparaître plusieurs fois DANS le même fichier
      (fascicules / textes différents du même manuscrit) → on fusionne en 1 entrée
    - On filtre : entry_id doit exister dans catalogue.txt, et le texte
      ne doit pas être uniquement "Idem" / "Eiusdem"

    Si un fichier a moins de n entrées valides uniques, on complète
    depuis le fichier IV (qui a ~648 entrées) pour atteindre exactement 4×n.
    """
    random.seed(seed)

    def _is_useful(eid, catalogue):
        if eid not in catalogue:
            return False
        raw = catalogue.get(eid, "")
        body = re.sub(r'^\d+\s+', '', raw).strip()
        if re.match(r'(?:Idem|Eiusdem)[.\s]*$', body, re.IGNORECASE):
            return False
        return True

    # ── Étape 1 : par fichier, dédoublonner par entry_id (intra-fichier) ─
    # Même entry_id = même manuscrit avec plusieurs textes → on garde
    # la première occurrence (les autres sont des sous-entrées de contenu)
    pools = {}   # fname → list[ms] (un ms par entry_id unique)
    for fname in JSON_FILES:
        fpath = os.path.join(json_dir, fname)
        if not os.path.exists(fpath):
            print(f"[WARN] Fichier introuvable : {fpath}", file=sys.stderr)
            pools[fname] = []
            continue
        mss = load_json_file(fpath)
        seen_intra = set()
        unique_valid = []
        for ms in mss:
            eid = ms_entry_id(ms)
            if eid is None or eid in seen_intra:
                continue
            if not _is_useful(eid, catalogue):
                continue
            seen_intra.add(eid)
            unique_valid.append(ms)
        pools[fname] = unique_valid
        print(f"  {fname}: {len(unique_valid)} entrées valides uniques")

    # ── Étape 2 : tirer exactement n par fichier ──────────────────────────
    target = len(JSON_FILES) * n
    result  = []
    used_ids = set()
    shortfall = 0

    for fname in JSON_FILES:
        pool = pools.get(fname, [])
        if len(pool) >= n:
            chosen = random.sample(pool, n)
        else:
            chosen = pool[:]
            shortfall += n - len(pool)
            print(f"  [WARN] {fname} : seulement {len(pool)} entrées valides (< {n})")
        for ms in chosen:
            used_ids.add(ms_entry_id(ms))
        result.extend((fname, ms) for ms in chosen)

    # ── Étape 3 : combler le déficit depuis les entrées non tirées ────────
    # (priorité au fichier IV qui est le plus grand)
    if shortfall > 0:
        reserve = []
        for fname in JSON_FILES:
            for ms in pools.get(fname, []):
                if ms_entry_id(ms) not in used_ids:
                    reserve.append((fname, ms))
        random.shuffle(reserve)
        added = 0
        for fname, ms in reserve:
            if added >= shortfall:
                break
            result.append((fname, ms))
            used_ids.add(ms_entry_id(ms))
            added += 1
        if added < shortfall:
            print(f"  [WARN] Pool total insuffisant : {len(result)} entrées seulement "
                  f"(objectif {target}).")
        else:
            print(f"  Déficit comblé : +{added} entrées depuis la réserve.")

    print(f"  → Total : {len(result)} entrées (objectif {target})")
    assert len(result) == target or len(result) < target,         f"BUG : {len(result)} entrées générées (objectif {target})"
    result.sort(key=lambda x: ms_entry_id(x[1]) or 0)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  NER (rule-based, spans dans le texte brut)
# ═══════════════════════════════════════════════════════════════════════════════

def find_span(text: str, substring: str, label: str,
              normalized: str = "") -> Optional[Span]:
    if not substring:
        return None
    idx = text.find(substring)
    if idx == -1:
        return None
    return Span(idx, idx + len(substring), substring, label, normalized)


def extract_spans(raw: str, cat_val: dict) -> list[Span]:
    spans = []

    # Auteur
    # Priorité 1 : génitif latin (forme exacte dans le texte)
    # Fallback   : nominatif (italien / grec, pas de déclinaison)
    genitif   = cat_val.get("auteur_genitif", "").strip()
    nominatif = cat_val.get("auteur_nominatif", "").strip()
    if genitif:
        sp = find_span(raw, genitif, "auteur", normalized=nominatif)
        if sp:
            spans.append(sp)
    elif nominatif:
        # Langue sans déclinaison : le nominatif apparaît tel quel dans le texte
        sp = find_span(raw, nominatif, "auteur", normalized=nominatif)
        if sp:
            spans.append(sp)

    # Ouvrage
    # Priorité 1 : génitif (latin)
    # Fallback   : nominatif (italien / grec)
    ouv_gen = cat_val.get("ouvrage_genitif", "").strip()
    ouv_nom = cat_val.get("ouvrage_nominatif", "").strip()
    if ouv_gen:
        sp = find_span(raw, ouv_gen, "ouvrage", normalized=ouv_nom)
        if sp:
            spans.append(sp)
    elif ouv_nom:
        sp = find_span(raw, ouv_nom, "ouvrage", normalized=ouv_nom)
        if sp:
            spans.append(sp)

    # Material
    sup_m = _SUPPORT_RE.search(raw)
    fmt_m = _FORMAT_RE.search(raw)
    if sup_m and fmt_m:
        mat_start = sup_m.start()
        mat_end   = max(sup_m.end(), fmt_m.end())
        mat_text  = raw[mat_start:mat_end].strip()
        # Priorité 1 : correspondance exacte via MAPPING_mfe
        norm_material = MATERIAL_COMBINATIONS.get(mat_text.strip())
        if not norm_material:
            # Priorité 2 : lookup support + format séparément
            sup_raw = sup_m.group(0).strip()
            fmt_raw = fmt_m.group(0).strip()
            norm_sup = MATERIAL_NORM_FULL.get(sup_raw) or                        MATERIAL_NORM.get(
                           sup_m.group("support").rstrip(".").lower().replace(".",""),
                           sup_raw)
            norm_fmt = FORMAT_NORM_FULL.get(fmt_raw) or                        FORMAT_NORM.get(
                           fmt_m.group("format").strip().rstrip(".").lower(),
                           fmt_raw)
            norm_material = f"{norm_sup} {norm_fmt}"
        spans.append(Span(mat_start, mat_end, mat_text,
                          "material", norm_material))

    # Date  →  normalisation via MAPPING (CENTURIES_MAP + PERIODS_MAP)
    dat_m = _DATE_RE.search(raw)
    if dat_m:
        date_text = dat_m.group(0).strip()
        norm = normalize_date_label(date_text)
        spans.append(Span(dat_m.start(), dat_m.end(), date_text, "date", norm))

    # État de conservation
    for eta_m in _ETAT_RE.finditer(raw):
        etat_raw = eta_m.group("etat").strip()
        # Priorité 1 : MAPPING_mfe (exhaustif)
        norm_e = ETAT_NORM_FULL.get(etat_raw)
        if not norm_e:
            # Priorité 2 : fallback dict interne
            _fallback = {
                "optime servatus":      "très bien conservé",
                "bene servatus":        "bien conservé",
                "mutilus":              "mutilé",
                "initio mutilus":       "mutilé au début",
                "in fine mutilus":      "mutilé à la fin",
                "mutilus in principio": "mutilé au début",
                "mutilus in fine":      "mutilé à la fin",
                "mancus et imperfectus":"mutilé et incomplet",
                "nitidissime exaratus": "très soigneusement écrit",
                "nitidissime scriptus": "très soigneusement écrit",
                "elegantissime exaratus":"élégamment écrit",
                "quantivis pretii":     "d'une valeur inestimable",
                "archetypus":           "archétype",
                "ms. archetypus":       "manuscrit archétype",
            }
            norm_e = _fallback.get(etat_raw.lower(), etat_raw)
        spans.append(Span(eta_m.start(), eta_m.end(),
                          etat_raw, "etat", norm_e))

    spans.sort(key=lambda s: s.start)
    return spans


def century_to_range(century_str: str) -> tuple:
    """Délègue à parse_date_range() via CENTURIES_MAP."""
    key = century_str.rstrip(".").lower()
    return CENTURIES_MAP.get(key, (0, 0))


# ═══════════════════════════════════════════════════════════════════════════════
# 6.  ENTITY LINKING – VIAF
# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════
# 7.  ENTITY LINKING – WIKIDATA
# ═══════════════════════════════════════════════════════════════════════════════

WD_SEARCH = "https://www.wikidata.org/w/api.php"
WD_SPARQL  = "https://query.wikidata.org/sparql"


def query_wikidata(author_name: str, ms_range: tuple) -> list[ELCandidate]:
    if not author_name or not HAS_REQUESTS:
        return []
    # Étape 1 : recherche label
    params = {
        "action": "wbsearchentities",
        "search": author_name,
        "language": "la",
        "fallbacklanguage": "fr",
        "type": "item",
        "limit": 5,
        "format": "json",
    }
    try:
        r = requests.get(WD_SEARCH, params=params, timeout=12)
        r.raise_for_status()
        results = r.json().get("search", [])
    except Exception as e:
        return [ELCandidate("wikidata", "", author_name, note=f"Erreur: {e}")]

    qids = [res["id"] for res in results[:5]]
    if not qids:
        return []

    # Étape 2 : dates SPARQL
    qids_str = " ".join(f"wd:{q}" for q in qids)
    sparql = f"""
SELECT ?item ?itemLabel ?birth ?death WHERE {{
  VALUES ?item {{ {qids_str} }}
  OPTIONAL {{ ?item wdt:P569 ?birth. }}
  OPTIONAL {{ ?item wdt:P570 ?death. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "la,fr,en". }}
}}"""
    rows = []
    try:
        r2 = requests.get(WD_SPARQL,
                          params={"query": sparql, "format": "json"},
                          headers={"Accept": "application/sparql-results+json"},
                          timeout=15)
        r2.raise_for_status()
        rows = r2.json().get("results", {}).get("bindings", [])
    except Exception:
        pass

    dates_map, label_map = {}, {}
    for row in rows:
        qid = row["item"]["value"].split("/")[-1]
        label_map[qid] = row.get("itemLabel", {}).get("value", qid)
        birth = _year_iso(row.get("birth", {}).get("value", ""))
        death = _year_iso(row.get("death", {}).get("value", ""))
        dates_map[qid] = (birth, death)

    candidates = []
    for qid in qids:
        birth, death = dates_map.get(qid, (None, None))
        label = label_map.get(qid, qid)
        score = _score(birth, death, ms_range)
        candidates.append(ELCandidate(
            "wikidata",
            f"https://www.wikidata.org/wiki/{qid}",
            label, birth, death, score, qid))

    # Calcul du score combiné (str_sim + time) et tri top-k
    for c in candidates:
        c.str_sim  = _str_sim(author_name, c.label)
        c.combined = _combined_score(c.str_sim, c.score)

    candidates.sort(key=lambda c: c.combined, reverse=True)
    return candidates[:TOP_K]


def _year_iso(s: str) -> Optional[int]:
    m = re.search(r'[+-]?(\d{3,4})-', s)
    return int(m.group(1)) if m else None


TOP_K = 3   # nombre de candidats à conserver par source

def _score(birth, death, ms_range) -> float:
    """Vraisemblance temporelle : auteur ↔ date du manuscrit."""
    if not ms_range or ms_range == (0, 0):
        return 0.0
    ms_start, ms_end = ms_range
    if birth is None and death is None:
        return 0.0
    if death is not None:
        if death <= ms_end:      return 1.0
        if death <= ms_end + 50: return 0.7
        return 0.1
    if birth is not None:
        if birth > ms_end:    return 0.0
        if birth >= ms_start: return 0.8
        return 0.6
    return 0.0


def _str_sim(query: str, candidate: str) -> float:
    """
    Similarité de chaîne entre le nom recherché et le label retourné.
    Utilise difflib.SequenceMatcher (pas de dépendance externe).
    Retourne un score [0.0 – 1.0].
    """
    import difflib
    q = query.lower().strip()
    c = candidate.lower().strip()
    if not q or not c:
        return 0.0
    return difflib.SequenceMatcher(None, q, c).ratio()


def _combined_score(str_sim: float, time_score: float,
                    w_str: float = 0.4, w_time: float = 0.6) -> float:
    """
    Score combiné :
      - w_str  × similarité de chaîne  (nom recherché ↔ label candidat)
      - w_time × vraisemblance temporelle (dates auteur ↔ siècle ms.)

    Si aucune date n'est connue (time_score == 0), on ne pénalise pas
    trop : on bascule sur 70% str / 30% time.
    """
    if time_score == 0.0:
        w_str, w_time = 0.7, 0.3
    return round(w_str * str_sim + w_time * time_score, 3)


# ═══════════════════════════════════════════════════════════════════════════════
# 8.  EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

def build_sample_txt(entries: list[Entry]) -> str:
    """Fichier texte 1 ligne/entrée pour import INCEpTION (Plain text one sentence per line)."""
    return "\n".join(e.raw_text for e in entries) + "\n"


def build_guide_tsv(entries: list[Entry]) -> str:
    """TSV lisible par l'annotateur : texte + traductions + champs JSON + EL."""
    cols = [
        "entry_id", "source_file",
        "raw_text", "traduction_fr", "traduction_zh",
        "json_authors", "json_titles",
        "json_material", "json_date_raw", "json_date_norm",
        "ner_auteur_raw", "ner_auteur_norm",
        "ner_ouvrage_raw",
        "ner_material_raw", "ner_material_norm",
        "ner_date_raw", "ner_date_norm",
        "ner_etat",
        "ms_century_range",
        "viaf_top3 [label | dates | str= tps= ★= | uri]",
        "wikidata_top3 [label | dates | str= tps= ★= | uri]",
        "plausibilite",
    ]
    rows = ["\t".join(cols)]

    for e in entries:
        def fs(label):   # first span by label
            return next((s for s in e.spans if s.label == label), None)

        au_sp = fs("auteur");  ouv_sp = fs("ouvrage")
        mat_sp= fs("material"); dat_sp = fs("date")
        etat_str = " | ".join(s.normalized for s in e.spans if s.label == "etat")

        viaf_top = [c for c in e.el_results if c.source == "viaf"][:TOP_K]
        wd_top   = [c for c in e.el_results if c.source == "wikidata"][:TOP_K]

        def fmt_top3(candidates):
            """Formate top-3 candidats en une cellule lisible."""
            parts = []
            for i, c in enumerate(candidates, 1):
                dates = f"{c.birth or '?'}–{c.death or '?'}" if (c.birth or c.death) else "dates?"
                parts.append(
                    f"#{i} {c.label} | {dates} | "
                    f"str={c.str_sim:.2f} tps={c.score:.2f} ★={c.combined:.2f} | {c.identifier}"
                )
            return "  //  ".join(parts) if parts else "—"

        # Plausibilité globale (meilleur score combiné)
        best_combined = max((c.combined for c in e.el_results), default=0.0)
        if best_combined >= 0.8:   plaus = "✅ très probable"
        elif best_combined >= 0.5: plaus = "🟡 possible"
        elif best_combined > 0:    plaus = "🔴 peu probable"
        else:                      plaus = "❓ inconnu"

        row = [
            str(e.entry_id), e.source_file,
            e.raw_text, e.traduction_fr, e.traduction_zh,
            " | ".join(e.json_authors), " | ".join(e.json_titles),
            e.json_material, e.json_date, e.json_date_norm,
            au_sp.text if au_sp else "",
            au_sp.normalized if au_sp else "",
            ouv_sp.text if ouv_sp else "",
            mat_sp.text if mat_sp else "",
            mat_sp.normalized if mat_sp else "",
            dat_sp.text if dat_sp else "",
            dat_sp.normalized if dat_sp else "",
            etat_str,
            str(e.ms_century_range),
            fmt_top3(viaf_top),
            fmt_top3(wd_top),
            plaus,
        ]
        rows.append("\t".join(row))

    return "\n".join(rows)


def build_webanno_tsv(entries: list[Entry]) -> str:
    """
    WebAnno TSV 3.3 pour import direct dans INCEpTION.
    Une ligne par token. Chaque span NER est annoté avec :
      - label (auteur/ouvrage/material/date/etat)
      - normalized (forme normalisée)
      - el_uri (meilleur lien VIAF ou Wikidata)
    """
    lines = [
        "#FORMAT=WebAnno TSV 3.3",
        "#T_SP=webanno.custom.NER_PRIMA|label|normalized|el_uri",
        "",
    ]

    for sent_idx, entry in enumerate(entries, start=1):
        text = entry.raw_text
        lines.append(f"#Text={text}")

        tokens = list(re.finditer(r'\S+', text))
        for tok_i, tok_m in enumerate(tokens, start=1):
            ts, te = tok_m.start(), tok_m.end()
            tok_text = tok_m.group(0)

            # Trouver le span couvrant ce token
            # Condition souple : le token commence dans le span
            # OU le span finit à l'intérieur du token (ponctuation finale incluse)
            covering = next(
                (sp for sp in entry.spans
                 if sp.start <= ts < sp.end          # début du token dans le span
                 or sp.start <= te <= sp.end + 2),   # fin du token juste après le span (ponctuation)
                None
            )
            # Affiner : si plusieurs spans candidats, prendre le plus proche
            if covering is None:
                # Dernier recours : token qui chevauche le span
                covering = next(
                    (sp for sp in entry.spans
                     if ts < sp.end and te > sp.start),
                    None
                )

            if covering:
                label = covering.label
                norm  = (covering.normalized or "_").replace(" ", "_").replace("\t", " ")
                # Remplacer caractères réservés/non-ASCII pour WebAnno TSV
                norm = (norm
                        .replace("→", ">")
                        .replace("⚠", "!")
                        .replace("–", "-")
                        .replace("[", r"\[")
                        .replace("]", r"\]")
                        .replace("|", r"\|"))
                # Pour date : vérifier cohérence avec JSON
                if covering.label == "date":
                    cmp = _build_date_comparison(entry)
                    if cmp["coherent"] is False:
                        norm = norm + "_!incoherent>voir_el_report"
                # URI du meilleur candidat EL (pour auteur seulement)
                uri = "_"
                if covering.label == "auteur" and entry.el_results:
                    best = max(entry.el_results, key=lambda c: c.score)
                    uri = best.identifier or "_"
            else:
                label = norm = uri = "_"

            lines.append(f"{sent_idx}-{tok_i}\t{ts}-{te}\t{tok_text}\t"
                         f"{label}\t{norm}\t{uri}")

        lines.append("")

    return "\n".join(lines)



def _build_date_comparison(entry) -> dict:
    """
    Compare la date extraite du texte brut (catalogue.txt)
    avec la date normalisée depuis le JSON.
    Retourne un dict avec les deux valeurs et un flag de cohérence.
    """
    # Date depuis le texte brut (NER sur catalogue.txt)
    date_span = next((s for s in entry.spans if s.label == "date"), None)
    date_from_text     = date_span.text       if date_span else None
    date_from_text_norm = date_span.normalized if date_span else None

    # Date depuis le JSON (déjà normalisée)
    date_from_json      = entry.json_date       or None
    date_from_json_norm = entry.json_date_norm  or None

    # Vérification de cohérence : même siècle ?
    coherent = None
    if date_from_text_norm and date_from_json_norm:
        # Extraire le siècle romain de chaque
        import re as _re
        m_text = _re.search(r'([IVXLCDM]+)e', date_from_text_norm)
        m_json = _re.search(r'([IVXLCDM]+)e', date_from_json_norm)
        if m_text and m_json:
            coherent = (m_text.group(1) == m_json.group(1))

    return {
        "date_from_text":      date_from_text,
        "date_from_text_norm": date_from_text_norm,
        "date_from_json":      date_from_json,
        "date_from_json_norm": date_from_json_norm,
        "coherent":            coherent,
    }


def build_el_report(entries: list[Entry]) -> list[dict]:
    report = []
    for e in entries:
        report.append({
            "entry_id": e.entry_id,
            "source_file": e.source_file,
            "raw": e.raw_text,
            "traduction_fr": e.traduction_fr,
            "traduction_zh": e.traduction_zh,
            "json_authors": e.json_authors,
            "json_titles": e.json_titles,
            "json_material": e.json_material,
            "json_date": e.json_date,
            "json_date_norm": e.json_date_norm,
            "ms_century_range": list(e.ms_century_range),
            "spans": [{"label":s.label,"text":s.text,"normalized":s.normalized}
                      for s in e.spans],
            "date_comparison": _build_date_comparison(e),
            "el_results": [
                {
                    "rank": i + 1,
                    "source": c.source,
                    "identifier": c.identifier,
                    "label": c.label,
                    "birth": c.birth,
                    "death": c.death,
                    "score_temporel": round(c.score, 3),
                    "score_string": round(c.str_sim, 3),
                    "score_combine": round(c.combined, 3),
                    "note": c.note,
                }
                for i, c in enumerate(e.el_results)
            ],
        })
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# 9.  PIPELINE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def _wrap(text: str, width: int) -> list:
    """Coupe un texte long en lignes de max `width` caractères, sur les espaces."""
    if not text:
        return [""]
    words = text.split(" ")
    result_lines, current = [], ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            result_lines.append(current)
            current = word
    if current:
        result_lines.append(current)
    return result_lines


def display_sample_preview(sampled, catalogue, cat_dict):
    """
    Affiche un tableau récapitulatif des entrées tirées au sort,
    groupées par fichier source.

    Ordre des champs par entrée :
      N°  |  Texte brut complet (sans limite)
          |  FR  (traduction française)
          |  ZH  (traduction chinoise)
          |  auteur  génitif   / nominatif
          |  ouvrage génitif   / nominatif
    """
    from collections import defaultdict
    by_file = defaultdict(list)
    for fname, ms in sampled:
        by_file[fname].append(ms)

    W = 110

    print("\n" + "═" * W)
    print(f"  APERÇU DES {len(sampled)} ENTRÉES TIRÉES AU SORT")
    print("═" * W)

    for fname, mss in by_file.items():
        short = (fname.replace("Catalogo_", "")
                      .replace("_Riccardiana", "")
                      .replace(".json", ""))
        header = f"  ╔═ {short}  ({len(mss)} entrées) "
        print("\n" + header + "═" * max(0, W - len(header)))

        for ms in mss:
            eid = ms_entry_id(ms)
            raw = catalogue.get(eid, "")
            cd  = cat_dict.get(eid, {})

            fr      = cd.get("traduction_fr",    "") or "—"
            zh      = cd.get("traduction_zh",    "") or "—"
            aut_gen = cd.get("auteur_genitif",   "") or "none"
            aut_nom = cd.get("auteur_nominatif", "") or "none"
            ouv_gen = cd.get("ouvrage_genitif",  "") or "none"
            ouv_nom = cd.get("ouvrage_nominatif","") or "none"

            raw_body = re.sub(r'^\d+\s+', '', raw)

            print(f"  ╟─ #{eid}")
            for chunk in _wrap(raw_body, W - 6):
                print(f"  ║  {chunk}")
            print(f"  ║  FR : {fr}")
            print(f"  ║  ZH : {zh}")
            print(f"  ║  auteur  gén. → {aut_gen}")
            print(f"  ║  auteur  nom. → {aut_nom}")
            print(f"  ║  ouvrage gén. → {ouv_gen}")
            print(f"  ║  ouvrage nom. → {ouv_nom}")
            print(f"  ║")

        print("  ╚" + "═" * (W - 2))

    print("═" * W)


def confirm_sample(sampled, catalogue, cat_dict, seed) -> list:
    """
    Boucle interactive :
      - Affiche l'aperçu
      - Propose : [O]K / [R]enouveler / [Q]uitter
    Retourne la liste finale validée.
    """
    current_seed = seed
    current_sampled = sampled

    while True:
        display_sample_preview(current_sampled, catalogue, cat_dict)

        print("\n  Que voulez-vous faire ?")
        print("  [O] Confirmer ces entrées et continuer")
        print("  [R] Renouveler le tirage (nouveau seed aléatoire)")
        print("  [S] Entrer un seed spécifique")
        print("  [Q] Quitter")
        print()

        try:
            choice = input("  Votre choix [O/R/S/Q] : ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\n  Interruption. Au revoir.")
            sys.exit(0)

        if choice == "O":
            print(f"\n  ✅ Sélection confirmée ({len(current_sampled)} entrées, seed={current_seed})\n")
            return current_sampled

        elif choice == "R":
            current_seed = random.randint(0, 99999)
            print(f"\n  🔄 Nouveau tirage avec seed={current_seed}…")
            # On recharge le catalogue pour refaire le tirage
            # (on passe par une variable globale temporaire)
            random.seed(current_seed)
            current_sampled = _resample(current_sampled, catalogue, current_seed)

        elif choice == "S":
            try:
                current_seed = int(input("  Entrez le seed (entier) : ").strip())
                print(f"\n  🔄 Tirage avec seed={current_seed}…")
                current_sampled = _resample(current_sampled, catalogue, current_seed)
            except ValueError:
                print("  ⚠️  Seed invalide, réessayez.")

        elif choice == "Q":
            print("\n  Au revoir.")
            sys.exit(0)

        else:
            print("  ⚠️  Choix non reconnu, tapez O, R, S ou Q.")


def _resample(current_sampled, catalogue, new_seed):
    """Refait le tirage avec un nouveau seed, en conservant json_dir et n."""
    # On reconstruit la liste depuis les fichiers d'origine
    # On a besoin de json_dir et n : on les extrait du premier élément
    fname0 = current_sampled[0][0]
    n = len([x for x in current_sampled if x[0] == fname0])
    # Chercher le dossier
    import os
    json_dir = os.path.dirname(
        next((f for f in [
            os.path.join(".", fname0),
            os.path.join("/mnt/user-data/uploads", fname0),
        ] if os.path.exists(f)), ".")
    )
    return sample_from_files(json_dir, catalogue, n, new_seed)


def run(args):
    print("=" * 60)
    print("PRIMA – Pipeline NER + Entity Linking")
    print("=" * 60)

    # ── Chargement ────────────────────────────────────────────
    print("\n[1/5] Chargement des données…")
    catalogue = load_catalogue(args.catalogue)
    cat_dict  = load_cat_dict(args.cat_dict)
    print(f"  catalogue.txt : {len(catalogue)} entrées")
    print(f"  catalogue_dict : {len(cat_dict)} entrées")

    # ── Échantillonnage + confirmation interactive ─────────────
    print(f"\n[2/5] Échantillonnage ({args.sample} par fichier)…")
    sampled = sample_from_files(args.json_dir, catalogue,
                                args.sample, args.seed)

    # Confirmation interactive (sauf si --yes passé)
    if not getattr(args, 'yes', False):
        sampled = confirm_sample(sampled, catalogue, cat_dict, args.seed)
    else:
        print(f"  → {len(sampled)} entrées (confirmation automatique --yes)")

    # ── Traitement ────────────────────────────────────────────
    print(f"\n[3/5] NER + Entity Linking…")
    entries: list[Entry] = []

    for i, (fname, ms) in enumerate(sampled, start=1):
        eid = ms_entry_id(ms)
        if eid is None or eid not in catalogue:
            continue

        raw = catalogue[eid]
        jf  = extract_json_fields(ms)
        cd  = cat_dict.get(eid, {})

        entry = Entry(
            entry_id=eid,
            source_file=fname,
            raw_text=raw,
            traduction_fr=cd.get("traduction_fr", ""),
            traduction_zh=cd.get("traduction_zh", ""),
            json_material=jf["material"],
            json_date=jf["date_raw"],
            json_date_norm=jf["date_norm"],
            json_authors=jf["authors"],
            json_titles=jf["titles"],
        )

        # NER
        entry.spans = extract_spans(raw, cd)

        # Plage temporelle
        date_sp = next((s for s in entry.spans if s.label == "date"), None)
        if date_sp:
            roman = re.search(r'([IVXLCDM]+)e', date_sp.normalized)
            if roman:
                entry.ms_century_range = century_to_range(roman.group(1))
        # Fallback : utiliser la date du JSON
        if not entry.ms_century_range:
            roman2 = re.search(r'([IVXLCDM]+)', jf["date_norm"])
            if roman2:
                entry.ms_century_range = century_to_range(roman2.group(1))

        # Log
        authors_str = " | ".join(jf["authors"][:2]) or "(sans auteur)"
        print(f"  [{i:3d}/{len(sampled)}] #{eid:4d}  {authors_str[:40]}")

        entries.append(entry)

    # ── Aperçu interactif + confirmation ─────────────────────
    print("\n" + "=" * 60)
    print("APERÇU DES 100 ENTRÉES SÉLECTIONNÉES")
    print("=" * 60)

    # Grouper par fichier source
    by_file: dict[str, list[Entry]] = {}
    for e in entries:
        by_file.setdefault(e.source_file, []).append(e)

    for fname, elist in by_file.items():
        label = fname.replace("Catalogo_", "").replace("_Riccardiana", "").replace(".json", "")
        print(f"\n  ┌─ [{label}]  ({len(elist)} entrées)")
        for e in elist:
            authors_str = " | ".join(e.json_authors[:2]) if e.json_authors else "—"
            date_str    = e.json_date_norm or "—"
            # Indicateur NER : quels spans trouvés
            found = [s.label[0].upper() for s in e.spans]  # A O M D E
            ner_str = "".join(sorted(set(found))) if found else "·"
            print(f"  │  #{e.entry_id:4d}  {ner_str:5s}  "
                  f"{authors_str[:35]:<35}  {date_str:<20}  "
                  f"{e.raw_text[len(str(e.entry_id))+1:50]}…")
        print(f"  └{'─'*58}")

    print(f"\nLégende NER trouvé : A=auteur  O=ouvrage  M=material  D=date  E=etat")
    print(f"Seed utilisé : {args.seed}  |  Total : {len(entries)} entrées\n")

    # Demander confirmation
    while True:
        print("Options :")
        print("  [o]  Confirmer et générer les fichiers")
        print("  [r]  Relancer avec un seed différent")
        print("  [q]  Quitter sans générer")
        choix = input("\nVotre choix : ").strip().lower()

        if choix == "o":
            break
        elif choix == "r":
            new_seed = input("Nouveau seed (entier) : ").strip()
            try:
                args.seed = int(new_seed)
            except ValueError:
                print("  Seed invalide, on garde l'ancien.")
                continue
            print(f"\nRelance avec seed={args.seed}…\n")
            # Réchantillonner
            random.seed(args.seed)
            sampled = sample_from_files(args.json_dir, catalogue,
                                        args.sample, args.seed)
            entries = []
            for fname, ms in sampled:
                eid = ms_entry_id(ms)
                if eid is None or eid not in catalogue:
                    continue
                raw = catalogue[eid]
                jf  = extract_json_fields(ms)
                cd  = cat_dict.get(eid, {})
                entry = Entry(
                    entry_id=eid, source_file=fname, raw_text=raw,
                    traduction_fr=cd.get("traduction_fr",""),
                    traduction_zh=cd.get("traduction_zh",""),
                    json_material=jf["material"], json_date=jf["date_raw"],
                    json_date_norm=jf["date_norm"],
                    json_authors=jf["authors"], json_titles=jf["titles"],
                )
                entry.spans = extract_spans(raw, cd)
                date_sp = next((s for s in entry.spans if s.label=="date"), None)
                if date_sp:
                    roman = re.search(r'([IVXLCDM]+)e', date_sp.normalized)
                    if roman:
                        entry.ms_century_range = century_to_range(roman.group(1))
                entries.append(entry)
            # Réafficher
            print("\n" + "=" * 60)
            print(f"NOUVEAU TIRAGE (seed={args.seed})")
            print("=" * 60)
            by_file = {}
            for e in entries:
                by_file.setdefault(e.source_file, []).append(e)
            for fname2, elist in by_file.items():
                label = fname2.replace("Catalogo_","").replace("_Riccardiana","").replace(".json","")
                print(f"\n  ┌─ [{label}]  ({len(elist)} entrées)")
                for e in elist:
                    authors_str = " | ".join(e.json_authors[:2]) if e.json_authors else "—"
                    date_str    = e.json_date_norm or "—"
                    found = [s.label[0].upper() for s in e.spans]
                    ner_str = "".join(sorted(set(found))) if found else "·"
                    print(f"  │  #{e.entry_id:4d}  {ner_str:5s}  "
                          f"{authors_str[:35]:<35}  {date_str:<20}  "
                          f"{e.raw_text[len(str(e.entry_id))+1:50]}…")
                print(f"  └{'─'*58}")
            print(f"\nSeed : {args.seed}  |  Total : {len(entries)} entrées\n")
        elif choix == "q":
            print("Abandon. Aucun fichier généré.")
            return []
        else:
            print("  Réponse non reconnue, tapez o / r / q.")

    # ── Export ────────────────────────────────────────────────
    print(f"\n[4/5] Export…")
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1. Texte pour INCEpTION (1 ligne / entrée)
    p1 = out / "sample_for_inception.txt"
    p1.write_text(build_sample_txt(entries), encoding="utf-8")
    print(f"  → {p1}  ({len(entries)} lignes)")

    # 2. Guide annotateur (TSV)
    p2 = out / "annotation_guide.tsv"
    p2.write_text(build_guide_tsv(entries), encoding="utf-8")
    print(f"  → {p2}")

    # 3. Rapport EL (JSON)
    p3 = out / "el_report.json"
    p3.write_text(json.dumps(build_el_report(entries),
                             ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  → {p3}")

    # 4. Pré-annotation WebAnno TSV (INCEpTION)
    p4 = out / "webanno_preannotation.tsv"
    p4.write_text(build_webanno_tsv(entries), encoding="utf-8")
    print(f"  → {p4}")

    print(f"\n[5/5] Terminé. {len(entries)} entrées traitées.")
    print(f"      Fichiers dans : {out.resolve()}")

    # Auto-upload TSV désactivé (utiliser inject_annotations.py)

    return entries



# ═══════════════════════════════════════════════════════════════════════════════
# 11.  INCEPTION AUTO-UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════

INCEPTION_BASE    = "http://localhost:8080"
INCEPTION_USER    = "admin"
INCEPTION_PASS    = "Zrx12345"
INCEPTION_PROJECT = "admin-1"   # slug du projet
INCEPTION_API     = "api/aero/v1"   # version API INCEpTION 40.x


def inception_get_project_id(base: str, auth: tuple, project_slug: str) -> int | None:
    """
    通过 slug 查找项目 ID。
    API 返回格式：{"1": {"admin-1": [roles]}, "0": {"admin": [roles]}}
    project_slug 对应 URL 里的 slug，如 "admin-1"。
    """
    try:
        r = requests.get(f"{base}/api/aero/v1/projects", auth=auth, timeout=8)
        r.raise_for_status()
        data = r.json()
        # Format INCEpTION 40.x : {"body": [...], "messages": [...]}
        projects = data.get("body", data) if isinstance(data, dict) else data
        if isinstance(projects, list):
            # Chercher par name ou slug
            for proj in projects:
                if proj.get("name") == project_slug:
                    return int(proj["id"])
            # Fallback : premier projet
            if projects:
                first = projects[0]
                print(f"  [INFO] Slug '{project_slug}' non trouvé, utilisation de '{first.get('name','?')}'")
                return int(first["id"])
    except Exception as e:
        print(f"  [WARN] Impossible de contacter INCEpTION : {e}")
    return None


def inception_upload_document(base: str, auth: tuple, project_id: int,
                               filepath: str, fmt: str = "text") -> bool:
    """上传文档到 INCEpTION（API aero/v1）。"""
    url   = f"{base}/api/aero/v1/projects/{project_id}/documents"
    fname = os.path.basename(filepath)

    # 删除同名旧文档
    try:
        r = requests.get(url, auth=auth, timeout=8)
        if r.status_code == 200:
            for doc in r.json() if isinstance(r.json(), list) else []:
                if doc.get("name") == fname:
                    requests.delete(f"{url}/{doc['id']}", auth=auth, timeout=8)
                    print(f"  [INFO] Document existant supprimé : {fname}")
                    break
    except Exception:
        pass

    # Upload
    try:
        with open(filepath, "rb") as f_obj:
            r = requests.post(
                url,
                auth=auth,
                files={"content": (fname, f_obj, "text/plain")},
                data={"name": fname, "format": fmt},
                timeout=15,
            )
        if r.status_code in (200, 201):
            print(f"  ✅ Document uploadé : {fname}")
            return True
        else:
            print(f"  ❌ Erreur upload ({r.status_code}) : {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur upload : {e}")
        return False


def auto_upload_to_inception(sample_txt_path: str) -> None:
    """
    脚本确认后自动将 webanno_preannotation.tsv 推送至 INCEpTION。
    若 INCEpTION 不可达则跳过，不报错中断。
    """
    print(f"\n[AUTO-UPLOAD] Connexion à INCEpTION ({INCEPTION_BASE})…")
    auth = (INCEPTION_USER, INCEPTION_PASS)

    project_id = inception_get_project_id(INCEPTION_BASE, auth, INCEPTION_PROJECT)
    if project_id is None:
        print(f"  [WARN] Projet « {INCEPTION_PROJECT} » introuvable ou INCEpTION hors ligne.")
        print("  → Upload ignoré. Importez manuellement webanno_preannotation.tsv (INCEpTION → Documents → Format : WebAnno TSV 3)")
        return

    print(f"  Projet trouvé : ID={project_id}")
    inception_upload_document(
        INCEPTION_BASE, auth, project_id,
        sample_txt_path,
        fmt="ctsv3",
    )
    print(f"  → Ouvrez INCEpTION : {INCEPTION_BASE}/#/p/{project_id}/annotate")


# ═══════════════════════════════════════════════════════════════════════════════
# 10.  CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="PRIMA – NER + Entity Linking + export INCEpTION"
    )
    parser.add_argument("--json_dir",   default=".",
                        help="Dossier contenant les 4 JSON Riccardiana")
    parser.add_argument("--catalogue",  default="catalogue.txt")
    parser.add_argument("--cat_dict",   default="catalogue_dict.json")
    parser.add_argument("--sample",     type=int, default=25,
                        help="Entrées à tirer par fichier JSON (défaut: 25)")
    parser.add_argument("--seed",       type=int, default=42)
    parser.add_argument("--out_dir",    default="output_inception")
    parser.add_argument("--yes",        action="store_true",
                        help="Confirme automatiquement sans interaction (mode batch)")
    parser.add_argument("--no_upload",  action="store_true",
                        help="Désactive l'upload automatique vers INCEpTION")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
