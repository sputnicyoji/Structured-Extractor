# structured-extractor

```
  ____  _                   _                      _
 / ___|| |_ _ __ _   _  ___| |_ _   _ _ __ ___  __| |
 \___ \| __| '__| | | |/ __| __| | | | '__/ _ \/ _` |
  ___) | |_| |  | |_| | (__| |_| |_| | | |  __/ (_| |
 |____/ \__|_|   \__,_|\___|\__|\__,_|_|  \___|\__,_|
  _____      _                  _
 | ____|_  _| |_ _ __ __ _  ___| |_ ___  _ __
 |  _| \ \/ / __| '__/ _` |/ __| __/ _ \| '__|
 | |___ >  <| |_| | | (_| | (__| || (_) | |
 |_____/_/\_\\__|_|  \__,_|\___|\__\___/|_|
```

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-purple)

**A Claude Code Skill for structured information extraction from code, documents, and logs.**

Zero external dependencies. No API keys. Just Claude + Python stdlib.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Pipeline](#pipeline)
- [File Structure](#file-structure)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Performance](#performance)
- [License](#license)
- [Chinese / 简体中文](#简体中文)
- [Japanese / 日本語](#日本語)

---

## Overview

**structured-extractor** replaces [LangExtract](https://github.com/example/langextract) by leveraging Claude Code's built-in AI for extraction, paired with a 6-step Python post-processing pipeline.

The key insight: LangExtract was 90% prompt engineering and 10% difflib-based algorithms. This skill eliminates the external API dependency entirely -- Claude Code already provides the AI, so all we need is a solid post-processing pipeline.

### Key Features

- **6 extraction types**: rule, event, state, constraint, entity, relation
- **3 preset configurations**: code-logic, doc-structure, log-analysis
- **6-step pipeline**: Source Grounding, Overlap Dedup, Confidence Scoring, Entity Resolution, Relation Inference, KG Injection
- **Zero external dependencies**: Python standard library only
- **No API keys needed**: Uses Claude Code's built-in AI capabilities
- **Fast**: 1000 extractions against a 500-line source file in under 1 second

---

## Architecture

```
+----------------+          +------------------+          +--------------------+
|                |  JSON    |                  |  JSON    |                    |
|   Claude AI    +--------->+  Python Pipeline +--------->+  Structured Output |
|  (extraction)  |          | (post-processing)|          |                    |
+----------------+          +------------------+          +--------------------+

Claude Code Skill (SKILL.md)     scripts/pipeline.py        Final JSON / KG format
  - Prompt templates               - 6 processing steps
  - Few-shot examples              - All stdlib, no deps
  - Type definitions               - O(n^2) or better
```

---

## Pipeline

The post-processing pipeline transforms raw Claude extractions into high-quality, deduplicated, confidence-scored structured data.

```
  Raw Extractions (from Claude)
         |
         v
  +------+---------+
  | Source Grounding|   Step 1: 3-level text alignment
  | exact/norm/fuzz |   (exact match -> normalized -> difflib fuzzy)
  +------+---------+
         |
         v
  +------+---------+
  | Overlap Dedup  |   Step 2: Remove overlapping extractions
  | >50% threshold |   (interval overlap ratio > 0.5)
  +------+---------+
         |
         v
  +------+---------+
  | Confidence     |   Step 3: 4-dimension weighted scoring
  | Scoring        |   match(35%) + completeness(25%)
  |                |   + specificity(20%) + consistency(20%)
  +------+---------+
         |
         v
  +------+---------+
  | Entity         |   Step 4 (optional): Greedy clustering
  | Resolution     |   with difflib similarity threshold
  +------+---------+
         |
         v
  +------+---------+
  | Relation       |   Step 5 (optional): Rule-based
  | Inference      |   co-occurrence relation inference
  +------+---------+
         |
         v
  +------+---------+
  | KG Injection   |   Step 6 (optional): Convert to
  |                |   knowledge graph format
  +------+---------+
         |
         v
  Structured Output (JSON)
```

### Pipeline Steps in Detail

| Step | Module | Description |
|------|--------|-------------|
| 1. Source Grounding | `source_grounding.py` | 3-level text alignment: exact string match, normalized match (whitespace/case), fuzzy match via `difflib.SequenceMatcher`. Anchors each extraction to a specific source location. |
| 2. Overlap Dedup | `overlap_dedup.py` | Removes duplicate extractions where character intervals overlap by more than 50%. Keeps the higher-confidence extraction. |
| 3. Confidence Scoring | `confidence_scorer.py` | 4-dimension weighted score: `match_quality` (35%) + `attr_completeness` (25%) + `text_specificity` (20%) + `type_consistency` (20%). |
| 4. Entity Resolution | `entity_resolver.py` | Optional. Greedy clustering algorithm using `difflib` similarity to merge references to the same logical entity. |
| 5. Relation Inference | `relation_inferrer.py` | Optional. Rule-based inference of relations between entities based on co-occurrence patterns in source text. |
| 6. KG Injection | `kg_injector.py` | Optional. Converts structured extractions into knowledge graph format (entities + relations + observations). |

---

## File Structure

```
structured-extractor/
|
+-- SKILL.md                        # Claude Code skill definition
|
+-- assets/presets/                  # Preset configurations
|   +-- code-logic.json             #   C# / Python / JS code analysis
|   +-- doc-structure.json          #   Document structure extraction
|   +-- log-analysis.json           #   Log file analysis
|
+-- references/                     # Detailed reference documentation
|   +-- extraction-types.md         #   6 extraction type definitions
|   +-- few-shot-templates.md       #   Few-shot prompt examples
|   +-- output-schema.md            #   JSON Schema for output format
|   +-- post-processing.md          #   Pipeline algorithm details
|
+-- scripts/                        # Python pipeline
|   +-- pipeline.py                 #   Main pipeline (CLI entry point)
|   +-- source_grounding.py         #   Text alignment to source
|   +-- overlap_dedup.py            #   Overlap deduplication
|   +-- confidence_scorer.py        #   4-dimension confidence scoring
|   +-- entity_resolver.py          #   Entity disambiguation
|   +-- relation_inferrer.py        #   Relation inference
|   +-- kg_injector.py              #   Knowledge graph format conversion
|   +-- test_data/                  #   Test fixtures
|
+-- test/                           # Integration test data
```

---

## Quick Start

### Install as a Claude Code Skill

```bash
# Clone the repository
git clone https://github.com/sputnicyoji/structured-extractor.git

# Copy into your project's Claude Code skills directory
cp -r structured-extractor/ your-project/.claude/skills/structured-extractor/
```

That is it. Claude Code will automatically detect the skill via `SKILL.md` and make it available in your project.

### Verify Installation

In Claude Code, you can invoke the skill directly:

```
/structured-extractor
```

Or Claude Code will automatically trigger it when you ask for structured extraction tasks.

---

## Usage

### Basic Extraction (CLI)

```bash
# Minimal: input JSON + source file
python scripts/pipeline.py \
  --input raw.json \
  --source code.cs \
  --output result.json
```

### With Preset Configuration

```bash
# Use a preset for C#/Python/JS code analysis
python scripts/pipeline.py \
  --input raw.json \
  --source code.cs \
  --config assets/presets/code-logic.json \
  --output result.json
```

### Full Pipeline (All Optional Steps Enabled)

```bash
python scripts/pipeline.py \
  --input raw.json \
  --source code.cs \
  --enable-entity-resolution \
  --enable-relation-inference \
  --enable-kg-injection \
  --output result.json
```

### Extraction Types

| Type | Description | Example |
|------|-------------|---------|
| `rule` | Business rules, validation logic, constraints | "Max retry count is 3" |
| `event` | Events, triggers, callbacks, hooks | "OnPlayerDeath triggers respawn" |
| `state` | State machines, status transitions, flags | "Order: pending -> confirmed -> shipped" |
| `constraint` | Hard constraints, invariants, preconditions | "HP must be non-negative" |
| `entity` | Named entities, classes, modules, actors | "PlayerController manages input" |
| `relation` | Relationships between entities | "HeroSystem depends on BattleSystem" |

### Preset Configurations

| Preset | Target | Focus |
|--------|--------|-------|
| `code-logic.json` | C# / Python / JS source files | Control flow, state machines, business rules |
| `doc-structure.json` | Markdown / text documents | Sections, definitions, cross-references |
| `log-analysis.json` | Application log files | Error patterns, event sequences, anomalies |

---

## Performance

| Metric | Value |
|--------|-------|
| 1000 extractions + 500-line source | < 1 second |
| Algorithm complexity | O(n^2) or better |
| Memory per extraction | ~1 KB |
| External dependencies | None (Python stdlib only) |
| Minimum Python version | 3.10+ |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

---

# 简体中文

## 概述

**structured-extractor** 是一个 Claude Code Skill，用于从代码、文档和日志中提取结构化信息。

它替代了 LangExtract -- LangExtract 本质上是 90% 的 Prompt 工程加 10% 的 difflib 算法。本工具利用 Claude Code 内置的 AI 能力完成提取，配合纯 Python 标准库实现的 6 步后处理管道，无需任何外部依赖或 API 密钥。

## 核心特性

- **6 种提取类型**: rule (规则), event (事件), state (状态), constraint (约束), entity (实体), relation (关系)
- **3 种预设配置**: 代码逻辑分析、文档结构提取、日志分析
- **6 步处理管道**: 源码定位 -> 重叠去重 -> 置信度评分 -> 实体消歧 -> 关系推断 -> 知识图谱注入
- **零外部依赖**: 仅使用 Python 标准库
- **无需 API 密钥**: 直接使用 Claude Code 内置 AI

## 安装

```bash
# 克隆仓库
git clone https://github.com/sputnicyoji/structured-extractor.git

# 复制到项目的 Claude Code skills 目录
cp -r structured-extractor/ your-project/.claude/skills/structured-extractor/
```

## 使用方法

```bash
# 基本用法
python scripts/pipeline.py --input raw.json --source code.cs --output result.json

# 使用预设配置
python scripts/pipeline.py --input raw.json --source code.cs \
  --config assets/presets/code-logic.json --output result.json

# 完整管道
python scripts/pipeline.py --input raw.json --source code.cs \
  --enable-entity-resolution --enable-relation-inference \
  --enable-kg-injection --output result.json
```

## 管道流程

```
Claude AI 提取 -> JSON -> Python 管道 (6 步后处理) -> 结构化输出

步骤 1: 源码定位    - 3 级文本对齐 (精确/归一化/模糊匹配)
步骤 2: 重叠去重    - 移除重叠率 > 50% 的重复提取
步骤 3: 置信度评分  - 4 维加权: 匹配质量(35%) + 属性完整度(25%)
                      + 文本特异性(20%) + 类型一致性(20%)
步骤 4: 实体消歧    - (可选) 基于 difflib 的贪心聚类
步骤 5: 关系推断    - (可选) 基于共现的规则推断
步骤 6: 知识图谱注入 - (可选) 转换为知识图谱格式
```

## 性能

- 1000 条提取 + 500 行源码: < 1 秒
- 算法复杂度: O(n^2) 或更优
- 每条提取内存占用: ~1 KB

---

---

# 日本語

## 概要

**structured-extractor** は、コード・ドキュメント・ログから構造化情報を抽出する Claude Code Skill です。

LangExtract の代替として開発されました。LangExtract の実態は 90% がプロンプトエンジニアリング、10% が difflib アルゴリズムでした。本ツールは Claude Code 内蔵の AI で抽出を行い、Python 標準ライブラリのみで実装された 6 段階の後処理パイプラインと組み合わせます。外部依存や API キーは不要です。

## 主な特徴

- **6 種類の抽出タイプ**: rule (ルール), event (イベント), state (状態), constraint (制約), entity (エンティティ), relation (関係)
- **3 種類のプリセット設定**: コードロジック分析、ドキュメント構造抽出、ログ分析
- **6 段階パイプライン**: ソース位置特定 -> 重複排除 -> 信頼度スコアリング -> エンティティ解決 -> 関係推論 -> ナレッジグラフ注入
- **外部依存ゼロ**: Python 標準ライブラリのみ使用
- **API キー不要**: Claude Code 内蔵の AI をそのまま利用

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/sputnicyoji/structured-extractor.git

# プロジェクトの Claude Code skills ディレクトリにコピー
cp -r structured-extractor/ your-project/.claude/skills/structured-extractor/
```

## 使用方法

```bash
# 基本的な使用方法
python scripts/pipeline.py --input raw.json --source code.cs --output result.json

# プリセット設定を使用
python scripts/pipeline.py --input raw.json --source code.cs \
  --config assets/presets/code-logic.json --output result.json

# 全パイプラインを有効化
python scripts/pipeline.py --input raw.json --source code.cs \
  --enable-entity-resolution --enable-relation-inference \
  --enable-kg-injection --output result.json
```

## パイプライン

```
Claude AI 抽出 -> JSON -> Python パイプライン (6段階後処理) -> 構造化出力

Step 1: ソース位置特定   - 3段階テキストアライメント (完全/正規化/あいまい一致)
Step 2: 重複排除         - 重複率 > 50% の抽出を除去
Step 3: 信頼度スコアリング - 4次元加重: 一致品質(35%) + 属性完全性(25%)
                           + テキスト特異性(20%) + 型一貫性(20%)
Step 4: エンティティ解決  - (任意) difflib ベースの貪欲クラスタリング
Step 5: 関係推論         - (任意) 共起ベースのルール推論
Step 6: KG 注入          - (任意) ナレッジグラフ形式への変換
```

## パフォーマンス

- 1000 件の抽出 + 500 行のソース: 1 秒未満
- アルゴリズム計算量: O(n^2) 以下
- 抽出 1 件あたりのメモリ: 約 1 KB
