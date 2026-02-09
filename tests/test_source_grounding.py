"""Tests for source_grounding module."""

import pytest
from source_grounding import SourceGrounder


class TestSourceGrounder:
    """Tests for the SourceGrounder class."""

    def test_exact_match(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        extractions = [{"type": "entity", "text": "public class MGMultiGateSolver"}]
        result = grounder.process(extractions)

        assert len(result) == 1
        loc = result[0]["source_location"]
        assert loc["match_type"] == "exact"
        assert loc["confidence"] == 1.0
        assert loc["char_start"] is not None
        assert loc["char_end"] > loc["char_start"]
        assert loc["line"] == 1

    def test_normalized_match(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        # Text with different whitespace
        extractions = [{"type": "entity", "text": "NativeArray<ActorData>m_ActorData"}]
        result = grounder.process(extractions)

        loc = result[0]["source_location"]
        assert loc["match_type"] in ("exact", "normalized")
        assert loc["confidence"] >= 0.85

    def test_fuzzy_match(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        # Text with slight differences from source - enough overlap for fuzzy match
        extractions = [{"type": "entity", "text": "ProcessCommand(cmd)"}]
        result = grounder.process(extractions)

        loc = result[0]["source_location"]
        # "ProcessCommand(cmd)" should fuzzy-match against "ProcessCommand(cmd);" in source
        assert loc["match_type"] in ("exact", "normalized", "fuzzy")

    def test_no_match(self):
        grounder = SourceGrounder("hello world")
        extractions = [{"type": "entity", "text": "completely unrelated text that does not exist anywhere"}]
        result = grounder.process(extractions)

        loc = result[0]["source_location"]
        assert loc["match_type"] in ("none", "fuzzy")

    def test_empty_text_skipped(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        extractions = [{"type": "entity", "text": ""}]
        result = grounder.process(extractions)

        assert len(result) == 1
        assert "source_location" not in result[0]

    def test_empty_extractions(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        result = grounder.process([])
        assert result == []

    def test_char_interval_is_tuple(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        extractions = [{"type": "entity", "text": "public class MGMultiGateSolver"}]
        result = grounder.process(extractions)

        interval = result[0]["source_location"]["char_interval"]
        assert len(interval) == 2
        assert interval[0] < interval[1]

    def test_line_number_accuracy(self):
        source = "line1\nline2\nline3_target\nline4"
        grounder = SourceGrounder(source)
        extractions = [{"type": "entity", "text": "line3_target"}]
        result = grounder.process(extractions)

        assert result[0]["source_location"]["line"] == 3

    def test_multiple_extractions(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        extractions = [
            {"type": "entity", "text": "public class MGMultiGateSolver"},
            {"type": "entity", "text": "AddCommand"},
            {"type": "entity", "text": "Initialize"},
        ]
        result = grounder.process(extractions)

        assert len(result) == 3
        for item in result:
            assert "source_location" in item
            assert item["source_location"]["match_type"] == "exact"

    def test_preserves_original_fields(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        extractions = [{"type": "entity", "text": "Initialize", "custom_field": "preserved"}]
        result = grounder.process(extractions)

        assert result[0]["custom_field"] == "preserved"
        assert result[0]["type"] == "entity"

    def test_does_not_mutate_input(self, sample_source_text):
        grounder = SourceGrounder(sample_source_text)
        original = {"type": "entity", "text": "Initialize"}
        extractions = [original]
        grounder.process(extractions)

        assert "source_location" not in original
