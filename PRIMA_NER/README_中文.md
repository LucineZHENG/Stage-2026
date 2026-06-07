# Stage-2026

PRIMA 项目（ERC Grant 101142242）实习代码仓库，聚焦于中世纪拉丁语手稿目录的命名实体识别（NER）与实体链接（EL）。

实习单位：LIFAT 实验室，图尔大学  
指导老师：Carlos-Emiliano González-Gallardo  
实习时间：2026 年 4 月 — 11 月

---

## 目录结构

```
Stage-2026/
├── pipeline_gold/        # 100 条 gold 标准完整流水线
├── pipeline_remaining/   # 838 条 remaining 条目流水线
└── monitor_apps/         # Flask 监控与专家验证界面
```

---

## 一、100 条 Gold 标准流水线

数据来源：Biblioteca Riccardiana 目录（条目 221–1700 中的 100 条抽样）

### 步骤说明

| 步骤 | 脚本 | 输入 | 输出 |
|------|------|------|------|
| Step 1 自动 NER + EL | `prima_pipeline.py` | 4 个 Riccardiana JSON + `catalogue.txt` + `catalogue_dict.json` | `webanno_preannotation.tsv` / `annotation_guide.tsv` / `el_report.json` |
| Step 2 INCEpTION 人工校对 | —（手动操作） | `sample_for_inception.txt` | `admin.json` |
| Step 3 合并标注与元数据 | `merge_annotations.py` | `admin.json` + `el_report.json` | `gold_annotations.json` |
| Step 4 EL 搜索（监控界面） | `monitor_apps/prima_monitor.py` | INCEpTION 实时标注 | `el_auteur_ouvrage.jsonl` |
| Step 5 合并 EL 结果 | `merge_el.py` | `gold_annotations.json` + `el_auteur_ouvrage.jsonl` | `gold_annotations_with_el.json` |
| Step 6 专家验证 | `monitor_apps/prima_monitor_expert.py` | `gold_annotations_with_el.json` | `el_validated.jsonl / .json / .csv` |

> **关于 gold_annotations.json**：`el_report.json` 含 pipeline 自动标注 + 元数据（法译、日期对比等），`admin.json` 含人工校对后的准确标注。合并逻辑为：用人工标注覆盖自动标注，保留元数据。两者结合即为 NLP 意义上的"黄金标准"数据集。

### 辅助脚本

- `MAPPING_date.py`：日期字段格式映射
- `MAPPING_mfe.py`：中古法语字段映射

---

## 二、838 条 Remaining 流水线

数据来源：Biblioteca Riccardiana 目录中除 gold 100 条外的剩余条目

### 步骤说明

| 步骤 | 脚本 | 输入 | 输出 |
|------|------|------|------|
| Étape 1 准备数据 | `prepare_remaining.py` | 原始目录 | `remaining_for_inception.txt` / `remaining_guide.tsv` / `remaining_entries.json` |
| Étape 2 INCEpTION 标注 + 实时 EL | `prima_monitor_remaining.py` | INCEpTION API（轮询） | `el_auteur_ouvrage_remaining.jsonl` |
| Étape 3 合并 NER 标注与元数据 | `merge_annotations_remaining.py` | `admin.json` + `remaining_entries.json` | `gold_annotations_remaining.json` |
| Étape 4 合并 EL 结果 | `merge_el_remaining.py` | `gold_annotations_remaining.json` + `el_auteur_ouvrage_remaining.jsonl` | `gold_annotations_remaining_el.json` |
| Étape 5 专家验证 | `prima_monitor_expert_remaining.py` | `gold_annotations_remaining_el.json` | `el_validated_remaining.jsonl / .json / .csv` |

---

## 三、监控与验证界面

| 脚本 | 功能 | 默认端口 |
|------|------|------|
| `prima_monitor.py` | 实时监听 INCEpTION，对 auteur/ouvrage 自动触发 VIAF/Wikidata 搜索（gold 100 条） | 5051 |
| `prima_monitor_remaining.py` | 实时监听 INCEpTION，对 auteur/ouvrage 自动触发 VIAF/Wikidata 搜索（838 条） | 5051 |
| `prima_monitor_expert.py` | 专家逐条确认 VIAF/Wikidata 候选（gold 100 条），结果保存为三种格式 | 5052 |
| `prima_monitor_expert_remaining.py` | 专家逐条确认 VIAF/Wikidata 候选（838 条），结果保存为三种格式 | 5053 |

> `prima_monitor.py` 与 `prima_monitor_remaining.py` 端口相同（5051），两者不会同时运行。

---

## 数据文件说明

所有 `.json` / `.jsonl` / `.csv` 数据文件**不上传至本仓库**，在本地 `output_EL/`、`output_inception/`、`output_remaining/` 目录中管理。
