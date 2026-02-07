# Extraction Types

> 6 种通用提取类型定义

## rule - 业务规则

**定义**: 包含条件判断的业务决策逻辑

**识别特征**:
- `if/else`, `switch/case`, `? :` 三元表达式
- 条件中包含业务概念（非纯技术检查）
- 决定了某个业务行为是否执行

**代码示例**:
```csharp
if (MLevel.IsGuideLevel)     // "新手引导关卡特殊处理"
if (hero.HeroID == mhero.ID) // "英雄未修改，跳过操作"
```

**文档示例**: "满3年工龄可申请晋升"
**日志示例**: 不常见

**必填属性**: `condition`, `action`
**可选属性**: `exception`, `priority`

---

## event - 事件流

**定义**: 事件的注册、发布、订阅关系

**识别特征**:
- `+=` 事件订阅, `-=` 取消订阅
- `FireEvent`, `SendMessage`, `Notify`, `Trigger`
- `EventMgr`, `TEvent`, `Action<T>`

**代码示例**:
```csharp
MLevel.LevelStageChanged += OnStageChanged;
RLevel.NotifyHeroRemoved(hero.Slot);
```

**文档示例**: "审批通过后通知财务部门"
**日志示例**: `[EVENT] OrderCreated orderId=12345`

**必填属性**: `event_type`, `direction` (subscribe/publish/both)
**可选属性**: `subscriber`, `publisher`, `handler`, `payload`

---

## state - 状态机

**定义**: 状态的转换、阶段的变化

**识别特征**:
- `SetState()`, `SetStage()`, `TransitionTo()`
- 枚举值赋值 (`status = EStatus.Active`)
- bool 状态切换 (`SetPaused(true)`)

**代码示例**:
```csharp
MLevel.SetLevelStage(ELevelStage.Fight);
MLevel.SetPaused(true);
```

**文档示例**: "草稿 -> 审核中 -> 已发布"
**日志示例**: `Status: PENDING -> RUNNING`

**必填属性**: `from_state` (可为 unknown), `to_state`, `trigger`
**可选属性**: `guard_condition`, `side_effect`

---

## constraint - 约束检查

**定义**: 校验、边界条件、前置断言、防御性检查

**识别特征**:
- `null == x`, `x == null`, `x != null`
- `x < 0`, `x >= max`, 边界检查
- `return` / `continue` / `break` 提前退出
- `throw`, `D.Error()`, `Debug.LogError()`

**代码示例**:
```csharp
if (null == formation) { D.Error("..."); return; }
if (teamInfo.heroId < 0) continue;
```

**文档示例**: "金额不得超过10万元"
**日志示例**: `[WARN] Request timeout > 30s`

**必填属性**: `check_type` (null_check/boundary/precondition/assertion), `condition_cn`
**可选属性**: `action` (return/throw/log/continue), `severity`

---

## entity - 实体

**定义**: 关键概念、类定义、角色、系统组件

**识别特征**:
- `class`, `struct`, `interface`, `enum` 定义
- 文档中的专有名词、角色定义
- 日志中的服务名、组件名

**代码示例**:
```csharp
public class MGMultiGateActor : ...
public enum ELevelStage { Ready, Fight, Settlement }
```

**文档示例**: "甲方: XX科技有限公司"
**日志示例**: `Service: payment-api v2.3.1`

**必填属性**: `entity_name`, `entity_kind` (class/enum/role/service/concept)
**可选属性**: `parent`, `namespace`, `description`

---

## relation - 关系

**定义**: 实体之间的关系

**识别特征**:
- 继承: `: BaseClass`, `extends`, `implements`
- 依赖: `new Xxx()`, `GetComponent<T>()`, 字段引用
- 调用: `xxx.Method()` 跨类调用

**代码示例**:
```csharp
public class AMultiGateLevel : AMultiGateLevelBase  // inherits
private MGMultiGateSolver m_Solver;                  // depends_on
```

**文档示例**: "部门A向部门B报告"
**日志示例**: `payment-api -> db-master (latency: 15ms)`

**必填属性**: `from_entity`, `to_entity`, `relation_type`
**可选属性**: `direction` (uni/bi), `strength` (strong/weak)
