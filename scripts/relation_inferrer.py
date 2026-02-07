"""
Relation Inference Module

基于规则表推断实体间关系：
- 按 source_file + 行号范围 分 scope (50行一组)
- 同 scope 内按类型对匹配推断关系
- 规则表驱动，支持自定义扩展
"""


# 推断规则表: (type_a, type_b) -> relation_type
INFERENCE_RULES = {
    ("rule", "entity"): "governs",
    ("constraint", "entity"): "validates",
    ("event", "entity"): "subscribes_to",
    ("state", "entity"): "transitions",
    ("entity", "entity"): "relates_to",
}


class RelationInferrer:
    """关系推断器"""

    def __init__(self, scope_window: int = 50):
        """
        Args:
            scope_window: scope 窗口大小 (行数)
        """
        self.scope_window = scope_window

    def process(self, extractions: list[dict]) -> tuple[list[dict], list[dict]]:
        """
        推断新关系

        Args:
            extractions: 提取项列表

        Returns:
            (原始extractions, 新推断的relations列表)
        """
        # 按 scope 分组
        scopes = self._group_by_scope(extractions)

        inferred_relations = []

        # 在每个 scope 内推断
        for scope_key, items in scopes.items():
            relations = self._infer_in_scope(items)
            inferred_relations.extend(relations)

        return extractions, inferred_relations

    def _group_by_scope(self, extractions: list[dict]) -> dict:
        """
        按 (source_file, line_group) 分组

        Args:
            extractions: 提取列表

        Returns:
            {scope_key: [items]}
        """
        scopes = {}

        for ext in extractions:
            loc = ext.get('source_location', {})
            line = loc.get('line')

            if line is None:
                continue

            # 获取源文件（如果有）
            source_file = ext.get('source_file', 'unknown')

            # 计算行分组 (0-49 -> 0, 50-99 -> 50, ...)
            line_group = (line // self.scope_window) * self.scope_window

            scope_key = (source_file, line_group)

            if scope_key not in scopes:
                scopes[scope_key] = []

            scopes[scope_key].append(ext)

        return scopes

    def _infer_in_scope(self, items: list[dict]) -> list[dict]:
        """
        在单个 scope 内推断关系

        Args:
            items: 同 scope 的提取项

        Returns:
            推断的关系列表
        """
        relations = []

        # 遍历所有类型对
        for i, item_a in enumerate(items):
            type_a = item_a.get('type')
            text_a = item_a.get('text', '')

            if not type_a or not text_a:
                continue

            for j, item_b in enumerate(items):
                if i == j:
                    continue  # 跳过自身

                type_b = item_b.get('type')
                text_b = item_b.get('text', '')

                if not type_b or not text_b:
                    continue

                # 查找匹配规则
                relation_type = self._find_relation(type_a, type_b)

                if relation_type:
                    # 创建关系
                    relation = {
                        "type": "relation",
                        "from": text_a,
                        "to": text_b,
                        "relation_type": relation_type,
                        "confidence": 0.6,  # 推断关系置信度较低
                        "inferred": True,
                    }
                    relations.append(relation)

        return relations

    def _find_relation(self, type_a: str, type_b: str) -> str:
        """
        查找类型对应的关系类型

        Args:
            type_a, type_b: 实体类型

        Returns:
            关系类型，或 None
        """
        # 精确匹配
        if (type_a, type_b) in INFERENCE_RULES:
            return INFERENCE_RULES[(type_a, type_b)]

        # 反向匹配
        if (type_b, type_a) in INFERENCE_RULES:
            return INFERENCE_RULES[(type_b, type_a)]

        return None


if __name__ == "__main__":
    # 测试示例
    extractions = [
        {
            "type": "rule",
            "text": "禁止修改 Solver",
            "source_location": {"line": 10},
            "source_file": "solver-readonly.md"
        },
        {
            "type": "entity",
            "text": "MGMultiGateSolver",
            "source_location": {"line": 15},
            "source_file": "solver-readonly.md"
        },
        {
            "type": "constraint",
            "text": "必须通过命令交互",
            "source_location": {"line": 20},
            "source_file": "solver-readonly.md"
        },
        {
            "type": "entity",
            "text": "CreateActorCommand",
            "source_location": {"line": 25},
            "source_file": "solver-readonly.md"
        },
        {
            "type": "entity",
            "text": "OtherEntity",
            "source_location": {"line": 100},  # 不同 scope
            "source_file": "solver-readonly.md"
        },
    ]

    inferrer = RelationInferrer(scope_window=50)
    _, inferred = inferrer.process(extractions)

    import json
    print(f"推断出 {len(inferred)} 条关系:")
    print(json.dumps(inferred, indent=2, ensure_ascii=False))
