"""Tests for kg_injector module."""

import pytest
from kg_injector import KGInjector


class TestKGInjector:
    """Tests for the KGInjector class."""

    def test_basic_entity_conversion(self):
        injector = KGInjector()
        extractions = [{
            "type": "entity",
            "text": "MGMultiGateSolver",
            "summary_cn": "倍增门解算器",
            "confidence": 0.85,
            "source_file": "test.cs",
            "source_location": {"line": 42},
        }]
        result = injector.convert(extractions)
        assert len(result["entities"]) == 1
        entity = result["entities"][0]
        assert "entity:" in entity["name"]
        assert entity["entityType"] == "entity"
        assert any("倍增门解算器" in obs for obs in entity["observations"])

    def test_unique_entity_names(self):
        """Different types with same summary should have different KG names."""
        injector = KGInjector()
        extractions = [
            {"type": "entity", "text": "Solver", "summary_cn": "解算器", "confidence": 0.9},
            {"type": "rule", "text": "Solver rule", "summary_cn": "解算器", "confidence": 0.9},
        ]
        result = injector.convert(extractions)
        names = [e["name"] for e in result["entities"]]
        assert len(names) == len(set(names)), f"Duplicate names: {names}"

    def test_name_format_type_prefix(self):
        """Entity name should have type: prefix."""
        injector = KGInjector()
        extractions = [
            {"type": "rule", "text": "some rule", "summary_cn": "规则", "confidence": 0.9},
        ]
        result = injector.convert(extractions)
        assert result["entities"][0]["name"].startswith("rule:")

    def test_low_confidence_filtered(self):
        injector = KGInjector(confidence_threshold=0.5)
        extractions = [
            {"type": "entity", "text": "high", "confidence": 0.8},
            {"type": "entity", "text": "low", "confidence": 0.3},
        ]
        result = injector.convert(extractions)
        assert len(result["entities"]) == 1

    def test_relation_conversion(self):
        injector = KGInjector()
        extractions = [
            {"type": "relation", "from": "A", "to": "B", "relation_type": "uses", "confidence": 0.8},
        ]
        result = injector.convert(extractions)
        assert len(result["relations"]) == 1
        rel = result["relations"][0]
        assert rel["from"] == "A"
        assert rel["to"] == "B"
        assert rel["relationType"] == "uses"

    def test_inferred_relations_included(self):
        injector = KGInjector()
        extractions = []
        relations = [
            {"from": "X", "to": "Y", "relation_type": "governs", "confidence": 0.6},
        ]
        result = injector.convert(extractions, relations)
        assert len(result["relations"]) == 1

    def test_low_confidence_relations_filtered(self):
        injector = KGInjector(confidence_threshold=0.7)
        extractions = []
        relations = [
            {"from": "X", "to": "Y", "relation_type": "governs", "confidence": 0.5},
        ]
        result = injector.convert(extractions, relations)
        assert len(result["relations"]) == 0

    def test_observations_include_source_info(self):
        injector = KGInjector()
        extractions = [{
            "type": "entity",
            "text": "Foo",
            "confidence": 0.9,
            "source_file": "bar.cs",
            "source_location": {"line": 10},
        }]
        result = injector.convert(extractions)
        obs = result["entities"][0]["observations"]
        assert any("bar.cs:10" in o for o in obs)

    def test_observations_include_confidence(self):
        injector = KGInjector()
        extractions = [{
            "type": "entity",
            "text": "Foo",
            "confidence": 0.85,
        }]
        result = injector.convert(extractions)
        obs = result["entities"][0]["observations"]
        assert any("0.85" in o for o in obs)

    def test_fallback_name_from_text(self):
        injector = KGInjector()
        extractions = [{"type": "entity", "text": "SomeClassName", "confidence": 0.9}]
        result = injector.convert(extractions)
        assert "SomeClassName" in result["entities"][0]["name"]

    def test_empty_input(self):
        injector = KGInjector()
        result = injector.convert([])
        assert result == {"entities": [], "relations": []}

    def test_all_types_converted(self):
        """entity, rule, constraint, event, state should all be converted."""
        injector = KGInjector()
        types = ["entity", "rule", "constraint", "event", "state"]
        extractions = [
            {"type": t, "text": f"text_{t}", "confidence": 0.9}
            for t in types
        ]
        result = injector.convert(extractions)
        assert len(result["entities"]) == 5

    def test_relation_type_not_converted_to_entity(self):
        injector = KGInjector()
        extractions = [
            {"type": "relation", "from": "A", "to": "B", "relation_type": "uses", "confidence": 0.9},
        ]
        result = injector.convert(extractions)
        assert len(result["entities"]) == 0
        assert len(result["relations"]) == 1
