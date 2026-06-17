#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prima_bilstm_crf.py
===================
Baseline BiLSTM-CRF pour la NER sur les entrées du catalogue Riccardiana.

Labels : auteur, ouvrage, material, date, etat  (schéma BIO)
Données : train.json / val.json / test.json

Sorties dans ./logs/ et ./model_bilstm/ :
  - logs/training_log.jsonl   → loss + F1 + temps par epoch
  - logs/test_results.json    → métriques finales sur test
  - model_bilstm/model.pt     → meilleurs poids du modèle

Usage (dans ~/prima_ner/bilstm_crf/) :
    python3 prima_bilstm_crf.py

Dépendances :
    pip install torch seqeval --use-pep517

================================================================================
【代码逻辑与结构说明】
================================================================================

■ 任务目标
  与 XLM-RoBERTa 相同的 NER 任务，作为 baseline 对比系统。
  BiLSTM-CRF 是经典的序列标注模型，不依赖预训练语言模型。

■ 模型架构
  词嵌入层（Embedding）
    → 双向 LSTM（BiLSTM）：同时从左到右和从右到左读取序列，
      捕捉每个词的上下文信息，输出维度 = 2 × hidden_dim
    → 线性层：将 BiLSTM 输出映射到标签空间（NUM_LABELS 维）
    → CRF 层：对标签序列建模，学习标签之间的转移概率
              （如 I-auteur 不能跟在 B-ouvrage 后面）
              使用 Viterbi 算法解码最优标签序列

■ 特征
  - 词级别（word-level）：每个词对应一个 embedding 向量
  - 词表从训练集构建，OOV（未登录词）用 <UNK> 处理
  - 无预训练词向量（从零开始训练），这是与 XLM-RoBERTa 的主要区别

■ 数据处理
  - 同 XLM-RoBERTa：JSON → BIO 转换（字符级对齐）
  - padding 到批次最大长度（动态 padding，不固定 MAX_LEN）

■ 代码结构（按执行顺序）
  1. json_to_bio()      : JSON 标注 → BIO 词序列（同 XLM-RoBERTa）
  2. 构建词表/标签表    : 从训练集统计所有词，构建 word2id/id2word
  3. NERDataset         : 将词序列转为 id 序列，pad 到批次最长
  4. BiLSTM_CRF 类      : 模型定义（Embedding + BiLSTM + Linear + CRF）
  5. CRF 实现           : neg_log_likelihood（训练loss）+ viterbi_decode（推理）
  6. evaluate()         : seqeval 实体级别 P/R/F1
  7. 训练循环           : 每 epoch 记录 loss/F1/时间戳，保存最佳模型
  8. 测试评估           : 加载最佳模型，在 test set 上计算最终指标

■ 超参数
  EPOCHS=50, BATCH_SIZE=8, LR=0.001, EMBED_DIM=64, HIDDEN_DIM=128, SEED=42
  （BiLSTM 收敛慢于 Transformer，需要更多 epoch）

■ 与 XLM-RoBERTa 的主要区别
  - 无预训练：从零开始学习词表示，需要更多数据才能达到同等效果
  - 速度快：模型小，训练快（无需 GPU 也可运行）
  - 泛化弱：对未见词（OOV）处理能力差
  - 这正是 baseline 的意义：展示预训练模型带来的提升幅度
