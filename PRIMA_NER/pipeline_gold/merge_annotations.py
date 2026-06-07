"""
merge_annotations.py
====================
Fusion de el_report.json (NER automatique, pipeline) et admin.json
(annotation manuelle exportée depuis INCEpTION) en un fichier gold unifié.

═══════════════════════════════════════════════════════════════════════════════
ANALYSE DES DIFFÉRENCES ENTRE LES DEUX FICHIERS
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────
│ FICHIER 1 : el_report.json
│   - Généré automatiquement par prima_pipeline.py
│   - 100 entrées, chacune avec : entry_id, raw, spans[], el_results[]
│   - Chaque span contient : label, text, normalized
│   - normalized : rempli automatiquement via MAPPING_mfe.py / MAPPING_date.py
│     et catalogue_dict.json
│   - el_results : VIDE (EL non effectué, interface monitor non fonctionnelle)
│
│ FICHIER 2 : admin.json
│   - Export UIMA CAS JSON 0.4.0 depuis INCEpTION après annotation manuelle
│   - 422 spans annotés manuellement sur les 100 entrées
│   - Chaque span contient : label, begin, end (offsets caractères dans le texte)
│   - normalized : VIDE (non rempli dans INCEpTION, normal : c'est le monitor
│     qui devait le calculer automatiquement)
│   - el_uri : VIDE (monitor non fonctionnel, sera complété ultérieurement)
└─────────────────────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════════════════════
CAS 1 — SPANS DANS admin.json MAIS ABSENTS DE el_report.json
         (pipeline a raté ces entités → on les AJOUTE au gold)
═══════════════════════════════════════════════════════════════════════════════

Ces spans ont été détectés manuellement mais le pipeline ne les avait pas
extraits (auteurs italiens/grecs sans génitif, œuvres manquées, material
sans format, etat non standard).

  Auteurs manqués par le pipeline :
    #233  [auteur]  'S. Augustini'              (génitif court, non matché)
    #239  [auteur]  'Petro de Riga'
    #257  [auteur]  'Gasparis Pasquali'
    #276  [auteur]  'Hieronymi' + 'Origenis'    (deux auteurs)
    #286  [auteur]  'S. Ephraem' + 'Chrysostomi'
    #312  [auteur]  'Hieronymi' + 'Rufini'
    #335  [auteur]  'Girolamo' + 'Agostino' + 'Gregorio'  (forme italienne)
    #350  [auteur]  'Prosperi' + 'Aesopi'
    #351  [auteur]  'Basilii' + 'Marsilii Ficini'
    #379  [auteur]  'Bedae' + 'S. Augustini'
    #406  [auteur]  'Bardis de Roberti'
    #434  [auteur]  'Isaaci'
    #509  [auteur]  'Ciceronis' + 'Demosthenis'
    #1061  [auteur]  manquant (Boccaccio, forme italienne)
    #1174  [auteur]  'Cermusona Ant'
    #1183  [auteur]  'Capponi March. Vincenzio'
    #1240  [auteur]  'Ambrosit Camaldulensis' + 'Ciceronis' + 'Poggii'
    #1298  [auteur]  'da Cascia Fra Simone'
    #1349  [auteur]  'S. Bernardo'
    #1421  [auteur]  'S. Gregorio'
    #1439  [auteur]  'Cavalca'                  (forme italienne)
    #1444  [auteur]  'S. Girolamo' + 'S. Agostin'
    #1507  [auteur]  'S. Antonino'
    #1554  [auteur]  'T. Livio'
    #1592  [auteur]  'Boccaccium'
    #1618  [auteur]  'Boezio' + 'M. Alberto'
    #1630  [auteur]  'S. Gregorio' + 'S. Gio. Grisostomo'

  Œuvres manquées par le pipeline :
    #236  [ouvrage]  'Historia Ecclesiastica'
    #239  [ouvrage]  'Vetus et Novum Testamentum'
    #250  [ouvrage]  'Compendium Moralium'
    #257  [ouvrage]  'Synodus Dioecesan'
    #275  [ouvrage]  'in Matthaeum'
    #276  [ouvrage]  'translatio de Tractatu' + 'in Epithalamicis'
    #293  [ouvrage]  'Evang. S. Johanni'
    #310  [ouvrage]  'Passionarium SS'
    #318  [ouvrage]  'De conditionibus ad rite sumendam'
    #334  [ouvrage]  'vita S. Nicolai'
    #338  [ouvrage]  'chronicon et alia'
    #350  [ouvrage]  'Aesopi fabulae'
    #351  [ouvrage]  'oratio ad juvenes'
    #359  [ouvrage]  'Brevia'
    #367  [ouvrage]  'Etymologicum nominum hebraicorum'
    #379  [ouvrage]  'dererum natura' + 'Psalterium'
    #406  [ouvrage]  'Sermones'
    #432  [ouvrage]  'Officium B. M. Virginis'
    #434  [ouvrage]  'Collationes'
    #457  [ouvrage]  'Officium B. M. Virginia'
    #469  [ouvrage]  'Officium B. M. Virginis'
    #509  [ouvrage]  'Questiones Tusculanae' + 'Philppica octava'
    #516  [ouvrage]  'de Senectute'
    #1240  [ouvrage]  'Epistolae'
    #1251  [ouvrage]  'Epistole e Vangeli volgarizz'
    #1270  [ouvrage]  'Trattati morali e rettorici'
    #1298  [ouvrage]  'Esposizione dei Vangeli'
    #1349  [ouvrage]  'Apocalisse di S. Gio' + 'del governo della famiglia'
    #1421  [ouvrage]  'Dialoghi Volgarizzati'
    #1439  [ouvrage]  "Specchio de' Peccati"
    #1444  [ouvrage]  'Regola Latina e Volgare'
    #1507  [ouvrage]  "Trattato de' peccati mortali"
    #1554  [ouvrage]  'la prima Deca volgarizzata'
    #1592  [ouvrage]  'Geta e Birria'
    #1618  [ouvrage]  'Boezio, volgarizzato'
    #1630  [ouvrage]  'Morali volgarizzati'

  Material sans format (pipeline ne génère pas de span si format absent) :
    #312  [material]  'Cod. chart.'
    #338  [material]  'Cod. membr.'
    #497  [material]  'Cod, membr.'       (virgule au lieu de point)
    #503  [material]  'Cod partim membr. partim chartac.'
    #504  [material]  'Cod membr.'
    #1061  [material]  'Cod. cart.'
    #1507  [material]  'Cod. cartac.'

  Etat non standard :
    #233  [etat]  'elegantissimis'
    #504  [etat]  'nitidissimus'

═══════════════════════════════════════════════════════════════════════════════
CAS 2 — SPANS DANS el_report.json MAIS ABSENTS DE admin.json
         (erreurs du pipeline → on les SUPPRIME du gold)
═══════════════════════════════════════════════════════════════════════════════

Seulement 2 cas, tous deux des erreurs pipeline confirmées :

  #332  [auteur]  'incerti Auctoris'  → pipeline a pris "auteur inconnu"
                                        comme nom d'auteur. SUPPRIMÉ.
  #383  [date]    'Saeculo. C'        → regex a capturé 'Saeculo' suivi de
                                        'C' (début de 'Cod.'). SUPPRIMÉ.

═══════════════════════════════════════════════════════════════════════════════
CAS 3 — SPANS FRAGMENTÉS DANS admin.json (LIMITATION INCEpTION)
         Les spans ne peuvent pas être discontiguus dans INCEpTION.
         Quand une date ou un autre span interrompt un material/auteur,
         on obtient deux fragments séparés pour ce qui est conceptuellement
         une seule entité.
═══════════════════════════════════════════════════════════════════════════════

  Fragments de material (date interposée) :
    #249  [material]  ['Cod. chart', 'n fol.']
                      → texte original : "Cod. chart. Saec. XVII in fol."
    #276  [material]  ['Cod. membr.', 'in fol.']
    #335  [material]  ['Cod. membran', 'in 8']
    #448  [material]  ['Cod. chartac.', 'in octavo']
    #451  [material]  ['Cod. chartac.', 'in octavo']

  Deux auteurs dans la même entrée (annotés séparément, normal) :
    #276  [auteur]  ['Hieronymi', 'Origenis']
    #286  [auteur]  ['S. Ephraem', 'Chrysostomi']
    #312  [auteur]  ['Hieronymi', 'Rufini']
    #335  [auteur]  ['Girolamo', 'Agostino', 'Gregorio']
    #350  [auteur]  ['Prosperi', 'Aesopi']
    #351  [auteur]  ['Basilii', 'Marsilii Ficini']
    #359  [auteur]  ['Clementis VII', 'Paulli III']
    #379  [auteur]  ['Bedae', 'S. Augustini']
    #509  [auteur]  ['Ciceronis', 'Demosthenis']
    #1240  [auteur]  ['Ambrosit Camaldulensis', 'Ciceronis', 'Poggii,']
    #1444  [auteur]  ['S. Girolamo', 'S. Agostin']
    #1618  [auteur]  ['Boezio', 'M. Alberto']
    #1630  [auteur]  ['S. Gregorio', 'S. Gio. Grisostomo']

  Deux œuvres dans la même entrée (annotées séparément, normal) :
    #293  [ouvrage]  ['S. Matthaei Evangelium', 'Evang. S. Johanni']
    #350  [ouvrage]  ['de virtute activa et contemplativa', 'Aesopi fabulae']
    #379  [ouvrage]  ['dererum natura', 'Psalterium']
    #434  [ouvrage]  ['Evangelia', 'Collationes']
    #509  [ouvrage]  ['Questiones Tusculanae', 'Philppica octava']
    #1270  [ouvrage]  ['Trattati morali e rettorici', "volgarizzamento dell'Eneide"]
    #1349  [ouvrage]  ['Apocalisse di S. Gio', 'del governo della famiglia']

  Deux états dans la même entrée (annotés séparément, normal) :
    #276  [etat]  ['in fine mutilus', 'bene servatus']

═══════════════════════════════════════════════════════════════════════════════
CE QUI EST REMPLACÉ / AJOUTÉ DANS LE FICHIER GOLD
═══════════════════════════════════════════════════════════════════════════════

  REMPLACÉ : el_report.json["spans"] → remplacé par les spans de admin.json
             (annotation manuelle = gold standard, plus fiable)

  CONSERVÉ  : el_report.json["entry_id", "raw", "source_file",
               "traduction_fr", "traduction_zh", "json_authors",
               "json_titles", "json_material", "json_date",
               "json_date_norm", "ms_century_range"]
             (métadonnées non touchées par l'annotation manuelle)

  SUPPRIMÉ  : les 2 spans pipeline erronés (#332 auteur, #383 date)

  AJOUTÉ    : les 181 spans manuels absents du pipeline (Cas 1)

═══════════════════════════════════════════════════════════════════════════════
CE QUI RESTE VIDE EN ATTENTE DE L'INTERFACE MONITOR
═══════════════════════════════════════════════════════════════════════════════

  Pour chaque span de type auteur ou ouvrage :
    - "normalized" : sera calculé automatiquement par normalize() du monitor
    - "el_uri"     : sera rempli après validation VIAF/Wikidata via le monitor
                     et sauvegardé dans output_EL/el_auteur_ouvrage.jsonl

  Pour material / date / etat :
    - "normalized" : récupéré depuis MAPPING_mfe.py et MAPPING_date.py
                     (rempli automatiquement par ce script)
    - "el_uri"     : non applicable (pas d'EL pour ces types)

═══════════════════════════════════════════════════════════════════════════════
"""

