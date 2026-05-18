#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prima_xlmroberta.py
===================
Fine-tuning XLM-RoBERTa pour la NER sur les entrées du catalogue Riccardiana.

Labels : auteur, ouvrage, material, date, etat  (schéma BIO)
Données : train.json / val.json / test.json  (gold_annotations_with_el.json)

Sorties dans ./logs/ et ./model_xlmroberta/ :
  - logs/training_log.jsonl     → loss + F1 + temps par epoch
  - logs/eval_results.json      → métriques finales sur val
  - logs/test_results.json      → métriques finales sur test
  - model_xlmroberta/           → modèle fine-tuné (sauvegardé)

Usage (dans ~/prima_ner/xlm_roberta/) :
    python3 prima_xlmroberta.py

Dépendances :
    pip install transformers datasets seqeval torch

================================================================================
【代码逻辑与结构说明】
================================================================================

本脚本针对 PRIMA 项目（ERC 101142242）对里恰尔迪亚纳图书馆中世纪手稿目录
进行命名实体识别（NER）的微调训练。

■ 任务目标
  识别拉丁语/意大利语目录条目中的5类实体：
    - auteur   : 作者名（拉丁属格或意大利语形式）
    - ouvrage  : 作品名
    - material : 载体描述（如 Cod. membr. in fol.）
    - date     : 手稿年代（如 Saec. XIV）
    - etat     : 保存状态描述

■ 数据
  - 来源：gold_annotations_with_el.json（100条人工标注）
  - 划分：train(70) / val(20) / test(10)，seed=42，随机划分
  - 标注格式：每条 entry 含 raw 文本 + spans（含 text、label 字段）

■ 模型
  XLM-RoBERTa-base（多语言预训练模型，支持拉丁语/法语/意大利语）
  + TokenClassification head（BIO标签分类层）

■ 代码结构（按执行顺序）
  1. json_to_bio()     : 将 JSON 标注转换为 BIO 序列
                         - 按字符位置构建 char_labels 数组
                         - 按空格切词，取每个词首字符的标签
  2. NERDataset        : PyTorch Dataset
                         - 使用 tokenizer 将词列表转为 subword token
                         - 对齐 BIO 标签（subword → word_ids 映射）
                         - padding 到 MAX_LEN=128，-100 掩盖非实体位置
  3. evaluate()        : 使用 seqeval 计算实体级别的 P/R/F1
                         - 按类型单独报告（auteur/ouvrage/material/date/etat）
                         - 同时计算 macro 平均
  4. 数据加载          : 读取 train/val/test.json，转 BIO，构建 DataLoader
  5. 模型初始化        : 加载 xlm-roberta-base，替换分类头（NUM_LABELS=11）
  6. 优化器            : AdamW，lr=2e-5，线性 warmup（前10%步骤）
  7. 训练循环          : 每个 epoch：
                         - 前向传播 + 计算 cross-entropy loss
                         - 梯度裁剪（max_norm=1.0）
                         - 在 val 上评估 F1
                         - 保存最佳模型（按 val F1）
                         - 记录 epoch 日志（loss/F1/时间戳）到 JSONL 文件
  8. 测试评估          : 加载最佳模型，在 test set 上计算最终指标
                         - 输出 test_results.json（含按类型的详细报告）

■ 超参数
  EPOCHS=20, BATCH_SIZE=8, LR=2e-5, MAX_LEN=128, SEED=42

■ 输出文件
  logs/training_log.jsonl   → 每个 epoch 的 loss、val F1、时间戳
  logs/test_results.json    → 最终测试结果（含按类型 P/R/F1）
  model_xlmroberta/         → 最佳模型权重（可用于推理或继续训练）
