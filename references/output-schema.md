# Output Schema

> 完整的输出 JSON Schema 定义

## 顶层结构

```json
{
  "metadata": { ... },
  "extractions": [ ... ],
  "relations": [ ... ],
  "stats": { ... }
}
```

## metadata (必填)

```json
{
  "source_file": "string - 源文件路径",
  "preset": "code-logic | doc-structure | log-analysis | full | custom",
  "pipeline_config": {
    "source_grounding": "boolean",
    "overlap_dedup": "boolean",
    "confidence_scoring": "boolean",
    "entity_resolution": "boolean",
    "relation_inference": "boolean",
    "kg_injection": "boolean"
  },
  "generated_at": "string - ISO 8601 时间戳",
  "extractor_version": "1.0.0"
}
```

## extraction 对象 (必填)

```json
{
  "id": "string - ext_001 格式, 顺序递增",
  "type": "rule | event | state | constraint | entity | relation",
  "text": "string - 原文精确片段 (不可改写)",
  "summary_cn": "string - 中文语义总结",
  "attributes": "object - 按 type 定义的属性 (见下方)",
  "source_file": "string - 所在文件名",
  "location": {
    "line": "number - 行号 (1-based)",
    "char_start": "number - 起始字符位置",
    "char_end": "number - 结束字符位置",
    "match_type": "exact | normalized | fuzzy | none",
    "confidence": "number - 0.0~1.0 置信度"
  }
}
```

### location 字段说明

| 字段 | 类型 | 说明 | 来源 |
|------|------|------|------|
| `line` | number | 行号 | Source Grounding 填充 |
| `char_start` | number | 起始字符位置 | Source Grounding 填充 |
| `char_end` | number | 结束字符位置 | Source Grounding 填充 |
| `match_type` | string | 匹配类型 | Source Grounding 填充 |
| `confidence` | number | 置信度评分 | Confidence Scoring 覆写 |

**match_type 含义**:

| 值 | 说明 | 典型置信度 |
|----|------|-----------|
| `exact` | 精确子串匹配 | 1.0 |
| `normalized` | 忽略空白后匹配 | 0.85 |
| `fuzzy` | difflib 模糊对齐 | 0.4~0.8 |
| `none` | 未匹配到 | 0.0 |

## attributes 按 type 定义

### type: rule

```json
{
  "condition": "string (必填) - 条件表达式或描述",
  "action": "string (必填) - 满足条件后执行的动作",
  "exception": "string (可选) - 例外情况",
  "priority": "string (可选) - 优先级"
}
```

### type: event

```json
{
  "event_type": "string (必填) - 事件名称",
  "direction": "subscribe | publish | both (必填)",
  "subscriber": "string (可选) - 订阅者",
  "publisher": "string (可选) - 发布者",
  "handler": "string (可选) - 处理方法",
  "payload": "string (可选) - 事件载荷描述"
}
```

### type: state

```json
{
  "from_state": "string (必填, 可为 unknown) - 起始状态",
  "to_state": "string (必填) - 目标状态",
  "trigger": "string (必填) - 触发条件",
  "guard_condition": "string (可选) - 守卫条件",
  "side_effect": "string (可选) - 副作用"
}
```

### type: constraint

```json
{
  "check_type": "null_check | boundary | precondition | assertion (必填)",
  "condition_cn": "string (必填) - 中文条件描述",
  "action": "return | throw | log | continue (可选) - 违反后动作",
  "severity": "error | warning | info (可选)"
}
```

### type: entity

```json
{
  "entity_name": "string (必填) - 实体名称",
  "entity_kind": "class | enum | role | service | concept (必填)",
  "parent": "string (可选) - 父类/父概念",
  "namespace": "string (可选) - 命名空间",
  "description": "string (可选) - 描述"
}
```

### type: relation

```json
{
  "from_entity": "string (必填) - 起始实体",
  "to_entity": "string (必填) - 目标实体",
  "relation_type": "inherits | depends_on | calls | contains | implements | relates_to (必填)",
  "direction": "uni | bi (可选, 默认 uni)",
  "strength": "strong | weak (可选)"
}
```

## relations 数组 (可选, Relation Inference 产生)

```json
{
  "from": "string - extraction ID (ext_xxx)",
  "to": "string - extraction ID (ext_xxx)",
  "type": "governs | calls | validates | subscribes_to | transitions | belongs_to | relates_to",
  "scope": "string - 共现范围标识"
}
```

**关系类型说明**:

| 类型 | 含义 | 典型来源组合 |
|------|------|-------------|
| `governs` | 规则约束实体 | rule -> entity |
| `validates` | 约束检查实体 | constraint -> entity |
| `subscribes_to` | 事件订阅 | event -> entity |
| `transitions` | 状态转换 | state -> entity |
| `calls` | 调用关系 | entity -> entity |
| `belongs_to` | 包含归属 | entity -> entity |
| `relates_to` | 通用关联 | 默认关系 |

## stats (Pipeline 自动生成)

```json
{
  "total": "number - 提取总数",
  "by_type": {
    "rule": "number",
    "event": "number",
    "state": "number",
    "constraint": "number",
    "entity": "number",
    "relation": "number"
  },
  "avg_confidence": "number - 平均置信度",
  "dedup_removed": "number - 去重移除数",
  "entities_merged": "number - 实体合并数"
}
```

## Claude 提取阶段的输出格式

Claude 在提取阶段只需要输出 `extractions` 数组，不需要包含 `location` 字段（由 Source Grounding 后处理填充）：

```json
[
  {
    "id": "ext_001",
    "type": "rule",
    "text": "if (MLevel.IsGuideLevel)",
    "summary_cn": "新手引导关卡特殊处理",
    "attributes": {
      "condition": "IsGuideLevel == true",
      "action": "自动上阵并进入战斗"
    },
    "source_file": "AMultiGateLevel.cs"
  }
]
```

**Pipeline 后处理后会自动添加**:
- `location` 字段 (Source Grounding)
- `confidence` 评分 (Confidence Scoring)
- 去除重复项 (Overlap Dedup)
- 实体合并 (Entity Resolution, 可选)
- 关系推断 (Relation Inference, 可选)
