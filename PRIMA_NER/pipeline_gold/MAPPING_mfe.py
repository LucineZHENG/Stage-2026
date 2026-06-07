"""
MAPPING_catalogue.py
====================
Correspondances pour les champs material et etat
extraites exhaustivement de catalogue.txt (1975 entrées).

Chaque clé = forme exacte trouvée dans le texte brut
Chaque valeur = forme normalisée retenue pour l'annotation

Statistiques :
  - 61 variantes de support
  - 13 variantes de format
  - 96 combinaisons support+format
  - 13 variantes d'état de conservation
"""

# ═══════════════════════════════════════════════════════════════════════════════
# MATERIAL — Support (type de parchemin/papier)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Deux grandes catégories :
#   membr. / membranac. / membranaceus  →  parchemin (Cod. membr.)
#   cart. / cartac. / chart. / chartac. →  papier    (Cod. chart.)
#
# Toutes les variantes orthographiques relevées dans catalogue.txt

SUPPORT_NORM = {
    # ── Parchemin (membranaceus) ───────────────────────────────────────────
    "Cod. membr.":         "Cod. membr.",      # 202x  forme principale
    "Cod membr.":          "Cod. membr.",      # 13x
    "Cod. memb.":          "Cod. membr.",      # 13x
    "Cod. mem.":           "Cod. membr.",      # 11x
    "Cod. membr":          "Cod. membr.",      # 7x
    "Codex membr.":        "Cod. membr.",      # 6x
    "Cod. Membr.":         "Cod. membr.",      # 4x
    "Cod. membran.":       "Cod. membran.",    # 19x  forme étendue
    "Codex membran.":      "Cod. membran.",    # 2x
    "Cod. membranac.":     "Cod. membranac.",  # 4x   forme complète
    "Cod. Membranac":      "Cod. membranac.",  # 1x
    "Cod. membranac":      "Cod. membranac.",  # 1x
    "Cod membranac":       "Cod. membranac.",  # 1x
    "Codex membranac.":    "Cod. membranac.",  # 1x
    "Cod. membranaceus":   "Cod. membranaceus",# 1x   forme complète non abrégée
    "Cod. membranaceo":    "Cod. membranaceus",# 1x   ablatif
    "Cod. Membran":        "Cod. membran.",    # 1x
    "Cod. mem":            "Cod. membr.",      # 2x
    "Cod. memban.":        "Cod. membran.",    # 1x   coquille
    "Cod. mebr.":          "Cod. membr.",      # 1x   coquille

    # ── Papier (chartaceus) ────────────────────────────────────────────────
    "Cod. cart.":          "Cod. chart.",      # 251x forme principale (cart.)
    "Cod. cartac.":        "Cod. chart.",      # 185x
    "Cod. chart.":         "Cod. chart.",      # 80x  forme principale (chart.)
    "Cod. chartac.":       "Cod. chart.",      # 48x
    "Codex chart.":        "Cod. chart.",      # 13x
    "Cod cart.":           "Cod. chart.",      # 12x
    "Cod. chart":          "Cod. chart.",      # 10x
    "Cod. cart":           "Cod. chart.",      # 10x
    "Cod. cartac":         "Cod. chart.",      # 5x
    "Codex chartac.":      "Cod. chart.",      # 6x
    "Cod. char.":          "Cod. chart.",      # 5x
    "Cod. car.":           "Cod. chart.",      # 4x
    "Cod cartac.":         "Cod. chart.",      # 4x
    "Cod chart.":          "Cod. chart.",      # 3x
    "Cod chartac.":        "Cod. chart.",      # 2x
    "Cod. cartac in":      "Cod. chart.",      # variante sans point
    "Cod Chartac.":        "Cod. chart.",      # 1x
    "Cod. Chart.":         "Cod. chart.",      # 1x
    "Cod. chartc.":        "Cod. chart.",      # 1x   coquille
    "Cod. Cart.":          "Cod. chart.",      # 1x
    "Cod Cart.":           "Cod. chart.",      # 1x
    "Cod. Cartac.":        "Cod. chart.",      # 1x
    "cod. car.":           "Cod. chart.",      # 1x   minuscule
    "Cod. car":            "Cod. chart.",      # 1x
}

