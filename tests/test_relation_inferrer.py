"""Tests for relation_inferrer module."""

import pytest
from relation_inferrer import RelationInferrer


def _make_ext(ext_type, text, line, source_file="test.cs"):
    return {
        "type": ext_type,
        "text": text,
        "source_location": {"line": line},
        "source_file": source_file,
    }


class TestRelationInferrer:
    """Tests for the RelationInferrer class."""

    def test_rule_entity_infers_governs(self):
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("rule", "must validate input", 10),
            _make_ext("entity", "InputValidator", 15),
        ]
        _, relations = inferrer.process(extractions)
        assert len(relations) >= 1
        assert any(r["relation_type"] == "governs" for r in relations)

    def test_constraint_entity_infers_validates(self):
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("constraint", "null check required", 10),
            _make_ext("entity", "DataProcessor", 20),
        ]
        _, relations = inferrer.process(extractions)
        assert any(r["relation_type"] == "validates" for r in relations)

    def test_event_entity_infers_subscribes(self):
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("event", "OnClick event", 10),
            _make_ext("entity", "ButtonHandler", 15),
        ]
        _, relations = inferrer.process(extractions)
        assert any(r["relation_type"] == "subscribes_to" for r in relations)

    def test_state_entity_infers_transitions(self):
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("state", "SetState(Active)", 10),
            _make_ext("entity", "StateMachine", 20),
        ]
        _, relations = inferrer.process(extractions)
        assert any(r["relation_type"] == "transitions" for r in relations)

    def test_entity_entity_infers_relates_to(self):
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("entity", "ClassA", 10),
            _make_ext("entity", "ClassB", 20),
        ]
        _, relations = inferrer.process(extractions)
        assert any(r["relation_type"] == "relates_to" for r in relations)

    def test_different_scope_no_inference(self):
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("rule", "some rule", 10),
            _make_ext("entity", "SomeEntity", 100),  # Line 100 -> different scope
        ]
        _, relations = inferrer.process(extractions)
        assert len(relations) == 0

    def test_different_file_no_inference(self):
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("rule", "some rule", 10, source_file="file1.cs"),
            _make_ext("entity", "SomeEntity", 10, source_file="file2.cs"),
        ]
        _, relations = inferrer.process(extractions)
        assert len(relations) == 0

    def test_no_duplicate_relations(self):
        """Same pair should not produce duplicate relations."""
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("rule", "rule text", 10),
            _make_ext("entity", "entity text", 10),
        ]
        _, relations = inferrer.process(extractions)
        dedup_keys = [(r["from"], r["to"], r["relation_type"]) for r in relations]
        assert len(dedup_keys) == len(set(dedup_keys))

    def test_bidirectional_entity_dedup(self):
        """entity-entity should only produce one direction (i < j)."""
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("entity", "A", 10),
            _make_ext("entity", "B", 15),
        ]
        _, relations = inferrer.process(extractions)
        relates_to = [r for r in relations if r["relation_type"] == "relates_to"]
        # Should only have A->B, not B->A
        assert len(relates_to) == 1
        assert relates_to[0]["from"] == "A"
        assert relates_to[0]["to"] == "B"

    def test_no_location_items_ignored(self):
        inferrer = RelationInferrer()
        extractions = [
            {"type": "rule", "text": "no location"},
            {"type": "entity", "text": "no location"},
        ]
        _, relations = inferrer.process(extractions)
        assert len(relations) == 0

    def test_empty_input(self):
        inferrer = RelationInferrer()
        _, relations = inferrer.process([])
        assert relations == []

    def test_extractions_returned_unchanged(self):
        inferrer = RelationInferrer()
        extractions = [_make_ext("entity", "test", 10)]
        returned_exts, _ = inferrer.process(extractions)
        assert returned_exts is extractions

    def test_inferred_relations_have_required_fields(self):
        inferrer = RelationInferrer(scope_window=50)
        extractions = [
            _make_ext("rule", "some rule", 10),
            _make_ext("entity", "SomeEntity", 15),
        ]
        _, relations = inferrer.process(extractions)
        for rel in relations:
            assert "type" in rel
            assert rel["type"] == "relation"
            assert "from" in rel
            assert "to" in rel
            assert "relation_type" in rel
            assert "confidence" in rel
            assert rel["inferred"] is True
