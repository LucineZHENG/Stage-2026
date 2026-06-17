# Rapport de division des données — PRIMA NER (corpus complet)

Seed : 42 | Total : 938 entrées | Train : 657 / Val : 188 / Test : 93

Sources :
- `gold_annotations_with_el.json` (100 entrées, gold standard)
- `gold_annotations_remaining_el.json` (838 entrées restantes)


---

## TRAIN — 657 entrées

### Distribution des labels

| Label | Nb spans | % |
|---|---|---|
| auteur | 596 | 21.1% |
| ouvrage | 777 | 27.5% |
| material | 650 | 23.0% |
| date | 646 | 22.9% |
| etat | 152 | 5.4% |
| **Total** | **2821** | 100% |

### Caractéristiques

- Longueur moyenne : **16.5 tokens** (min 8, max 162)
- Spans par entrée (moyenne) : **4.3**
- Entrées avec `auteur`  : **465**
- Entrées avec `ouvrage` : **646**
- Entrées avec `etat`    : **146**
- Entrées sans spans     : **0**

### Sources

| Source | Nb entrées |
|---|---|
| gold_100 | 67 |
| remaining_838 | 590 |

---

## VAL — 188 entrées

### Distribution des labels

| Label | Nb spans | % |
|---|---|---|
| auteur | 162 | 20.5% |
| ouvrage | 225 | 28.4% |
| material | 188 | 23.8% |
| date | 186 | 23.5% |
| etat | 30 | 3.8% |
| **Total** | **791** | 100% |

### Caractéristiques

- Longueur moyenne : **15.8 tokens** (min 9, max 52)
- Spans par entrée (moyenne) : **4.2**
- Entrées avec `auteur`  : **126**
- Entrées avec `ouvrage` : **183**
- Entrées avec `etat`    : **30**
- Entrées sans spans     : **0**

### Sources

| Source | Nb entrées |
|---|---|
| gold_100 | 19 |
| remaining_838 | 169 |

---

## TEST — 93 entrées

### Distribution des labels

| Label | Nb spans | % |
|---|---|---|
| auteur | 79 | 19.9% |
| ouvrage | 112 | 28.3% |
| material | 91 | 23.0% |
| date | 92 | 23.2% |
| etat | 22 | 5.6% |
| **Total** | **396** | 100% |

### Caractéristiques

- Longueur moyenne : **16.2 tokens** (min 2, max 54)
- Spans par entrée (moyenne) : **4.3**
- Entrées avec `auteur`  : **60**
- Entrées avec `ouvrage` : **89**
- Entrées avec `etat`    : **22**
- Entrées sans spans     : **1**

### Sources

| Source | Nb entrées |
|---|---|
| gold_100 | 14 |
| remaining_838 | 79 |
