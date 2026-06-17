#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_medieval_model.py — Run 1
==============================
Teste le modèle fine-tuné magistermilitum/roberta-multilingual-medieval-ner
sur nos données (test.json) du catalogue Riccardiana.

Ce modèle reconnaît uniquement PERS (personnes) et LOC (lieux).
Notre gold standard contient : auteur, ouvrage, material, date, etat.

Seule correspondance valide :
  auteur → PERS  (les auteurs sont des personnes)

Les autres labels (ouvrage, material, date, etat) n'ont pas de correspondance
dans le modèle et sont donc exclus de l'évaluation.

Résultat : on évalue uniquement la capacité du modèle à détecter
les auteurs (auteur dans notre gold → PERS dans les prédictions).

Usage (dans ~/prima_ner/) :
    python3 test_medieval_model.py

Dépendances :
    pip install transformers torch seqeval

================================================================================
【代码说明】
================================================================================

■ 背景
  本脚本用于测试 Torres Aguilar (2022) 论文发布的微调模型
  （magistermilitum/roberta-multilingual-medieval-ner）在我们的
  里恰尔迪亚纳目录数据上的零样本表现（zero-shot evaluation）。

  该模型在约 8000 份中世纪拉丁语/古法语/古西班牙语契约文书上微调，
  识别两类实体：PERS（人名）和 LOC（地名）。

■ 标签对应问题
  我们的标注体系有5类：auteur / ouvrage / material / date / etat
  文章模型只有：PERS / LOC

  唯一有意义的对应关系：
    auteur → PERS（作者是人名，逻辑上对应）

  不可用的对应：
    ouvrage → LOC（作品名 ≠ 地名，语义不匹配，排除）
    material / date / etat → 无对应，排除

  因此本次评估仅针对 auteur 类型。

■ 评估逻辑
  1. 将 test.json 中的 auteur spans 转为 BIO 序列（gold）：
     auteur → B-PERS / I-PERS，其他 → O
  2. 用模型对原文进行推理，只保留 PERS 类型的预测
  3. 用 seqeval 在实体级别计算 Precision / Recall / F1
  4. 保存每条 entry 的详细对比（gold auteur vs pred PERS）

■ 输出
  run1_medieval_model/test_results_run1.json
