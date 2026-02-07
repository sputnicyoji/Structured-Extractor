# Few-shot Templates

> 各场景的 Few-shot 示例，Claude 提取时参考

## code 场景 (C# / Python / JS)

### rule 示例

**输入代码**:
```csharp
if (MLevel.IsGuideLevel)
{
    AutoSetHeroes();
    EnterBattle();
}
```

**提取输出**:
```json
{
  "id": "ext_001",
  "type": "rule",
  "text": "if (MLevel.IsGuideLevel)",
  "summary_cn": "新手引导关卡自动上阵并进入战斗",
  "attributes": {
    "condition": "IsGuideLevel == true",
    "action": "自动上阵英雄并进入战斗"
  },
  "source_file": "AMultiGateLevel.cs"
}
```

### event 示例

**输入代码**:
```csharp
MLevel.LevelStageChanged += OnStageChanged;
```

**提取输出**:
```json
{
  "id": "ext_002",
  "type": "event",
  "text": "MLevel.LevelStageChanged += OnStageChanged;",
  "summary_cn": "订阅关卡阶段变化事件",
  "attributes": {
    "event_type": "LevelStageChanged",
    "direction": "subscribe",
    "subscriber": "当前类",
    "handler": "OnStageChanged"
  },
  "source_file": "AMultiGateLevel.cs"
}
```

### state 示例

**输入代码**:
```csharp
MLevel.SetLevelStage(ELevelStage.Fight);
```

**提取输出**:
```json
{
  "id": "ext_003",
  "type": "state",
  "text": "MLevel.SetLevelStage(ELevelStage.Fight);",
  "summary_cn": "关卡进入战斗阶段",
  "attributes": {
    "from_state": "unknown",
    "to_state": "Fight",
    "trigger": "SetLevelStage 调用"
  },
  "source_file": "AMultiGateLevel.cs"
}
```

### constraint 示例

**输入代码**:
```csharp
if (null == formation)
{
    D.Error("[MultiGate] formation is null");
    return;
}
```

**提取输出**:
```json
{
  "id": "ext_004",
  "type": "constraint",
  "text": "if (null == formation)",
  "summary_cn": "阵型数据不能为空",
  "attributes": {
    "check_type": "null_check",
    "condition_cn": "formation 对象不能为 null",
    "action": "return",
    "severity": "error"
  },
  "source_file": "FormationGenerator.cs"
}
```

### entity 示例

**输入代码**:
```csharp
public class MGMultiGateActor : MGMultiGateActorBase
{
    // 倍增门中的角色实体
}
```

**提取输出**:
```json
{
  "id": "ext_005",
  "type": "entity",
  "text": "public class MGMultiGateActor : MGMultiGateActorBase",
  "summary_cn": "倍增门角色实体",
  "attributes": {
    "entity_name": "MGMultiGateActor",
    "entity_kind": "class",
    "parent": "MGMultiGateActorBase",
    "namespace": "ScriptGame.MGMultiGate"
  },
  "source_file": "MGMultiGateActor.cs"
}
```

### relation 示例

**输入代码**:
```csharp
public class AMultiGateLevel : AMultiGateLevelBase
{
    private MGMultiGateSolver m_Solver;
}
```

**提取输出**:
```json
[
  {
    "id": "ext_006",
    "type": "relation",
    "text": "public class AMultiGateLevel : AMultiGateLevelBase",
    "summary_cn": "AMultiGateLevel 继承自 AMultiGateLevelBase",
    "attributes": {
      "from_entity": "AMultiGateLevel",
      "to_entity": "AMultiGateLevelBase",
      "relation_type": "inherits"
    },
    "source_file": "AMultiGateLevel.cs"
  },
  {
    "id": "ext_007",
    "type": "relation",
    "text": "private MGMultiGateSolver m_Solver;",
    "summary_cn": "AMultiGateLevel 依赖 MGMultiGateSolver",
    "attributes": {
      "from_entity": "AMultiGateLevel",
      "to_entity": "MGMultiGateSolver",
      "relation_type": "depends_on",
      "strength": "strong"
    },
    "source_file": "AMultiGateLevel.cs"
  }
]
```

---

## document 场景 (合同/规范/文档)

### rule 示例