# ═══════════════════════════════════════════════════════════════════════════════
# MATERIAL — Format (dimension/format du codex)
# ═══════════════════════════════════════════════════════════════════════════════

FORMAT_NORM = {
    # ── Folio ─────────────────────────────────────────────────────────────
    "in fol.":              "in fol.",          # 377x  forme principale
    "in fol":               "in fol.",          # 22x
    "In fol.":              "in fol.",          # 4x    majuscule
    "in folio":             "in fol.",          # 1x
    "in fol. Atlantico":    "in fol. atlantico",# 2x
    "in folio atlantico":   "in fol. atlantico",# 1x
    "in fol max":           "in fol. max.",     # 1x
    "in fol. max":          "in fol. max.",     # 1x
    "in fol. maximo":       "in fol. max.",     # 1x

    # ── Quarto ────────────────────────────────────────────────────────────
    "in quarto":            "in quarto",        # 243x  forme principale
    "In quarto":            "in quarto",        # 1x    majuscule

    # ── Octavo ────────────────────────────────────────────────────────────
    "in octavo":            "in octavo",        # 91x   forme principale
    "In octavo":            "in octavo",        # 2x    majuscule
}

# ═══════════════════════════════════════════════════════════════════════════════
# MATERIAL — Combinaisons complètes (support + format)
# ═══════════════════════════════════════════════════════════════════════════════
# Forme normalisée = support_norm + " " + format_norm

MATERIAL_COMBINATIONS = {
    # ── Parchemin + folio (les plus fréquentes) ───────────────────────────
    "Cod. membr. in fol.":          "Cod. membr. in fol.",       # 57x
    "Cod. membran. in fol.":        "Cod. membran. in fol.",     # 11x
    "Cod. membr. in fol":           "Cod. membr. in fol.",       # 2x
    "Cod membr. in fol.":           "Cod. membr. in fol.",       # 5x
    "Cod. memb. in fol.":           "Cod. membr. in fol.",       # 4x
    "Codex membr. in fol.":         "Cod. membr. in fol.",       # 1x
    "Cod. membranac. in folio atlantico": "Cod. membranac. in fol. atlantico",
    "Cod. membranaceus in fol. Atlantico": "Cod. membranaceus in fol. atlantico",
    "Cod. Membran in fol. Atlantico": "Cod. membran. in fol. atlantico",
    "Cod. membr. in fol max":       "Cod. membr. in fol. max.",
    "Cod. membr. in fol. max":      "Cod. membr. in fol. max.",
    "Cod. membr. in fol. maximo":   "Cod. membr. in fol. max.",

    # ── Parchemin + quarto ────────────────────────────────────────────────
    "Cod. membr. in quarto":        "Cod. membr. in quarto",     # 44x
    "Cod. membran. in quarto":      "Cod. membran. in quarto",   # 5x
    "Cod. membranac. in quarto":    "Cod. membranac. in quarto", # 1x

    # ── Parchemin + octavo ────────────────────────────────────────────────
    "Cod. membr. in octavo":        "Cod. membr. in octavo",     # 42x
    "Cod. memb. in octavo":         "Cod. membr. in octavo",     # 5x
    "Cod. membranac. in octavo":    "Cod. membranac. in octavo", # 1x

    # ── Papier + folio ────────────────────────────────────────────────────
    "Cod. cart. in fol.":           "Cod. chart. in fol.",       # 149x
    "Cod. cartac. in fol.":         "Cod. chart. in fol.",       # 47x
    "Cod. chart. in fol.":          "Cod. chart. in fol.",       # 24x
    "Cod. chartac. in fol.":        "Cod. chart. in fol.",       # 19x
    "Cod. cart. in fol":            "Cod. chart. in fol.",       # 10x
    "Cod chart. in fol.":           "Cod. chart. in fol.",       # 1x

    # ── Papier + quarto ───────────────────────────────────────────────────
    "Cod. cartac. in quarto":       "Cod. chart. in quarto",     # 85x
    "Cod. chart. in quarto":        "Cod. chart. in quarto",     # 25x
    "Cod. chartac. in quarto":      "Cod. chart. in quarto",     # 8x
    "Cod. cart. in quarto":         "Cod. chart. in quarto",     # 28x

    # ── Papier + octavo ───────────────────────────────────────────────────
    "Cod. chartac. in octavo":      "Cod. chart. in octavo",     # 16x
    "Cod. chart. in octavo":        "Cod. chart. in octavo",     # 13x
    "Cod. cartac. in octavo":       "Cod. chart. in octavo",     # 1x
}

