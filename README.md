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
![Cursor Rules](https://img.shields.io/badge/Cursor-Rules-orange)

**A Claude Code Skill / Cursor Rule for structured information extraction from code, documents, and logs.** Built on [Google LangExtract](https://github.com/google/langextract)'s Source Grounding algorithms -- enhanced and extended.

Zero external dependencies. No API keys. Just your AI assistant + Python stdlib.

---

## Table of Contents

- [Overview](#overview)
- [Why structured-extractor?](#why-structured-extractor)
- [Architecture](#architecture)
- [Pipeline](#pipeline)
- [File Structure](#file-structure)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Performance](#performance)
- [License](#license)
- [Cursor IDE](#cursor-ide)
- [Chinese / 简体中文](#简体中文)
- [Japanese / 日本語](#日本語)

---

## Overview

**structured-extractor** reimplements [Google LangExtract](https://github.com/google/langextract)'s post-processing core as a standalone pipeline, eliminating the external LLM dependency by leveraging the host AI assistant's built-in capabilities.

### Origin: What we learned from LangExtract

[LangExtract](https://github.com/google/langextract) is Google's Gemini-powered library for structured information extraction. After studying its internals, we identified two distinct layers:

- **The AI layer** (~90%): Prompt engineering, few-shot examples, and schema enforcement that drive extraction quality. This is what Gemini (or any capable LLM) provides.
- **The algorithm layer** (~10%): Source Grounding via `difflib.SequenceMatcher`, character-offset deduplication, and result aggregation. This is pure Python -- model-agnostic and portable.

The key insight: **if you are already working inside an AI-powered coding assistant (Claude Code, Cursor, etc.), the AI layer is already present.** You don't need a second LLM call to Gemini. What you *do* need is the algorithmic post-processing layer -- extracted, enhanced, and made standalone.

That is exactly what structured-extractor does: it takes LangExtract's Source Grounding and dedup algorithms, **improves them** (best-win dedup instead of first-win, 3-level matching, 4-dimension confidence scoring), and **extends them** with Entity Resolution, Relation Inference, and Knowledge Graph injection -- capabilities LangExtract does not offer.

### Key Features

- **6 extraction types**: rule, event, state, constraint, entity, relation
- **3 preset configurations**: code-logic, doc-structure, log-analysis
- **5-step pipeline + 3 output formats**: Source Grounding, Overlap Dedup, Confidence Scoring, Entity Resolution, Relation Inference -- then output as JSON, Markdown, or Knowledge Graph
- **Zero external dependencies**: Python standard library only
- **No API keys needed**: Uses Claude Code's built-in AI capabilities
- **Fast**: 1000 extractions against a 500-line source file in under 1 second

---

## Why structured-extractor?

Code knowledge exists at three distinct layers. Most tools only reach the first two:

```
  Layer 3 (Semantic)    "Shutdown must be deferred during iteration to prevent collection modification"
      ^                  structured-extractor extracts THIS layer
      |
  Layer 2 (Location)    "m_IsDelayShutdown appears at line 42, 87, 153"
      ^                  Grep / code search finds this
      |
  Layer 1 (Structure)   "GameSolver has field m_IsDelayShutdown (bool) and method Shutdown()"
                         AST / Repomap / tree-sitter gives you this
```

### What AST / Repomap sees

AST-based tools parse syntax trees. They excel at answering **what** and **where**:

```
GameSolver
+-- field: m_IsDelayShutdown (bool)
+-- field: m_IsUpdating (bool)
+-- method: Shutdown() -> void
+-- method: OnUpdate() -> void
|   +-- calls: WaitForCompletion()
|   +-- calls: RunAllSystems()
+-- inherits: ISolver
```

This is the **skeleton** -- class members, call graphs, inheritance. Extremely useful for navigation. But it cannot tell you *why* `m_IsDelayShutdown` exists or what breaks if you remove it.

### What Grep / Code Search sees

```bash
grep "m_IsDelayShutdown" -> 3 hits (declaration, set true, check)
grep "WaitForCompletion" -> 2 hits (in Shutdown, in OnUpdate)
```

These are **fragments** -- where a symbol appears. You must mentally reconstruct the full picture.

### What structured-extractor sees

```json
{
  "type": "constraint",
  "text": "if (m_IsUpdating) { m_IsDelayShutdown = true; return; }",
  "summary": "Deferred shutdown: cannot execute during system iteration",
  "attributes": {
    "reason": "Prevents collection modification during foreach traversal",
    "type": "concurrency_safety",
    "consequence": "Removing this causes InvalidOperationException at runtime"
  }
}
```

It extracts **semantic knowledge** -- not what the code looks like, but what it *means* and *why it must be this way*.

### Three categories of knowledge AST cannot capture

#### 1. Implicit ordering constraints

```csharp
InitPhysics();
InitRendering();
InitAudio();
RegisterCallbacks();
```

AST sees: four sequential method calls.
**But it cannot distinguish "happens to be in this order" from "MUST be in this order or the system crashes."**
structured-extractor labels this as a `rule` with `order: mandatory` and `consequence: changing order breaks dependency chain`.

#### 2. Distributed compound rules

Pause logic scattered across three locations in a game engine:

```csharp
// Location 1 (line 40): stage guard
if (currentStage != Stage.Running) return;

// Location 2 (line 55): input cleanup
pendingInputX = 0f;

// Location 3 (line 72): time freeze
TimeManager.SetGroupScale(groupId, 0f);
```

AST sees three independent statements. Grep finds each location separately. Only structured-extractor **associates** them as a compound rule: "Pause requires all three steps -- skipping any one causes bugs."

#### 3. The "why" behind defensive code

```csharp
lastUpdateTime = Time.current;  // inside Resume()
```

| Tool | Sees | Misses |
|------|------|--------|
| AST | Assignment, type `float` | Why is this needed? |
| Grep | `lastUpdateTime` at line 88 | Relationship to pause duration |
| **structured-extractor** | "Prevents frame spike after pause: without reset, first frame deltaTime equals total pause duration, causing teleportation" | -- |

### Summary

| Capability | AST / Repomap | Grep / Search | structured-extractor |
|------------|:---:|:---:|:---:|
| Class hierarchy & members | Yes | -- | -- |
| Symbol location | -- | Yes | Yes |
| **Business rules** | -- | -- | **Yes** |
| **Ordering constraints** | -- | -- | **Yes** |
| **Causal reasoning (why)** | -- | -- | **Yes** |
| **Cross-location rule aggregation** | -- | -- | **Yes** |
| **Consequence of violation** | -- | -- | **Yes** |

> **AST tells you the skeleton of the code. structured-extractor tells you its soul.**

The ideal developer knowledge system covers all three layers: Repomap for structural navigation, Grep for precise location, structured-extractor for semantic understanding. They are complementary, not competing.

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
  Structured Output (JSON)
         |
         v
  +------+---------+
  | Output Format  |   Choose one or more:
  | Selection      |   - JSON file (.json)
  |                |   - Markdown report (.md)
  |                |   - Knowledge Graph (if available)
  +------+---------+
```

### Pipeline Steps in Detail

| Step | Module | Description |
|------|--------|-------------|
| 1. Source Grounding | `source_grounding.py` | 3-level text alignment: exact string match, normalized match (whitespace/case), fuzzy match via `difflib.SequenceMatcher`. Anchors each extraction to a specific source location. |
| 2. Overlap Dedup | `overlap_dedup.py` | Removes duplicate extractions where character intervals overlap by more than 50%. Keeps the higher-confidence extraction. |
| 3. Confidence Scoring | `confidence_scorer.py` | 4-dimension weighted score: `match_quality` (35%) + `attr_completeness` (25%) + `text_specificity` (20%) + `type_consistency` (20%). |
| 4. Entity Resolution | `entity_resolver.py` | Optional. Greedy clustering algorithm using `difflib` similarity to merge references to the same logical entity. |
| 5. Relation Inference | `relation_inferrer.py` | Optional. Rule-based inference of relations between entities based on co-occurrence patterns in source text. |

After the pipeline completes, you choose one or more **output formats**:

| Format | Description |
|--------|-------------|
| **JSON file** | Save pipeline output as `.json` -- always available, machine-readable |
| **Markdown report** | Generate a human-readable `.md` file grouped by extraction type |
| **Knowledge Graph** | Inject into KG via `aim_create_entities` / MCP tools (requires KG tooling) |

---

## File Structure

```
structured-extractor/
|
+-- SKILL.md                        # Claude Code skill definition
|
+-- cursor/                         # Cursor IDE rules
|   +-- structured-extractor.mdc   #   Cursor-compatible .mdc rules file
|
+-- install.ps1                     # Cursor installer (Windows PowerShell)
+-- install.sh                      # Cursor installer (macOS / Linux)
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

### Install as a Cursor IDE Rule (Standalone)

Cursor users can install the **complete skill** without Claude Code. The install script clones the full repo and sets up Cursor's `.mdc` rule automatically.

```bash
# 1. Clone into the standard skill location
cd your-project
git clone https://github.com/sputnicyoji/Structured-Extractor .cursor/skills/structured-extractor

# 2. Run the installer (copies .mdc to .cursor/rules/)
# Windows PowerShell:
.cursor/skills/structured-extractor/install.ps1

# macOS / Linux:
bash .cursor/skills/structured-extractor/install.sh
```

**Or as a git submodule** (recommended for version-controlled projects):

```bash
git submodule add https://github.com/sputnicyoji/Structured-Extractor .cursor/skills/structured-extractor
bash .cursor/skills/structured-extractor/install.sh
```

After installation, the directory structure is:

```
your-project/
+-- .cursor/
    +-- rules/
    |   +-- structured-extractor.mdc   <-- Cursor loads this
    +-- skills/
        +-- structured-extractor/      <-- Full skill (references + scripts + presets)
```

The `.mdc` rule references files from `.cursor/skills/structured-extractor/`, so the AI can read few-shot templates, run the Python pipeline, and access all reference documentation -- **no Claude Code required**.

---

## Cursor IDE

### How It Works

Cursor uses `.mdc` (Markdown Cursor) files in `.cursor/rules/` as project-level AI rules. The `structured-extractor.mdc` file teaches Cursor's AI assistant the same structured extraction methodology as the Claude Code skill.

**Key difference from the old approach**: The `.mdc` file is no longer a standalone copy -- it references the full skill directory at `.cursor/skills/structured-extractor/`. This means Cursor gets access to:
- `references/` -- extraction types, few-shot templates, output schema, algorithm docs
- `scripts/` -- the Python post-processing pipeline
- `assets/presets/` -- preset configurations for different file types

### Installation Methods

| Method | Command | Best For |
|--------|---------|----------|
| **Git clone** | `git clone ... .cursor/skills/structured-extractor` | Quick setup |
| **Git submodule** | `git submodule add ... .cursor/skills/structured-extractor` | Team projects |
| **Manual copy** | Copy entire repo to `.cursor/skills/structured-extractor/` | Offline use |

After cloning, run the install script to copy `.mdc` to `.cursor/rules/`:

```bash
# Windows
.cursor/skills/structured-extractor/install.ps1

# macOS / Linux
bash .cursor/skills/structured-extractor/install.sh
```

### Configuration

The `.mdc` file has three frontmatter fields:

| Field | Default | Description |
|-------|---------|-------------|
| `description` | Extraction expert... | Triggers the rule when Cursor detects relevant tasks |
| `globs` | `[]` (empty) | File patterns to auto-trigger (e.g., `["*.cs", "*.py"]`) |
| `alwaysApply` | `false` | Set to `true` to always load this rule |

### Customization Examples

```yaml
# Auto-trigger for C# files only
globs: ["*.cs"]
alwaysApply: false

# Always active (loaded in every conversation)
globs: []
alwaysApply: true

# Auto-trigger for multiple file types
globs: ["*.cs", "*.py", "*.ts", "*.md"]
alwaysApply: false
```

### Cursor vs Claude Code

| Feature | Claude Code (SKILL.md) | Cursor (.mdc) |
|---------|----------------------|---------------|
| Skill location | `.claude/skills/structured-extractor/` | `.cursor/skills/structured-extractor/` |
| Rule file | `SKILL.md` (auto-detected) | `.cursor/rules/structured-extractor.mdc` (installed by script) |
| Trigger | `description` field + `/skill` invocation | `description` + `globs` + `alwaysApply` |
| Reference access | Relative paths from `SKILL.md` | Full paths from `.cursor/skills/` root |
| Pipeline | Same `scripts/pipeline.py` | Same `scripts/pipeline.py` |
| Install | Copy to `.claude/skills/` | Clone + run `install.ps1` / `install.sh` |

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

**Input format**: `--input` accepts both formats:
- Array: `[{"id": "ext_001", ...}, ...]`
- Object: `{"extractions": [{"id": "ext_001", ...}, ...]}`

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

**structured-extractor** 是一个 Claude Code Skill / Cursor Rule，用于从代码、文档和日志中提取结构化信息。

### 起源: 从 LangExtract 中学到的

[Google LangExtract](https://github.com/google/langextract) 是 Google 推出的 Gemini 驱动的结构化提取库。研究其内部实现后，我们发现它分为两个层次:

- **AI 层** (~90%): Prompt 工程、Few-shot 示例、Schema 约束 -- 决定提取质量的核心，由 LLM 提供
- **算法层** (~10%): 基于 `difflib.SequenceMatcher` 的 Source Grounding、字符偏移去重、结果聚合 -- 纯 Python，与模型无关

**核心洞察: 如果你已经在 AI 编程助手 (Claude Code / Cursor) 中工作，AI 层已经存在，不需要再额外调用 Gemini。你真正需要的是算法后处理层。**

structured-extractor 将 LangExtract 的 Source Grounding 和去重算法提取出来，**改进** (best-win 去重替代 first-win、3 级匹配、4 维置信度评分) 并 **扩展** (实体消歧、关系推断、知识图谱注入) -- 这些是 LangExtract 没有的能力。无需外部依赖或 API 密钥。

## 为什么需要 structured-extractor?

代码知识存在于三个层次，大多数工具只能触及前两层:

```
  第3层 (语义层)    "迭代期间必须延迟关闭，防止遍历时修改集合"
      ^              structured-extractor 提取的是这一层
      |
  第2层 (定位层)    "m_IsDelayShutdown 出现在第 42、87、153 行"
      ^              Grep / 代码搜索擅长这一层
      |
  第1层 (结构层)    "GameSolver 有字段 m_IsDelayShutdown (bool) 和方法 Shutdown()"
                     AST / Repomap / tree-sitter 擅长这一层
```

### AST 看到骨架，structured-extractor 看到灵魂

| 能力 | AST / Repomap | Grep / 搜索 | structured-extractor |
|------|:---:|:---:|:---:|
| 类层级和成员 | Yes | -- | -- |
| 符号定位 | -- | Yes | Yes |
| **业务规则** | -- | -- | **Yes** |
| **顺序约束** | -- | -- | **Yes** |
| **因果推理 (为什么)** | -- | -- | **Yes** |
| **跨位置规则聚合** | -- | -- | **Yes** |
| **违反后果** | -- | -- | **Yes** |

### AST 无法捕获的三类知识

1. **隐式顺序约束** -- AST 看到 4 个顺序调用，但无法区分 "恰好这个顺序" 和 "必须这个顺序否则崩溃"
2. **分散的复合规则** -- 暂停逻辑分布在三个位置 (阶段检查/输入清理/时间冻结)，AST 认为是三条独立语句，只有 structured-extractor 将它们关联为 "暂停三件套"
3. **防御性代码的 "为什么"** -- `lastUpdateTime = Time.current` 在 Resume 中，AST 看到赋值语句；structured-extractor 看到 "防止暂停后首帧 deltaTime 异常导致角色瞬移"

> 理想的开发者知识系统应三层全覆盖: Repomap 做结构导航，Grep 做精确定位，structured-extractor 做语义理解。三者互补而非竞争。

## 核心特性

- **6 种提取类型**: rule (规则), event (事件), state (状态), constraint (约束), entity (实体), relation (关系)
- **3 种预设配置**: 代码逻辑分析、文档结构提取、日志分析
- **5 步处理管道 + 3 种输出**: 源码定位 -> 重叠去重 -> 置信度评分 -> 实体消歧 -> 关系推断 -> 输出为 JSON / Markdown / 知识图谱
- **零外部依赖**: 仅使用 Python 标准库
- **无需 API 密钥**: 直接使用 Claude Code 内置 AI

## 安装

### Claude Code

```bash
# 克隆仓库
git clone https://github.com/sputnicyoji/structured-extractor.git

# 复制到项目的 Claude Code skills 目录
cp -r structured-extractor/ your-project/.claude/skills/structured-extractor/
```

### Cursor IDE (独立安装，无需 Claude Code)

```bash
# 1. 克隆完整技能到项目的 .cursor/skills/ 目录
cd your-project
git clone https://github.com/sputnicyoji/Structured-Extractor .cursor/skills/structured-extractor

# 2. 运行安装脚本 (自动复制 .mdc 到 .cursor/rules/)
# Windows PowerShell:
.cursor/skills/structured-extractor/install.ps1

# macOS / Linux:
bash .cursor/skills/structured-extractor/install.sh
```

安装后 `.mdc` 规则文件会引用 `.cursor/skills/structured-extractor/` 下的所有资源 (references, scripts, presets)，Cursor 的 AI 可以完整使用提取类型定义、Few-shot 模板和 Python 管道。

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
  --output result.json
```

**输入格式**: `--input` 同时支持两种 JSON 格式:
- 纯数组: `[{"id": "ext_001", ...}, ...]`
- 对象包装: `{"extractions": [{"id": "ext_001", ...}, ...]}`

## 管道流程

```
Claude AI 提取 -> JSON -> Python 管道 (6 步后处理) -> 结构化输出

步骤 1: 源码定位    - 3 级文本对齐 (精确/归一化/模糊匹配)
步骤 2: 重叠去重    - 移除重叠率 > 50% 的重复提取
步骤 3: 置信度评分  - 4 维加权: 匹配质量(35%) + 属性完整度(25%)
                      + 文本特异性(20%) + 类型一致性(20%)
步骤 4: 实体消歧    - (可选) 基于 difflib 的贪心聚类
步骤 5: 关系推断    - (可选) 基于共现的规则推断

输出格式 (完成后选择):
  - JSON 文件     - 保存为 .json (始终可用)
  - Markdown 报告 - 生成可读的 .md 文件 (始终可用)
  - 知识图谱注入  - 写入 KG (需要 KG 工具)
```

## 性能

- 1000 条提取 + 500 行源码: < 1 秒
- 算法复杂度: O(n^2) 或更优
- 每条提取内存占用: ~1 KB

---

---

# 日本語

## 概要

**structured-extractor** は、コード・ドキュメント・ログから構造化情報を抽出する Claude Code Skill / Cursor Rule です。

### 起源: LangExtract から学んだこと

[Google LangExtract](https://github.com/google/langextract) は Google が開発した Gemini ベースの構造化抽出ライブラリです。内部実装を分析した結果、2つのレイヤーが識別できました:

- **AI レイヤー** (~90%): プロンプト設計、Few-shot 例、スキーマ制約 -- 抽出品質を決める中核、LLM が提供
- **アルゴリズムレイヤー** (~10%): `difflib.SequenceMatcher` による Source Grounding、文字オフセット重複排除、結果集約 -- 純粋な Python、モデル非依存

**核心的な洞察: AI コーディングアシスタント (Claude Code / Cursor) 内で作業している場合、AI レイヤーは既に存在します。Gemini への追加呼び出しは不要です。必要なのはアルゴリズム後処理レイヤーだけです。**

structured-extractor は LangExtract の Source Grounding と重複排除アルゴリズムを抽出し、**改良** (first-win から best-win へ、3段階マッチング、4次元信頼度スコアリング) および **拡張** (エンティティ解決、関係推論、ナレッジグラフ注入) しました。外部依存や API キーは不要です。

## なぜ structured-extractor が必要か?

コード知識は3つのレイヤーに存在しますが、ほとんどのツールは最初の2つしか到達できません:

```
  Layer 3 (意味層)    "イテレーション中はシャットダウンを遅延させ、コレクション変更を防ぐ"
      ^                structured-extractor はこのレイヤーを抽出
      |
  Layer 2 (位置層)    "m_IsDelayShutdown は 42行目、87行目、153行目に出現"
      ^                Grep / コード検索の得意分野
      |
  Layer 1 (構造層)    "GameSolver にフィールド m_IsDelayShutdown (bool) とメソッド Shutdown() がある"
                       AST / Repomap / tree-sitter の得意分野
```

### AST は骨格を見せ、structured-extractor は魂を見せる

| 能力 | AST / Repomap | Grep / 検索 | structured-extractor |
|------|:---:|:---:|:---:|
| クラス階層・メンバー | Yes | -- | -- |
| シンボル位置特定 | -- | Yes | Yes |
| **ビジネスルール** | -- | -- | **Yes** |
| **順序制約** | -- | -- | **Yes** |
| **因果推論 (なぜ)** | -- | -- | **Yes** |
| **分散ルールの集約** | -- | -- | **Yes** |
| **違反時の結果** | -- | -- | **Yes** |

### AST が捕捉できない3つの知識カテゴリ

1. **暗黙の順序制約** -- AST は4つの順次呼び出しを見ますが、「たまたまこの順序」と「この順序でなければクラッシュ」を区別できません
2. **分散した複合ルール** -- ポーズロジックが3箇所に分散 (ステージ確認/入力クリア/時間凍結)。AST は独立した3文と認識しますが、structured-extractor だけがこれらを「ポーズ三点セット」として関連付けます
3. **防御的コードの「なぜ」** -- `lastUpdateTime = Time.current` が Resume 内にある場合、AST は代入文と認識。structured-extractor は「ポーズ後の最初のフレームで deltaTime が異常に大きくなり、キャラクターが瞬間移動するのを防止」と理解します

> 理想的な開発者知識システムは3層すべてをカバー: Repomap で構造ナビゲーション、Grep で正確な位置特定、structured-extractor で意味理解。互いに補完し合う関係です。

## 主な特徴

- **6 種類の抽出タイプ**: rule (ルール), event (イベント), state (状態), constraint (制約), entity (エンティティ), relation (関係)
- **3 種類のプリセット設定**: コードロジック分析、ドキュメント構造抽出、ログ分析
- **5 段階パイプライン + 3 出力形式**: ソース位置特定 -> 重複排除 -> 信頼度スコアリング -> エンティティ解決 -> 関係推論 -> JSON / Markdown / ナレッジグラフ出力
- **外部依存ゼロ**: Python 標準ライブラリのみ使用
- **API キー不要**: Claude Code 内蔵の AI をそのまま利用

## インストール

### Claude Code

```bash
# リポジトリをクローン
git clone https://github.com/sputnicyoji/structured-extractor.git

# プロジェクトの Claude Code skills ディレクトリにコピー
cp -r structured-extractor/ your-project/.claude/skills/structured-extractor/
```

### Cursor IDE (スタンドアロンインストール、Claude Code 不要)

```bash
# 1. プロジェクトの .cursor/skills/ にクローン
cd your-project
git clone https://github.com/sputnicyoji/Structured-Extractor .cursor/skills/structured-extractor

# 2. インストールスクリプトを実行 (.mdc を .cursor/rules/ にコピー)
# Windows PowerShell:
.cursor/skills/structured-extractor/install.ps1

# macOS / Linux:
bash .cursor/skills/structured-extractor/install.sh
```

インストール後、`.mdc` ルールファイルは `.cursor/skills/structured-extractor/` 配下の全リソース (references, scripts, presets) を参照します。Cursor の AI は抽出タイプ定義、Few-shot テンプレート、Python パイプラインを完全に利用できます。

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
  --output result.json
```

**入力形式**: `--input` は2つの JSON 形式をサポート:
- 配列: `[{"id": "ext_001", ...}, ...]`
- オブジェクト: `{"extractions": [{"id": "ext_001", ...}, ...]}`

## パイプライン

```
Claude AI 抽出 -> JSON -> Python パイプライン (6段階後処理) -> 構造化出力

Step 1: ソース位置特定   - 3段階テキストアライメント (完全/正規化/あいまい一致)
Step 2: 重複排除         - 重複率 > 50% の抽出を除去
Step 3: 信頼度スコアリング - 4次元加重: 一致品質(35%) + 属性完全性(25%)
                           + テキスト特異性(20%) + 型一貫性(20%)
Step 4: エンティティ解決  - (任意) difflib ベースの貪欲クラスタリング
Step 5: 関係推論         - (任意) 共起ベースのルール推論

出力形式 (完了後に選択):
  - JSON ファイル       - .json として保存 (常に利用可能)
  - Markdown レポート   - 可読な .md ファイルを生成 (常に利用可能)
  - ナレッジグラフ注入   - KG に書き込み (KG ツールが必要)
```

## パフォーマンス

- 1000 件の抽出 + 500 行のソース: 1 秒未満
- アルゴリズム計算量: O(n^2) 以下
- 抽出 1 件あたりのメモリ: 約 1 KB