import json
import re
import os
import sys

# ── Chemins ──────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.join(_HERE, '..')

ADMIN_JSON      = os.path.join(_HERE,   "admin.json")
EL_REPORT_JSON  = os.path.join(_HERE,   "el_report.json")
SAMPLE_TXT      = os.path.join(_HERE,   "sample_for_inception.txt")
OUTPUT_JSON     = os.path.join(_HERE,   "gold_annotations.json")

# ── Import des mappings ───────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from MAPPING_mfe import SUPPORT_NORM, FORMAT_NORM, MATERIAL_COMBINATIONS, ETAT_NORM
from MAPPING_date import CENTURIES, PERIODS


def normalize_material(text):
    """Cherche la forme normalisée pour un span material."""
    t = text.strip()
    if t in MATERIAL_COMBINATIONS:
        return MATERIAL_COMBINATIONS[t]
    # Cherche support seul
    for k, v in SUPPORT_NORM.items():
        if t == k or t.startswith(k):
            return v
    # Cherche format seul
    for k, v in FORMAT_NORM.items():
        if k in t:
            return v
    return t  # fallback : texte brut


def normalize_etat(text):
    """Cherche la forme normalisée pour un span etat."""
    t = text.strip().lower()
    for k, v in ETAT_NORM.items():
        if k.lower() in t or t in k.lower():
            return v
    return text.strip()


