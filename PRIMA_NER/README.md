# Stage-2026

Dépôt de code du stage PRIMA (ERC Grant 101142242), centré sur la reconnaissance d'entités nommées (NER) et la liaison d'entités (EL) appliquées aux catalogues de manuscrits latins médiévaux.

Laboratoire d'accueil : LIFAT, Université de Tours  
Encadrant : Carlos-Emiliano González-Gallardo  
Période : avril — novembre 2026

---

## Structure du dépôt

```
Stage-2026/
├── pipeline_gold/        # Pipeline complet — 100 entrées gold standard
├── pipeline_remaining/   # Pipeline — 838 entrées restantes
└── monitor_apps/         # Interfaces Flask de surveillance et validation
```

---

## I. Pipeline gold standard — 100 entrées

Source : catalogue de la Biblioteca Riccardiana (échantillon de 100 entrées parmi les n° 221–1700)

### Étapes

| Étape | Script | Entrée | Sortie |
|-------|--------|--------|--------|
| Step 1 — NER + EL automatique | `prima_pipeline.py` | 4 JSON Riccardiana + `catalogue.txt` + `catalogue_dict.json` | `webanno_preannotation.tsv` / `annotation_guide.tsv` / `el_report.json` |
| Step 2 — Correction manuelle INCEpTION | — (opération manuelle) | `sample_for_inception.txt` | `admin.json` |
| Step 3 — Fusion annotations + métadonnées | `merge_annotations.py` | `admin.json` + `el_report.json` | `gold_annotations.json` |
| Step 4 — Recherche EL (interface de surveillance) | `monitor_apps/prima_monitor.py` | Annotations INCEpTION en temps réel | `el_auteur_ouvrage.jsonl` |
| Step 5 — Fusion résultats EL | `merge_el.py` | `gold_annotations.json` + `el_auteur_ouvrage.jsonl` | `gold_annotations_with_el.json` |
| Step 6 — Validation experte | `monitor_apps/prima_monitor_expert.py` | `gold_annotations_with_el.json` | `el_validated.jsonl / .json / .csv` |

> **À propos de `gold_annotations.json`** : `el_report.json` contient les annotations automatiques du pipeline ainsi que les métadonnées (traduction française, comparaison de dates, etc.) ; `admin.json` contient les annotations corrigées manuellement dans INCEpTION. La fusion consiste à substituer les annotations automatiques par les annotations manuelles tout en conservant les métadonnées. Le résultat constitue un jeu de données de référence (*gold standard*) au sens NLP du terme.

### Scripts auxiliaires

- `MAPPING_date.py` : normalisation du champ date
- `MAPPING_mfe.py` : normalisation des champs en moyen français

---

## II. Pipeline — 838 entrées restantes

Source : entrées du catalogue de la Biblioteca Riccardiana non incluses dans les 100 entrées gold

### Étapes

| Étape | Script | Entrée | Sortie |
|-------|--------|--------|--------|
| Étape 1 — Préparation des données | `prepare_remaining.py` | Catalogue brut | `remaining_for_inception.txt` / `remaining_guide.tsv` / `remaining_entries.json` |
| Étape 2 — Annotation INCEpTION + EL temps réel | `prima_monitor_remaining.py` | API INCEpTION (interrogation toutes les 2 s) | `el_auteur_ouvrage_remaining.jsonl` |
| Étape 3 — Fusion annotations NER + métadonnées | `merge_annotations_remaining.py` | `admin.json` + `remaining_entries.json` | `gold_annotations_remaining.json` |
| Étape 4 — Fusion résultats EL | `merge_el_remaining.py` | `gold_annotations_remaining.json` + `el_auteur_ouvrage_remaining.jsonl` | `gold_annotations_remaining_el.json` |
| Étape 5 — Validation experte | `prima_monitor_expert_remaining.py` | `gold_annotations_remaining_el.json` | `el_validated_remaining.jsonl / .json / .csv` |

---

## III. Interfaces de surveillance et de validation

| Script | Fonction | Port par défaut |
|--------|----------|-----------------|
| `prima_monitor.py` | Écoute INCEpTION en temps réel et déclenche automatiquement la recherche VIAF/Wikidata sur les spans auteur/ouvrage (100 entrées gold) | 5051 |
| `prima_monitor_remaining.py` | Même fonction pour les 838 entrées restantes | 5051 |
| `prima_monitor_expert.py` | Validation experte des candidats VIAF/Wikidata (100 entrées gold), résultats sauvegardés en trois formats | 5052 |
| `prima_monitor_expert_remaining.py` | Validation experte des candidats VIAF/Wikidata (838 entrées), résultats sauvegardés en trois formats | 5053 |

> `prima_monitor.py` et `prima_monitor_remaining.py` utilisent le même port (5051) et ne sont jamais lancés simultanément.

---

## Données

Tous les fichiers `.json` / `.jsonl` / `.csv` **ne sont pas versionnés dans ce dépôt** et sont gérés localement dans les répertoires `output_EL/`, `output_inception/` et `output_remaining/`.