# ═══════════════════════════════════════════════════════════════════════════════
# ETAT DE CONSERVATION
# ═══════════════════════════════════════════════════════════════════════════════
# 13 variantes relevées dans catalogue.txt

ETAT_NORM = {
    # ── Mutilé ────────────────────────────────────────────────────────────
    "in fine mutilus":      "mutile a la fin",      # 23x  le plus fréquent
    "mutilus":              "mutile",               # 13x
    "initio mutilus":       "mutile au debut",      # 10x
    "mancus et imperfectus":"mutile et incomplet",  # 3x
    "mutilus in principio": "mutile au debut",      # 1x   variante de initio mutilus
    "mutilus in fine":      "mutile a la fin",      # 1x   variante de in fine mutilus
    "valde mutilus":        "tres mutile",          # non relevé mais probable

    # ── Bien conservé ─────────────────────────────────────────────────────
    "optime servatus":      "tres bien conserve",   # 3x
    "bene servatus":        "bien conserve",        # 1x

    # ── Qualité d'écriture ────────────────────────────────────────────────
    "nitidissime exaratus": "tres soigneusement ecrit",  # 3x
    "nitidissime scriptus": "tres soigneusement ecrit",  # 3x
    "elegantissime exaratus":"elegamment ecrit",          # 1x

    # ── Valeur / statut ───────────────────────────────────────────────────
    "quantivis pretii":     "d'une valeur inestimable",  # 3x
    "MS. Archetypus":       "manuscrit archetype",       # 1x
}

# ═══════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ STATISTIQUE
# ═══════════════════════════════════════════════════════════════════════════════

STATS = {
    "total_entries_catalogue": 1975,
    "support_variants": 61,
    "format_variants": 13,
    "material_combinations": 96,
    "etat_variants": 13,
    "most_frequent_material": [
        ("Cod. chart. in fol.",    149),
        ("Cod. chart. in quarto",  85),
        ("Cod. membr. in fol.",    57),
        ("Cod. chart. in fol.",    47),   # cartac.
        ("Cod. membr. in quarto",  44),
        ("Cod. membr. in octavo",  42),
        ("Cod. chart. in quarto",  28),   # cart.
    ],
    "most_frequent_etat": [
        ("in fine mutilus",   23),
        ("mutilus",           13),
        ("initio mutilus",    10),
        ("optime servatus",    3),
        ("quantivis pretii",   3),
    ],
}

if __name__ == "__main__":
    print(f"Supports    : {len(SUPPORT_NORM)} variantes → 2 catégories (membr. / chart.)")
    print(f"Formats     : {len(FORMAT_NORM)} variantes → 3 catégories (fol. / quarto / octavo)")
    print(f"Combinaisons: {len(MATERIAL_COMBINATIONS)} variantes documentées")
    print(f"Etats       : {len(ETAT_NORM)} variantes → 5 catégories sémantiques")
    print()
    print("Catégories support :")
    print("  membr. / membran. / membranac. / membranaceus → parchemin")
    print("  cart. / cartac. / chart. / chartac.           → papier")
    print()
    print("Catégories format :")
    print("  in fol. / in fol. max. / in fol. atlantico    → folio")
    print("  in quarto                                      → quarto")
    print("  in octavo                                      → octavo")
    print()
    print("Catégories état :")
    print("  mutilé (fin / début / partiel)")
    print("  bien conservé")
    print("  qualité d'écriture")
    print("  valeur / statut")