================================================================================
"""

import json
import os
import time
import random
import re
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
import numpy as np

# ── Configuration ─────────────────────────────────────────────────────────────
DATA_DIR   = "../data"
LOG_DIR    = "./logs"
MODEL_DIR  = "./model_bilstm"

EPOCHS     = 50       # BiLSTM 收敛慢，需要更多 epoch
BATCH_SIZE = 8
LR         = 0.001    # Adam 默认学习率
EMBED_DIM  = 64       # 词嵌入维度
HIDDEN_DIM = 128      # BiLSTM 隐藏层维度（单向），双向输出为 256
DROPOUT    = 0.3      # Dropout 防止过拟合
SEED       = 42

# BIO 标签体系（与 XLM-RoBERTa 完全一致，便于对比）
LABELS = ["auteur", "ouvrage", "material", "date", "etat"]
LABEL2ID = {"O": 0, "PAD": -1}
for lab in LABELS:
    LABEL2ID[f"B-{lab}"] = len(LABEL2ID) - 1
    LABEL2ID[f"I-{lab}"] = len(LABEL2ID) - 1
# 重建干净的标签映射（去掉 PAD）
LABEL2ID = {"O": 0}
for lab in LABELS:
    LABEL2ID[f"B-{lab}"] = len(LABEL2ID)
    LABEL2ID[f"I-{lab}"] = len(LABEL2ID)
ID2LABEL = {v: k for k, v in LABEL2ID.items()}
NUM_LABELS = len(LABEL2ID)

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

random.seed(SEED)
torch.manual_seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[Config] Device    : {device}")
print(f"[Config] Epochs    : {EPOCHS}, LR: {LR}, Batch: {BATCH_SIZE}")
print(f"[Config] Embed_dim : {EMBED_DIM}, Hidden_dim: {HIDDEN_DIM}")


# ── 1. Conversion JSON → BIO ──────────────────────────────────────────────────
def json_to_bio(entries):
    """
    JSON 标注 → BIO 词序列（与 XLM-RoBERTa 脚本完全一致）
    按字符位置构建 char_labels，然后按空格切词取词首字符标签。
    """
    samples = []
    for entry in entries:
        raw   = entry["raw"]
        spans = entry.get("spans", [])

        char_labels = ["O"] * len(raw)
        for span in spans:
            text  = span["text"]
            label = span["label"]
            idx   = raw.find(text)
            if idx == -1:
                continue
            char_labels[idx] = f"B-{label}"
            for i in range(idx + 1, idx + len(text)):
                char_labels[i] = f"I-{label}"

        tokens = []
        labels = []
        pos = 0
        for word in raw.split():
            idx = raw.find(word, pos)
            if idx == -1:
                tokens.append(word); labels.append("O")
                pos += len(word); continue
            tokens.append(word)
            labels.append(char_labels[idx])
            pos = idx + len(word)

        samples.append((tokens, labels))
    return samples


# ── 2. Construire le vocabulaire ──────────────────────────────────────────────
def build_vocab(train_samples):
    """
    从训练集构建词表。
    特殊符号：<PAD>（填充）, <UNK>（未知词/OOV）
    """
    word2id = {"<PAD>": 0, "<UNK>": 1}
    for tokens, _ in train_samples:
        for w in tokens:
            if w not in word2id:
                word2id[w] = len(word2id)
    return word2id


# ── 3. Dataset ────────────────────────────────────────────────────────────────
class NERDataset(Dataset):
    """
    将词序列转为 id 序列。
    未知词（测试集中未在训练集出现的词）映射到 <UNK>。
    """
    def __init__(self, samples, word2id):
        self.data    = samples
        self.word2id = word2id

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        tokens, labels = self.data[idx]
        token_ids = [self.word2id.get(w, self.word2id["<UNK>"]) for w in tokens]
        label_ids = [LABEL2ID[l] for l in labels]
        return torch.tensor(token_ids, dtype=torch.long), \
               torch.tensor(label_ids, dtype=torch.long)


def collate_fn(batch):
    """
    动态 padding：将一个 batch 内的序列 pad 到该 batch 最大长度。
    比固定 MAX_LEN 更高效。
    """
    token_seqs, label_seqs = zip(*batch)
    token_padded = pad_sequence(token_seqs, batch_first=True, padding_value=0)
    label_padded = pad_sequence(label_seqs, batch_first=True, padding_value=-1)
    mask = (token_padded != 0)   # True = 真实 token，False = PAD
    return token_padded, label_padded, mask


# ── 4. Modèle BiLSTM-CRF ────────────────────────────────────────────────────
class BiLSTM_CRF(nn.Module):
    """
    BiLSTM-CRF 序列标注模型。

    架构：
      Embedding → Dropout → BiLSTM → Dropout → Linear → CRF

    CRF 层维护一个 (NUM_LABELS × NUM_LABELS) 的转移矩阵，
    学习标签之间的合法转移（如禁止 I-auteur 跟在 B-date 后面）。
    """
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_labels, dropout):
        super().__init__()
        self.num_labels = num_labels

        # 词嵌入层
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.dropout   = nn.Dropout(dropout)

        # 双向 LSTM：输出维度 = 2 × hidden_dim
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True,
                            bidirectional=True, num_layers=1)

        # 将 BiLSTM 输出映射到标签空间（发射分数）
        self.hidden2tag = nn.Linear(hidden_dim * 2, num_labels)

        # CRF 转移矩阵：transitions[i][j] = 从标签 j 转移到标签 i 的分数
        self.transitions = nn.Parameter(torch.randn(num_labels, num_labels))
        # 初始化：禁止转移到 O 标签的中间位置（软约束）
        nn.init.uniform_(self.transitions, -0.1, 0.1)

    def get_emissions(self, x):
        """计算发射分数（BiLSTM 输出）"""
        emb  = self.dropout(self.embedding(x))
        out, _ = self.lstm(emb)
        out  = self.dropout(out)
        return self.hidden2tag(out)   # (batch, seq_len, num_labels)

    def crf_forward(self, emissions, mask):
        """
        CRF 前向算法：计算所有可能路径的归一化因子 log Z。
        用于训练时计算 negative log-likelihood。
        """
        batch_size, seq_len, _ = emissions.shape
        # 初始化：第一个时间步的分数
        score = emissions[:, 0, :]   # (batch, num_labels)
        for t in range(1, seq_len):
            # broadcast：当前分数 + 转移分数 + 发射分数
            score_t = score.unsqueeze(2) + self.transitions.unsqueeze(0) \
                      + emissions[:, t, :].unsqueeze(1)
            score_t = torch.logsumexp(score_t, dim=1)
            # mask：PAD 位置不更新分数
            mask_t  = mask[:, t].unsqueeze(1).float()
            score   = score_t * mask_t + score * (1 - mask_t)
        return torch.logsumexp(score, dim=1)   # (batch,)

    def score_sequence(self, emissions, tags, mask):
        """
        计算给定标签序列的路径分数（发射分数 + 转移分数之和）。
        """
        batch_size, seq_len, _ = emissions.shape
        score = torch.zeros(batch_size, device=emissions.device)
        for t in range(seq_len):
            mask_t = mask[:, t].float()
            emit   = emissions[:, t, :].gather(1, tags[:, t].unsqueeze(1)).squeeze(1)
            if t > 0:
                trans = self.transitions[tags[:, t], tags[:, t-1]]
                score = score + (emit + trans) * mask_t
            else:
                score = score + emit * mask_t
        return score

    def neg_log_likelihood(self, x, tags, mask):
        """
        训练损失：负对数似然 = log Z - score(正确路径)
        """
        emissions = self.get_emissions(x)
        # 将 PAD 位置的标签（-1）替换为 0，避免索引越界
        tags_safe = tags.clone()
        tags_safe[tags_safe < 0] = 0
        forward   = self.crf_forward(emissions, mask)
        gold      = self.score_sequence(emissions, tags_safe, mask)
        return (forward - gold).mean()

    def viterbi_decode(self, x, mask):
        """
        Viterbi 算法：找到最优标签序列（推理阶段）。
        """
        emissions  = self.get_emissions(x)
        batch_size, seq_len, _ = emissions.shape

        viterbi  = emissions[:, 0, :]
        backptr  = []

        for t in range(1, seq_len):
            v_t   = viterbi.unsqueeze(2) + self.transitions.unsqueeze(0)
            best_scores, best_tags = v_t.max(dim=1)
            backptr.append(best_tags)
            mask_t  = mask[:, t].unsqueeze(1).float()
            viterbi = (best_scores + emissions[:, t, :]) * mask_t \
                      + viterbi * (1 - mask_t)

        # 回溯
        best_last = viterbi.argmax(dim=1)
        best_path = [best_last]
        for bp in reversed(backptr):
            best_last = bp.gather(1, best_last.unsqueeze(1)).squeeze(1)
            best_path.append(best_last)
        best_path.reverse()
        best_path = torch.stack(best_path, dim=1)   # (batch, seq_len)
        return best_path


# ── 5. Évaluation ─────────────────────────────────────────────────────────────
def evaluate(model, loader, split_name="val"):
    """seqeval 实体级别评估，与 XLM-RoBERTa 脚本完全一致。"""
    model.eval()
    all_preds = []
    all_trues = []
    with torch.no_grad():
        for token_ids, label_ids, mask in loader:
            token_ids = token_ids.to(device)
            mask      = mask.to(device)
            preds     = model.viterbi_decode(token_ids, mask)

            for pred_seq, true_seq, m in zip(
                    preds.cpu().tolist(), label_ids.tolist(), mask.cpu().tolist()):
                p_tags = [ID2LABEL[p] for p, valid in zip(pred_seq, m) if valid]
                t_tags = [ID2LABEL[t] for t, valid in zip(true_seq, m) if valid]
                all_preds.append(p_tags)
                all_trues.append(t_tags)

    f1  = f1_score(all_trues, all_preds, zero_division=0)
    pre = precision_score(all_trues, all_preds, zero_division=0)
    rec = recall_score(all_trues, all_preds, zero_division=0)
    report = classification_report(all_trues, all_preds, output_dict=True, zero_division=0)
    print(f"  [{split_name}] F1={f1:.4f}  P={pre:.4f}  R={rec:.4f}")
    print(classification_report(all_trues, all_preds, zero_division=0))
    return {"f1": f1, "precision": pre, "recall": rec, "report": report}


# ── 6. Chargement des données ─────────────────────────────────────────────────
print("\n[1/5] Chargement des données...")
splits = {}
for split in ["train", "val", "test"]:
    with open(os.path.join(DATA_DIR, f"{split}.json"), encoding="utf-8") as f:
        splits[split] = json.load(f)
    print(f"  {split}: {len(splits[split])} entrées")

train_samples = json_to_bio(splits["train"])
val_samples   = json_to_bio(splits["val"])
test_samples  = json_to_bio(splits["test"])

# ── 7. Vocabulaire ────────────────────────────────────────────────────────────
print("\n[2/5] Construction du vocabulaire...")
word2id = build_vocab(train_samples)
print(f"  Vocab size: {len(word2id)} mots")

train_dataset = NERDataset(train_samples, word2id)
val_dataset   = NERDataset(val_samples,   word2id)
test_dataset  = NERDataset(test_samples,  word2id)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                          shuffle=True,  collate_fn=collate_fn)
val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE, collate_fn=collate_fn)
test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE, collate_fn=collate_fn)

# ── 8. Modèle ─────────────────────────────────────────────────────────────────
print("\n[3/5] Initialisation du modèle BiLSTM-CRF...")
model = BiLSTM_CRF(
    vocab_size  = len(word2id),
    embed_dim   = EMBED_DIM,
    hidden_dim  = HIDDEN_DIM,
    num_labels  = NUM_LABELS,
    dropout     = DROPOUT,
).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=LR)
total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"  Paramètres entraînables: {total_params:,}")

# ── 9. Entraînement ───────────────────────────────────────────────────────────
print(f"\n[4/5] Entraînement ({EPOCHS} epochs)...")
log_path = os.path.join(LOG_DIR, "training_log.jsonl")
best_f1  = 0.0
training_start = time.time()

with open(log_path, "w", encoding="utf-8") as logf:
    for epoch in range(1, EPOCHS + 1):
        epoch_start = time.time()
        model.train()
        total_loss = 0.0

        for token_ids, label_ids, mask in train_loader:
            token_ids = token_ids.to(device)
            label_ids = label_ids.to(device)
            mask      = mask.to(device)

            # CRF 的 loss：负对数似然
            loss = model.neg_log_likelihood(token_ids, label_ids, mask)
            total_loss += loss.item()

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

        avg_loss   = total_loss / len(train_loader)
        epoch_time = time.time() - epoch_start
        timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\nEpoch {epoch}/{EPOCHS}  loss={avg_loss:.4f}  "
              f"time={epoch_time:.1f}s  [{timestamp}]")
        val_metrics = evaluate(model, val_loader, "val")

        # 保存最佳模型
        if val_metrics["f1"] > best_f1:
            best_f1 = val_metrics["f1"]
            torch.save(model.state_dict(),
                       os.path.join(MODEL_DIR, "model.pt"))
            # 保存词表（推理时需要）
            with open(os.path.join(MODEL_DIR, "word2id.json"), "w") as f:
                json.dump(word2id, f, ensure_ascii=False)
            print(f"  ✓ Meilleur modèle sauvegardé (F1={best_f1:.4f})")

        log_entry = {
            "epoch":         epoch,
            "timestamp":     timestamp,
            "duration_s":    round(epoch_time, 2),
            "train_loss":    round(avg_loss, 6),
            "val_f1":        round(val_metrics["f1"], 6),
            "val_precision": round(val_metrics["precision"], 6),
            "val_recall":    round(val_metrics["recall"], 6),
        }
        logf.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        logf.flush()

total_time = time.time() - training_start
print(f"\nEntraînement terminé en {total_time/60:.1f} min | "
      f"Meilleur val F1 = {best_f1:.4f}")

# ── 10. Évaluation finale sur test ───────────────────────────────────────────
print("\n[5/5] Évaluation sur le test set...")
model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "model.pt"),
                                  map_location=device))
test_metrics = evaluate(model, test_loader, "test")

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

results = {
    "model":      "BiLSTM-CRF",
    "epochs":     EPOCHS,
    "lr":         LR,
    "embed_dim":  EMBED_DIM,
    "hidden_dim": HIDDEN_DIM,
    "batch_size": BATCH_SIZE,
    "seed":       SEED,
    "vocab_size": len(word2id),
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
    json.dump(results, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

print(f"\n[Done] Test F1={test_metrics['f1']:.4f}")
print(f"       Résultats → {LOG_DIR}/test_results.json")
print(f"       Modèle    → {MODEL_DIR}/model.pt")