**输入文本**:
```
第五条：员工满3年工龄且年度绩效评分不低于B级，可申请晋升。
```

**提取输出**:
```json
{
  "id": "ext_001",
  "type": "rule",
  "text": "员工满3年工龄且年度绩效评分不低于B级，可申请晋升",
  "summary_cn": "晋升条件：3年工龄 + 绩效B级以上",
  "attributes": {
    "condition": "工龄 >= 3年 AND 绩效 >= B",
    "action": "可申请晋升"
  },
  "source_file": "员工手册.md"
}
```

### entity 示例

**输入文本**:
```
甲方: 深圳XX科技有限公司 (统一社会信用代码: 91440300...)
乙方: 张三，身份证号: 440...
```

**提取输出**:
```json
[
  {
    "id": "ext_002",
    "type": "entity",
    "text": "甲方: 深圳XX科技有限公司",
    "summary_cn": "合同甲方",
    "attributes": {
      "entity_name": "深圳XX科技有限公司",
      "entity_kind": "role",
      "description": "合同甲方，统一社会信用代码 91440300..."
    },
    "source_file": "合同.md"
  },
  {
    "id": "ext_003",
    "type": "entity",
    "text": "乙方: 张三",
    "summary_cn": "合同乙方",
    "attributes": {
      "entity_name": "张三",
      "entity_kind": "role",
      "description": "合同乙方，自然人"
    },
    "source_file": "合同.md"
  }
]
```

### constraint 示例

**输入文本**:
```
付款金额不得超过合同总额的30%，且单次付款不超过10万元。
```

**提取输出**:
```json
{
  "id": "ext_004",
  "type": "constraint",
  "text": "付款金额不得超过合同总额的30%，且单次付款不超过10万元",
  "summary_cn": "付款金额双重上限约束",
  "attributes": {
    "check_type": "boundary",
    "condition_cn": "付款 <= 合同总额*30% AND 单次 <= 10万",
    "severity": "mandatory"
  },
  "source_file": "合同.md"
}
```

---

## log 场景 (服务器日志/应用日志)

### event 示例

**输入日志**:
```
2026-02-06 14:23:15 [INFO] [OrderService] OrderCreated orderId=12345 userId=U001 amount=99.9
```

**提取输出**:
```json
{
  "id": "ext_001",
  "type": "event",
  "text": "[OrderService] OrderCreated orderId=12345 userId=U001 amount=99.9",
  "summary_cn": "订单创建事件",
  "attributes": {
    "event_type": "OrderCreated",
    "direction": "publish",
    "publisher": "OrderService",
    "payload": "orderId=12345, userId=U001, amount=99.9"
  },
  "source_file": "app.log"
}
```

### state 示例

**输入日志**:
```
2026-02-06 14:23:16 [INFO] [Pipeline] Job-7890 status changed: PENDING -> RUNNING
```

**提取输出**:
```json
{
  "id": "ext_002",
  "type": "state",
  "text": "Job-7890 status changed: PENDING -> RUNNING",
  "summary_cn": "任务 7890 从等待转为运行",
  "attributes": {
    "from_state": "PENDING",
    "to_state": "RUNNING",
    "trigger": "Pipeline 调度"
  },
  "source_file": "app.log"
}
```

### constraint 示例

**输入日志**:
```
2026-02-06 14:24:00 [WARN] [Gateway] Request timeout: 35.2s > threshold 30s, clientIP=192.168.1.100
```

**提取输出**:
```json
{
  "id": "ext_003",
  "type": "constraint",
  "text": "Request timeout: 35.2s > threshold 30s",
  "summary_cn": "请求超时超过 30 秒阈值",
  "attributes": {
    "check_type": "boundary",
    "condition_cn": "请求耗时 35.2s 超过阈值 30s",
    "action": "warn",
    "severity": "warning"
  },
  "source_file": "app.log"
}
```

---

## 提取原则

1. **text 必须来自原文** - 不能改写、翻译或总结，必须是原文的精确片段
2. **summary_cn 是中文语义总结** - 简洁描述这段文本的业务含义
3. **attributes 遵循类型定义** - 参见 `extraction-types.md` 中的必填/可选属性
4. **一段文本可产生多个提取** - 如同时包含 entity + relation
5. **ID 按顺序递增** - `ext_001`, `ext_002`, ...