def normalize_date(text):
    """Normalisation minimale pour date : retourne le texte brut nettoyé."""
    # La normalisation complète est faite par le monitor ; ici on garde le texte
    return text.strip()


def auto_normalize(label, text):
    """Dispatcher de normalisation selon le label."""
    if label == 'material':
        return normalize_material(text)
    elif label == 'etat':
        return normalize_etat(text)
    elif label == 'date':
        return normalize_date(text)
    else:
        # auteur / ouvrage : normalized sera rempli par le monitor
        return ""


def load_admin_spans(admin_path, sample_path):
    """
    Extrait les spans annotés manuellement depuis admin.json,
    les associe à leur entry_id via sample_for_inception.txt.
    Retourne : dict { entry_id -> list[{label, text, normalized, el_uri}] }
    """
    with open(admin_path, encoding='utf-8') as f:
        data = json.load(f)

    fs = data.get('%FEATURE_STRUCTURES', {})
    fs_list = list(fs.values()) if isinstance(fs, dict) else fs

    # Texte source
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

    # Mapping offset → entry_id
    with open(sample_path, encoding='utf-8') as f:
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
    for a in ner:
        begin = int(a.get('begin', 0))
        end   = int(a.get('end', 0))
        label = a.get('label', '').strip()
        if not label:
            continue
        span_text = text[begin:end].strip()
        eid = get_eid(begin, end)
        if eid is None:
            continue
        normalized = auto_normalize(label, span_text)
        result.setdefault(eid, []).append({
            "label":      label,
            "text":       span_text,
            "normalized": normalized,
            "el_uri":     ""   # sera rempli par le monitor après EL
        })

    return result


def merge(admin_path, el_path, sample_path, output_path):
    admin_spans = load_admin_spans(admin_path, sample_path)

    with open(el_path, encoding='utf-8') as f:
        el_data = json.load(f)

    gold = []
    for entry in el_data:
        eid = entry['entry_id']
        new_entry = {k: v for k, v in entry.items() if k != 'spans'}
        new_entry['spans'] = admin_spans.get(eid, [])
        # el_results reste vide, sera rempli par le monitor
        new_entry['el_results'] = entry.get('el_results', [])
        gold.append(new_entry)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(gold, f, ensure_ascii=False, indent=2)

    total_spans = sum(len(e['spans']) for e in gold)
    print(f"[OK] {len(gold)} entrées → {total_spans} spans → {output_path}")

    # Statistiques
    from collections import Counter
    counts = Counter(sp['label'] for e in gold for sp in e['spans'])
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    merge(ADMIN_JSON, EL_REPORT_JSON, SAMPLE_TXT, OUTPUT_JSON)
