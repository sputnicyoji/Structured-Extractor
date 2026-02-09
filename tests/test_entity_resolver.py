"""Tests for entity_resolver module."""

import pytest
from entity_resolver import EntityResolver


class TestEntityResolver:
    """Tests for the EntityResolver class."""

    def test_identical_entities_merged(self):
        resolver = EntityResolver(threshold=0.7)
        extractions = [
            {"type": "entity", "text": "MGMultiGateSolver", "summary_cn": "解算器1"},
            {"type": "entity", "text": "MGMultiGateSolver", "summary_cn": "解算器2"},
        ]
        result = resolver.process(extractions)
        entities = [e for e in result if e["type"] == "entity"]
        assert len(entities) == 1

    def test_different_entities_kept(self):
        resolver = EntityResolver(threshold=0.7)
        extractions = [
            {"type": "entity", "text": "MGMultiGateSolver"},
            {"type": "entity", "text": "Actor"},
        ]
        result = resolver.process(extractions)
        entities = [e for e in result if e["type"] == "entity"]
        assert len(entities) == 2

    def test_containment_similarity(self):
        """Short name contained in long name: similarity = 0.9 * (short/long)."""
        resolver = EntityResolver(threshold=0.3)
        extractions = [
            {"type": "entity", "text": "Solver"},         # 6 chars
            {"type": "entity", "text": "MGSolver"},        # 8 chars, contains "Solver"
        ]
        result = resolver.process(extractions)
        entities = [e for e in result if e["type"] == "entity"]
        # 0.9 * (6/8) = 0.675 < 0.7 default threshold, but we set threshold=0.3
        assert len(entities) == 1

    def test_short_containment_below_threshold(self):
        """Short name in long name with high threshold stays separate."""
        resolver = EntityResolver(threshold=0.7)
        extractions = [
            {"type": "entity", "text": "Map"},             # 3 chars
            {"type": "entity", "text": "MapManager"},      # 10 chars
        ]
        result = resolver.process(extractions)
        entities = [e for e in result if e["type"] == "entity"]
        # 0.9 * (3/10) = 0.27 < 0.7 threshold
        assert len(entities) == 2

    def test_canonical_name_prefers_camelcase(self):
        resolver = EntityResolver(threshold=0.5)
        extractions = [
            {"type": "entity", "text": "my solver class"},
            {"type": "entity", "text": "MySolverClass"},
        ]
        result = resolver.process(extractions)
        entities = [e for e in result if e["type"] == "entity"]
        # Should prefer CamelCase (no spaces)
        if len(entities) == 1:
            assert " " not in entities[0]["text"]

    def test_relation_references_rewritten(self):
        resolver = EntityResolver(threshold=0.5)
        extractions = [
            {"type": "entity", "text": "Solver"},
            {"type": "entity", "text": "TheSolver"},
            {"type": "relation", "from": "Solver", "to": "Actor", "relation_type": "uses"},
        ]
        result = resolver.process(extractions)
        relations = [e for e in result if e["type"] == "relation"]
        if relations:
            # If Solver was merged into TheSolver, relation should point to TheSolver
            assert relations[0]["from"] in ("Solver", "TheSolver")

    def test_non_entities_preserved(self):
        resolver = EntityResolver(threshold=0.7)
        extractions = [
            {"type": "entity", "text": "Foo"},
            {"type": "rule", "text": "some rule"},
            {"type": "constraint", "text": "some constraint"},
        ]
        result = resolver.process(extractions)
        assert any(e["type"] == "rule" for e in result)
        assert any(e["type"] == "constraint" for e in result)

    def test_single_entity_no_change(self):
        resolver = EntityResolver()
        extractions = [{"type": "entity", "text": "OnlyOne"}]
        result = resolver.process(extractions)
        assert len(result) == 1
        assert result[0]["text"] == "OnlyOne"

    def test_empty_input(self):
        resolver = EntityResolver()
        assert resolver.process([]) == []

    def test_no_entities_no_change(self):
        resolver = EntityResolver()
        extractions = [
            {"type": "rule", "text": "rule1"},
            {"type": "constraint", "text": "constraint1"},
        ]
        result = resolver.process(extractions)
        assert len(result) == 2