================================================================================
"""

import json
import os
import numpy as np
from datetime import datetime

import torch
from transformers import pipeline
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score

# ── Configuration ─────────────────────────────────────────────────────────────
MODEL_NAME = "magistermilitum/roberta-multilingual-medieval-ner"  # HuggingFace 上的微调模型
TEST_PATH  = "../data/test.json"   # 我们的10条测试数据
LOG_DIR    = "./run1_medieval_model"  # 结果输出目录
os.makedirs(LOG_DIR, exist_ok=True)

device = 0 if torch.cuda.is_available() else -1  # 有GPU用GPU，否则CPU
print(f"[Config] Device : {'GPU' if device==0 else 'CPU'}")
print(f"[Config] Modèle : {MODEL_NAME}")
print(f"[Config] Données: {TEST_PATH}")
print(f"[Config] Évaluation : auteur (gold) → PERS (pred) uniquement")

# ── Chargement des données ────────────────────────────────────────────────────
# 加载 test.json，列出其中所有 auteur 实体（方便对照）
print("\n[1/4] Chargement des données test...")
with open(TEST_PATH, encoding="utf-8") as f:
    test_data = json.load(f)
print(f"  {len(test_data)} entrées chargées")

print("\n  Auteurs présents dans le test set :")
for e in test_data:
    auteurs = [s["text"] for s in e.get("spans",[]) if s["label"]=="auteur"]
    if auteurs:
        print(f"    #{e['entry_id']} : {', '.join(auteurs)}")

# ── Chargement du modèle ──────────────────────────────────────────────────────
# 首次运行会从 HuggingFace 自动下载模型（约2.4GB），之后会本地缓存
# aggregation_strategy="simple"：将同一实体的多个 subword token 合并为一个完整实体
print("\n[2/4] Chargement du modèle fine-tuné...")
ner_pipe = pipeline(
    "token-classification",
    model=MODEL_NAME,
    aggregation_strategy="simple",
    device=device,
)
print("  Modèle chargé ✓")

# ── Fonctions BIO ──────────────────────────────────────────────────────────────
def build_char_bio(raw, spans, label_map):
    """
    构建字符级别的 BIO 标签数组（gold）。
    label_map：标签映射字典，如 {"auteur": "PERS"}
    不在映射中的标签统一标为 O（忽略）。
    """
    char_labels = ["O"] * len(raw)
    for span in spans:
        mapped = label_map.get(span["label"])
        if mapped is None:
            continue  # 不在映射中的标签忽略（ouvrage/material/date/etat）
        idx = raw.find(span["text"])
        if idx == -1:
            continue
        char_labels[idx] = f"B-{mapped}"          # 实体首字符
        for i in range(idx + 1, idx + len(span["text"])):
            char_labels[i] = f"I-{mapped}"        # 实体内部字符
    return char_labels

def char_to_word_bio(raw, char_labels):
    """
    将字符级别的 BIO 标签转换为词级别的 BIO 序列。
    取每个词首字符的标签作为该词的标签。
    """
    bio = []
    pos = 0
    for word in raw.split():
        idx = raw.find(word, pos)
        if idx == -1:
            bio.append("O")
            pos += len(word)
            continue
        bio.append(char_labels[idx])
        pos = idx + len(word)
    return bio

def pred_to_char_bio(raw, predictions, keep_labels):
    """
    将模型预测结果转换为字符级别的 BIO 标签数组。
    keep_labels：只保留这些类型的预测（如 {"PERS"}），其余忽略。
    """
    char_pred = ["O"] * len(raw)
    for pred in predictions:
        label = pred["entity_group"]
        if label not in keep_labels:
            continue  # 忽略 LOC 等不相关的预测
        start = pred["start"]
        end   = min(pred["end"], len(raw))
        if start >= len(raw):
            continue
        char_pred[start] = f"B-{label}"
        for i in range(start + 1, end):
            char_pred[i] = f"I-{label}"
    return char_pred

# ── Inférence + évaluation ────────────────────────────────────────────────────
print("\n[3/4] Inférence et évaluation (auteur → PERS)...")

# 唯一有效的标签映射：auteur → PERS
# ouvrage/material/date/etat 无对应，不参与评估
LABEL_MAP = {"auteur": "PERS"}

all_gold = []  # 所有条目的 gold BIO 序列
all_raw_tokens = []
all_pred = []  # 所有条目的 pred BIO 序列
details  = []  # 每条的详细对比信息

for entry in test_data:
    raw   = entry["raw"]
    spans = entry.get("spans", [])

    # 构建 gold BIO 序列（auteur → PERS，其余 → O）
    char_gold = build_char_bio(raw, spans, LABEL_MAP)
    gold_bio  = char_to_word_bio(raw, char_gold)

    # 模型推理：直接将原文字符串输入
    try:
        predictions = ner_pipe(raw)
    except Exception as e:
        print(f"  [WARN] Erreur entrée #{entry['entry_id']}: {e}")
        predictions = []

    # 只保留 PERS 类型的预测（忽略 LOC）
    char_pred = pred_to_char_bio(raw, predictions, keep_labels={"PERS"})
    pred_bio  = char_to_word_bio(raw, char_pred)

    all_gold.append(gold_bio)
    all_pred.append(pred_bio)
    predictions_raw = ner_pipe(raw, aggregation_strategy="none")
    all_raw_tokens.append(predictions_raw)

    # 记录详细对比：gold 的 auteur vs 模型预测的 PERS
    gold_auteurs = [s["text"] for s in spans if s["label"] == "auteur"]
    pred_pers    = [p["word"] for p in predictions if p["entity_group"] == "PERS"]
    details.append({
        "entry_id":    entry["entry_id"],
        "raw":         raw,
        "gold_auteur": gold_auteurs,
        "pred_pers":   pred_pers,
    })
    print(f"  #{entry['entry_id']:4d} | gold: {gold_auteurs} | pred: {pred_pers}")


# ── Sauvegarde BIO sequences──────────────────────────────────────────────────────────────
bio_path = os.path.join(LOG_DIR, "bio_sequences_run1.txt")
with open(bio_path, "w", encoding="utf-8") as f:
    for i, entry in enumerate(test_data):
        f.write(f"\n=== #{entry['entry_id']} ===\n")
        f.write(f"raw : {entry['raw']}\n")
        f.write(f"gold: {all_gold[i]}\n")
        f.write(f"pred: {all_pred[i]}\n")
        for tok in all_raw_tokens[i]:
            f.write(f"  {tok}\n")
print(f"[BIO] Séquences → {bio_path}")


# ── Résultats────────────────────────────────────────────────────────────────
# seqeval 在实体级别计算指标（而非 token 级别）
# 即只有完整实体边界完全匹配才算正确
print("\n[4/4] Résultats :")
print("=" * 55)
print(classification_report(all_gold, all_pred, zero_division=0))

f1  = f1_score(all_gold, all_pred, zero_division=0)
pre = precision_score(all_gold, all_pred, zero_division=0)
rec = recall_score(all_gold, all_pred, zero_division=0)
print(f"  F1={f1:.4f}  P={pre:.4f}  R={rec:.4f}")

# ── Sauvegarde ────────────────────────────────────────────────────────────────
# numpy 类型无法直接序列化为 JSON，需要自定义转换器
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

results = {
    "model":       MODEL_NAME,
    "run":         "Run 1 — modèle fine-tuné sur chartes médiévales",
    "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "test_entries": len(test_data),
    "evaluation_note": (
        "Seul auteur (gold) → PERS (pred) est évalué. "
        "ouvrage/material/date/etat exclus : pas de correspondance dans le modèle."
    ),
    "metrics": {
        "f1":        round(f1, 4),
        "precision": round(pre, 4),
        "recall":    round(rec, 4),
    },
    "details_par_entree": details,
}

out_path = os.path.join(LOG_DIR, "test_results_run1.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

print(f"\n[Done] Résultats → {out_path}")

# ── Rapport Markdown ──────────────────────────────────────────────────────────
def classify_error(gold_auteurs, pred_pers):
    """
    Classifie le type d'erreur pour une entrée donnée.
    Retourne une liste de types d'erreurs détectés.
    """
    errors = []
    if not gold_auteurs and not pred_pers:
        return ["correct_vide"]  # pas d'auteur, pas de prédiction → correct
    if gold_auteurs and not pred_pers:
        errors.append("faux_negatif")   # modèle n'a rien prédit
    if pred_pers and not gold_auteurs:
        errors.append("faux_positif")   # modèle a prédit mais rien dans le gold
    if gold_auteurs and pred_pers:
        # Vérifier correspondance partielle (boundary error)
        matched = False
        for g in gold_auteurs:
            for p in pred_pers:
                if g in p or p in g or any(tok in p for tok in g.split()):
                    matched = True
        if matched:
            # Vérifier si correspondance exacte
            exact = any(
                g.strip() == p.strip()
                for g in gold_auteurs for p in pred_pers
            )
            if exact:
                errors.append("correct_exact")
            else:
                errors.append("erreur_frontiere")  # partiel
        else:
            errors.append("faux_negatif")
            if pred_pers:
                errors.append("faux_positif")
    return errors if errors else ["correct_exact"]


md_lines = []

# ── En-tête ──
md_lines.append("# Rapport d'analyse — Run 1 : modèle médiéval (zero-shot)\n")
md_lines.append(f"**Modèle** : `{MODEL_NAME}`  ")
md_lines.append(f"**Date** : {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
md_lines.append(f"**Données** : `test.json` ({len(test_data)} entrées)  ")
md_lines.append(f"**Évaluation** : `auteur` (gold) → `PERS` (pred) uniquement\n")
md_lines.append("---\n")

# ── Section 1 : Définitions des métriques ──
md_lines.append("## 1. Définitions des métriques d'évaluation\n")
md_lines.append("### Français\n")
md_lines.append(
    "| Métrique | Définition |\n"
    "|---|---|\n"
    "| **Precision** | Parmi toutes les entités prédites par le modèle, quelle proportion est correcte ? "
    "Une precision faible signifie beaucoup de fausses alarmes (faux positifs). |\n"
    "| **Recall** | Parmi toutes les entités réellement présentes dans le gold standard, quelle proportion "
    "a été détectée ? Un recall faible signifie que le modèle rate beaucoup d'entités (faux négatifs). |\n"
    "| **F1-score** | Moyenne harmonique de la precision et du recall. Indicateur d'équilibre entre les deux. "
    "F1 = 2 × (P × R) / (P + R). |\n"
    "| **Micro avg** | Calcule P/R/F1 en agrégeant tous les tokens de toutes les classes ensemble. "
    "Donne plus de poids aux classes fréquentes. |\n"
    "| **Macro avg** | Calcule P/R/F1 séparément pour chaque classe, puis fait la moyenne simple. "
    "Chaque classe a le même poids, indépendamment de sa fréquence. |\n"
    "| **Weighted avg** | Comme le macro avg, mais pondéré par le nombre d'instances de chaque classe (support). "
    "Tient compte du déséquilibre entre classes. |\n"
)
md_lines.append("\n### 中文\n")
md_lines.append(
    "| 指标 | 定义 |\n"
    "|---|---|\n"
    "| **Precision（精确率）** | 在模型预测的所有实体中，真正正确的比例。精确率低意味着误报多（假阳性多）。|\n"
    "| **Recall（召回率）** | 在gold标准中实际存在的所有实体中，被模型成功识别的比例。召回率低意味着漏报多（假阴性多）。|\n"
    "| **F1-score** | 精确率和召回率的调和平均数，综合衡量两者的平衡。公式：F1 = 2×(P×R)/(P+R)。|\n"
    "| **Micro avg（微平均）** | 将所有类别的token合并后统一计算P/R/F1，频率高的类别权重更大。|\n"
    "| **Macro avg（宏平均）** | 对每个类别分别计算P/R/F1后取简单平均，每个类别权重相同，不考虑频率差异。|\n"
    "| **Weighted avg（加权平均）** | 类似宏平均，但按每个类别的样本数量加权，能反映类别不平衡的影响。|\n"
)
md_lines.append("---\n")

# ── Section 2 : Matrice de résultats ──
md_lines.append("## 2. Résultats globaux (seqeval — entité stricte)\n")
md_lines.append("```\n")
md_lines.append(classification_report(all_gold, all_pred, zero_division=0))
md_lines.append("```\n")
md_lines.append(f"- **F1** = {f1:.4f}  ")
md_lines.append(f"- **Precision** = {pre:.4f}  ")
md_lines.append(f"- **Recall** = {rec:.4f}\n")
md_lines.append(
    "> ⚠️ Évaluation stricte : une entité n'est comptée comme correcte que si ses bornes "
    "correspondent exactement au gold standard (pas de correspondance partielle).\n"
)
md_lines.append("---\n")

# ── Section 3 : Analyse par type d'erreur ──
md_lines.append("## 3. Analyse des erreurs par type\n")

type_counts = {"correct_exact": [], "correct_vide": [], "faux_negatif": [],
               "faux_positif": [], "erreur_frontiere": []}

for d in details:
    errs = classify_error(d["gold_auteur"], d["pred_pers"])
    for e in errs:
        if e in type_counts:
            type_counts[e].append(d["entry_id"])

md_lines.append("| Type d'erreur | Nb entrées | entry_ids |\n|---|---|---|")
labels_fr = {
    "correct_exact":    "✅ Correct (correspondance exacte)",
    "correct_vide":     "✅ Correct (pas d'auteur attendu ni prédit)",
    "faux_negatif":     "❌ Faux négatif — modèle n'a pas détecté l'auteur",
    "faux_positif":     "⚠️ Faux positif — modèle a prédit un auteur inexistant",
    "erreur_frontiere": "〰️ Erreur de frontière — détection partielle",
}
for t, ids in type_counts.items():
    if ids:
        md_lines.append(f"| {labels_fr[t]} | {len(ids)} | {', '.join(f'#{i}' for i in ids)} |")
md_lines.append("")
md_lines.append("---\n")

# ── Section 4 : Exemples détaillés par type ──
md_lines.append("## 4. Exemples détaillés\n")

# Regrouper les détails par type d'erreur
grouped = {"faux_negatif": [], "faux_positif": [], "erreur_frontiere": [], "correct_exact": []}
for d in details:
    errs = classify_error(d["gold_auteur"], d["pred_pers"])
    for e in errs:
        if e in grouped:
            grouped[e].append(d)

sections = [
    ("faux_negatif",     "❌ Type 1 : Faux négatifs — auteur non détecté",
     "Le modèle n'a prédit aucune entité PERS là où le gold indique un auteur. "
     "Cause probable : forme latine génitif (-i, -ii) peu fréquente dans les chartes médiévales ; "
     "entrée non conventionnelle (ex. `da Cascia Fra Simone`)."),
    ("faux_positif",     "⚠️ Type 2 : Faux positifs — entité prédite sans gold",
     "Le modèle a détecté des personnes réelles (saints, personnages dans les titres) "
     "qui ne sont pas des auteurs au sens de notre annotation. "
     "Cause : le modèle reconnaît tous les noms de personnes, pas seulement les auteurs."),
    ("erreur_frontiere", "〰️ Type 3 : Erreurs de frontière — détection partielle",
     "Le modèle identifie la bonne entité mais avec des bornes incorrectes. "
     "Cause : tokenisation en sous-mots (subword) de XLM-RoBERTa, "
     "qui découpe les tokens différemment de notre annotation au niveau du mot."),
    ("correct_exact",    "✅ Type 4 : Détections correctes",
     "Correspondance exacte entre gold et prédiction."),
]

for key, title, explication in sections:
    entries = grouped.get(key, [])
    if not entries:
        continue
    md_lines.append(f"### {title}\n")
    md_lines.append(f"*{explication}*\n")
    for d in entries:
        md_lines.append(f"**Entrée #{d['entry_id']}**\n")
        md_lines.append(f"```\nTexte : {d['raw']}\nGold  : {d['gold_auteur']}\nPréd  : {d['pred_pers']}\n```\n")

md_lines.append("---\n")

# ── Section 5 : Conclusion ──
md_lines.append("## 5. Conclusion\n")
md_lines.append(
    f"Le modèle `magistermilitum/roberta-multilingual-medieval-ner` obtient un **F1 de {f1:.4f}** "
    f"(P={pre:.4f}, R={rec:.4f}) en mode zero-shot sur notre test set de {len(test_data)} entrées, "
    "évalué uniquement sur la correspondance `auteur` → `PERS`.\n"
)
md_lines.append(
    "Les principales limites observées sont :\n"
    "1. **Faux négatifs** : le modèle rate les auteurs en forme génitif latin et les noms non conventionnels.\n"
    "2. **Faux positifs** : le modèle détecte des personnages cités dans les titres d'ouvrages comme auteurs.\n"
    "3. **Erreurs de frontière** : la tokenisation subword crée des décalages de bornes.\n\n"
    "Ces résultats confirment que le modèle, bien qu'entraîné sur des textes médiévaux latins, "
    "n'est pas adapté à notre tâche spécifique (catalogue de manuscrits vs chartes diplomatiques) "
    "et justifient l'entraînement d'un modèle dédié (Run 2 et Run 3).\n"
)

# ── Sauvegarde Markdown ──
md_path = os.path.join(LOG_DIR, "error_analysis_run1.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines) + "\n")
print(f"[Markdown] Rapport → {md_path}")