================================================================================
"""

import json
import os
import time
from datetime import datetime
from collections import defaultdict

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    get_linear_schedule_with_warmup,
)
from torch.optim import AdamW
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score

# ── Configuration ─────────────────────────────────────────────────────────────
MODEL_NAME   = "xlm-roberta-base"   # 多语言预训练模型（支持100+语言含拉丁语）
DATA_DIR     = "../data"            # train/val/test.json 所在目录
LOG_DIR      = "./logs"             # 训练日志输出目录
MODEL_DIR    = "./model_xlmroberta" # 最佳模型保存目录

EPOCHS       = 20       # 训练轮数（小数据集可适当多训练）
BATCH_SIZE   = 8        # 批大小（GPU 显存不足时可降为 4）
LR           = 2e-5     # 学习率（Transformer fine-tuning 标准值）
MAX_LEN      = 128      # 最大 token 长度（目录条目一般不超过此长度）
SEED         = 42       # 随机种子（与数据划分保持一致）

# BIO 标签体系：O + 每类实体的 B-/I- 标签
# O=0, B-auteur=1, I-auteur=2, B-ouvrage=3, I-ouvrage=4, ...
LABELS = ["auteur", "ouvrage", "material", "date", "etat"]
LABEL2ID = {"O": 0}
for lab in LABELS:
    LABEL2ID[f"B-{lab}"] = len(LABEL2ID)
    LABEL2ID[f"I-{lab}"] = len(LABEL2ID)
ID2LABEL = {v: k for k, v in LABEL2ID.items()}
NUM_LABELS = len(LABEL2ID)  # = 11

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

torch.manual_seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[Config] Device: {device}")
print(f"[Config] Model : {MODEL_NAME}")
print(f"[Config] Epochs: {EPOCHS}, LR: {LR}, Batch: {BATCH_SIZE}")


# ── 1. Conversion JSON → BIO ──────────────────────────────────────────────────
def json_to_bio(entries):
    """
    将 JSON 标注转换为 BIO 序列。
    输入：entries 列表，每条含 raw（原文）和 spans（标注片段列表）
    输出：[(tokens, labels), ...] 列表
      - tokens : 按空格切分的词列表
      - labels : 对应的 BIO 标签列表（如 B-auteur, I-auteur, O）
    """
    samples = []
    for entry in entries:
        raw = entry["raw"]
        spans = entry.get("spans", [])

        # 步骤1：按字符构建标签数组，初始全为 "O"
        # 每个字符位置对应一个标签，span 首字符标 B-，其余字符标 I-
        char_labels = ["O"] * len(raw)
        for span in spans:
            text  = span["text"]
            label = span["label"]
            idx   = raw.find(text)
            if idx == -1:
                continue  # 找不到则跳过（理论上不会发生）
            char_labels[idx] = f"B-{label}"           # 实体首字符
            for i in range(idx + 1, idx + len(text)):
                char_labels[i] = f"I-{label}"         # 实体内部字符

        # 步骤2：按空格切词，取每个词首字符的标签作为该词的标签
        # 这是"词级别"的 BIO 标注，与 subword tokenizer 的对齐在 NERDataset 中处理
        tokens = []
        labels = []
        pos = 0
        for word in raw.split():
            idx = raw.find(word, pos)
            if idx == -1:
                tokens.append(word)
                labels.append("O")
                pos += len(word)
                continue
            tok_label = char_labels[idx]  # 取词首字符的标签
            tokens.append(word)
            labels.append(tok_label)
            pos = idx + len(word)

        samples.append((tokens, labels))
    return samples


# ── 2. Dataset ────────────────────────────────────────────────────────────────
class NERDataset(Dataset):
    """
    PyTorch Dataset，将词级别的 BIO 序列转换为模型输入。

    核心问题：XLM-RoBERTa 使用 SentencePiece 切分 subword，
    一个词可能被切成多个 token（如 "Augustini" → "Aug", "ust", "ini"）。
    需要将词级别的 BIO 标签对齐到 subword 级别：
      - 词的第一个 subword 保留原标签
      - 后续 subword：若原标签是 B-X 则改为 I-X，否则保持不变
      - 特殊 token（[CLS], [SEP], [PAD]）标为 -100（loss 计算时忽略）
    """
    def __init__(self, samples, tokenizer, max_len):
        self.samples   = samples
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        tokens, labels = self.samples[idx]

        # subword tokenization，is_split_into_words=True 告知 tokenizer 输入已切词
        encoding = self.tokenizer(
            tokens,
            is_split_into_words=True,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        # word_ids()：每个 subword token 对应原来第几个词（None 表示特殊 token）
        word_ids    = encoding.word_ids()
        label_ids   = []
        prev_word   = None
        for wid in word_ids:
            if wid is None:
                label_ids.append(-100)          # 特殊 token，loss 中忽略
            elif wid != prev_word:
                label_ids.append(LABEL2ID[labels[wid]])   # 词的第一个 subword
            else:
                # 同一个词的后续 subword：B- 改为 I-，其余不变
                l = labels[wid]
                if l.startswith("B-"):
                    l = "I-" + l[2:]
                label_ids.append(LABEL2ID.get(l, 0))
            prev_word = wid

        return {
            "input_ids":      encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels":         torch.tensor(label_ids, dtype=torch.long),
        }


# ── 3. Évaluation seqeval ────────────────────────────────────────────────────
def evaluate(model, loader, split_name="val"):
    """
    使用 seqeval 在实体级别（而非 token 级别）计算 P/R/F1。
    seqeval 会将连续的 B-X I-X 序列识别为一个完整实体再比较，
    比 token 级别的准确率更符合 NER 任务的实际需求。

    输出：
      - 终端打印每个类型的 precision/recall/F1
      - 返回 dict：{f1, precision, recall, report（按类型详细）}
    """
    model.eval()
    all_preds = []
    all_trues = []
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attn_mask = batch["attention_mask"].to(device)
            lab       = batch["labels"].to(device)
            outputs   = model(input_ids=input_ids, attention_mask=attn_mask)
            logits    = outputs.logits
            preds     = torch.argmax(logits, dim=-1)   # 取概率最高的标签

            for pred_seq, true_seq in zip(preds.cpu().tolist(), lab.cpu().tolist()):
                p_tags = []
                t_tags = []
                for p, t in zip(pred_seq, true_seq):
                    if t == -100:
                        continue   # 跳过特殊 token
                    p_tags.append(ID2LABEL[p])
                    t_tags.append(ID2LABEL[t])
                all_preds.append(p_tags)
                all_trues.append(t_tags)

    report = classification_report(all_trues, all_preds, output_dict=True, zero_division=0)
    f1  = f1_score(all_trues, all_preds, zero_division=0)
    pre = precision_score(all_trues, all_preds, zero_division=0)
    rec = recall_score(all_trues, all_preds, zero_division=0)
    print(f"  [{split_name}] F1={f1:.4f}  P={pre:.4f}  R={rec:.4f}")
    print(classification_report(all_trues, all_preds, zero_division=0))
    return {"f1": f1, "precision": pre, "recall": rec, "report": report}


# ── 4. Chargement des données ─────────────────────────────────────────────────
print("\n[1/5] Chargement des données...")
for split in ["train", "val", "test"]:
    path = os.path.join(DATA_DIR, f"{split}.json")
    with open(path, encoding="utf-8") as f:
        globals()[f"{split}_entries"] = json.load(f)
    print(f"  {split}: {len(globals()[f'{split}_entries'])} entrées")

train_samples = json_to_bio(train_entries)
val_samples   = json_to_bio(val_entries)
test_samples  = json_to_bio(test_entries)
print(f"  BIO → train:{len(train_samples)}, val:{len(val_samples)}, test:{len(test_samples)}")


# ── 5. Tokenizer & Dataset ────────────────────────────────────────────────────
print("\n[2/5] Chargement du tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

train_dataset = NERDataset(train_samples, tokenizer, MAX_LEN)
val_dataset   = NERDataset(val_samples,   tokenizer, MAX_LEN)
test_dataset  = NERDataset(test_samples,  tokenizer, MAX_LEN)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE)
test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE)


# ── 6. Modèle ─────────────────────────────────────────────────────────────────
print("\n[3/5] Chargement du modèle...")
# 加载 xlm-roberta-base 并替换分类头：
# 原始模型输出 768 维向量，分类头将其映射到 NUM_LABELS=11 个标签
# （O + 5类×2 = 11：O, B-auteur, I-auteur, B-ouvrage, ... B-etat, I-etat）
model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_LABELS,
    id2label=ID2LABEL,
    label2id=LABEL2ID,
)
model.to(device)

# AdamW：Adam + weight decay，适合 Transformer fine-tuning
optimizer = AdamW(model.parameters(), lr=LR)
total_steps = len(train_loader) * EPOCHS
# 线性 warmup：前10%的步骤学习率从0线性增加到LR，之后线性衰减到0
# 避免训练初期大学习率破坏预训练权重
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=int(0.1 * total_steps),
    num_training_steps=total_steps,
)


# ── 7. Entraînement ───────────────────────────────────────────────────────────
print(f"\n[4/5] Entraînement ({EPOCHS} epochs)...")
log_path = os.path.join(LOG_DIR, "training_log.jsonl")
best_f1  = 0.0
training_start = time.time()

with open(log_path, "w", encoding="utf-8") as logf:
    for epoch in range(1, EPOCHS + 1):
        epoch_start = time.time()
        model.train()
        total_loss = 0.0

        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attn_mask = batch["attention_mask"].to(device)
            labels    = batch["labels"].to(device)

            # 前向传播：模型自动计算 cross-entropy loss（-100 位置被忽略）
            outputs = model(input_ids=input_ids, attention_mask=attn_mask, labels=labels)
            loss    = outputs.loss
            total_loss += loss.item()

            # 反向传播
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)  # 梯度裁剪防止梯度爆炸
            optimizer.step()
            scheduler.step()   # 线性 warmup + 衰减学习率
            optimizer.zero_grad()

        avg_loss   = total_loss / len(train_loader)
        epoch_time = time.time() - epoch_start
        timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\nEpoch {epoch}/{EPOCHS}  loss={avg_loss:.4f}  time={epoch_time:.1f}s  [{timestamp}]")
        val_metrics = evaluate(model, val_loader, "val")

        # 保存 val F1 最高的模型（而非最后一个 epoch）
        if val_metrics["f1"] > best_f1:
            best_f1 = val_metrics["f1"]
            model.save_pretrained(MODEL_DIR)
            tokenizer.save_pretrained(MODEL_DIR)
            print(f"  ✓ Meilleur modèle sauvegardé (F1={best_f1:.4f})")

        # 每个 epoch 写一行 JSON 日志（含时间戳，便于追踪训练进度）
        log_entry = {
            "epoch":         epoch,
            "timestamp":     timestamp,          # 该 epoch 结束的时刻
            "duration_s":    round(epoch_time, 2),
            "train_loss":    round(avg_loss, 6),
            "val_f1":        round(val_metrics["f1"], 6),
            "val_precision": round(val_metrics["precision"], 6),
            "val_recall":    round(val_metrics["recall"], 6),
        }
        logf.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        logf.flush()   # 实时写入，不等训练结束

total_time = time.time() - training_start
print(f"\nEntraînement terminé en {total_time/60:.1f} min | Meilleur val F1 = {best_f1:.4f}")


# ── 8. Évaluation finale sur test ────────────────────────────────────────────
print("\n[5/5] Évaluation sur le test set...")
# Recharger le meilleur modèle
model = AutoModelForTokenClassification.from_pretrained(MODEL_DIR)
model.to(device)
test_metrics = evaluate(model, test_loader, "test")

# Sauvegarder les résultats
results = {
    "model":       MODEL_NAME,
    "epochs":      EPOCHS,
    "lr":          LR,
    "batch_size":  BATCH_SIZE,
    "seed":        SEED,
    "best_val_f1": round(best_f1, 6),
    "test_metrics": {
        "f1":        round(test_metrics["f1"], 6),
        "precision": round(test_metrics["precision"], 6),
        "recall":    round(test_metrics["recall"], 6),
    },
    "test_report_by_label": test_metrics["report"],
    "total_training_time_min": round(total_time / 60, 2),
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

with open(os.path.join(LOG_DIR, "test_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n[Done] Test F1={test_metrics['f1']:.4f}")
print(f"       Résultats → {LOG_DIR}/test_results.json")
print(f"       Modèle    → {MODEL_DIR}/")
