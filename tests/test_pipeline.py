"""Integration tests for the pipeline module."""

import pytest
from pipeline import ExtractionPipeline


class TestExtractionPipeline:
    """Integration tests for the full pipeline."""

    def test_basic_pipeline(self, sample_source_text, sample_extractions):
        pipeline = ExtractionPipeline(sample_source_text)
        result = pipeline.process(sample_extractions)

        assert "extractions" in result
        assert "inferred_relations" in result
        assert "stats" in result
        assert len(result["extractions"]) > 0

    def test_all_extractions_have_confidence(self, sample_source_text, sample_extractions):
        pipeline = ExtractionPipeline(sample_source_text)
        result = pipeline.process(sample_extractions)

        for ext in result["extractions"]:
            assert "confidence" in ext
            assert 0.0 <= ext["confidence"] <= 1.0

    def test_all_extractions_have_source_location(self, sample_source_text, sample_extractions):
        pipeline = ExtractionPipeline(sample_source_text)
        result = pipeline.process(sample_extractions)

        for ext in result["extractions"]:
            assert "source_location" in ext

    def test_stats_has_required_fields(self, sample_source_text, sample_extractions):
        pipeline = ExtractionPipeline(sample_source_text)
        result = pipeline.process(sample_extractions)
        stats = result["stats"]

        assert "total_extractions" in stats
        assert "dedup_removed" in stats
        assert "by_type" in stats
        assert "avg_confidence" in stats
        assert "confidence_distribution" in stats
        assert "match_quality" in stats
        assert "inferred_relations" in stats

    def test_dedup_removed_in_stats(self, sample_source_text):
        """Stats should include dedup_removed count."""
        # Create two overlapping extractions
        extractions = [
            {"type": "entity", "text": "public class MGMultiGateSolver"},
            {"type": "entity", "text": "class MGMultiGateSolver"},  # overlaps
        ]
        pipeline = ExtractionPipeline(sample_source_text)
        result = pipeline.process(extractions)

        assert "dedup_removed" in result["stats"]
        assert isinstance(result["stats"]["dedup_removed"], int)

    def test_custom_config(self, sample_source_text, sample_extractions):
        config = {
            "source_grounding": True,
            "overlap_dedup": False,
            "confidence_scoring": True,
            "entity_resolution": False,
            "relation_inference": False,
            "kg_injection": False,
        }
        pipeline = ExtractionPipeline(sample_source_text, config=config)
        result = pipeline.process(sample_extractions)
        # All items should be preserved since dedup is off
        assert len(result["extractions"]) == len(sample_extractions)

    def test_with_entity_resolution(self, sample_source_text):
        extractions = [
            {"type": "entity", "text": "MGMultiGateSolver"},
            {"type": "entity", "text": "MGMultiGateSolver"},
        ]
        config = {"entity_resolution": True}
        pipeline = ExtractionPipeline(sample_source_text, config=config)
        result = pipeline.process(extractions)
        entities = [e for e in result["extractions"] if e.get("type") == "entity"]
        assert len(entities) == 1

    def test_with_relation_inference(self, sample_source_text):
        extractions = [
            {"type": "rule", "text": "if (cmd == null) { Debug.LogError(\"cmd is null\"); return; }"},
            {"type": "entity", "text": "public class MGMultiGateSolver"},
        ]
        config = {"relation_inference": True}
        pipeline = ExtractionPipeline(sample_source_text, config=config)
        result = pipeline.process(extractions)
        assert "inferred_relations" in result

    def test_with_kg_injection(self, sample_source_text, sample_extractions):
        config = {"kg_injection": True}
        pipeline = ExtractionPipeline(sample_source_text, config=config)
        result = pipeline.process(sample_extractions)
        assert result["kg_format"] is not None
        assert "entities" in result["kg_format"]
        assert "relations" in result["kg_format"]

    def test_kg_injection_disabled_by_default(self, sample_source_text, sample_extractions):
        pipeline = ExtractionPipeline(sample_source_text)
        result = pipeline.process(sample_extractions)
        assert result["kg_format"] is None

    def test_source_file_injected(self, sample_source_text, sample_extractions):
        pipeline = ExtractionPipeline(sample_source_text, source_file="test.cs")
        result = pipeline.process(sample_extractions)
        for ext in result["extractions"]:
            assert ext.get("source_file") == "test.cs"

    def test_empty_input(self, sample_source_text):
        pipeline = ExtractionPipeline(sample_source_text)
        result = pipeline.process([])
        assert result["extractions"] == []
        assert result["stats"]["total_extractions"] == 0

    def test_configurable_confidence_weights(self, sample_source_text, sample_extractions):
        """Pipeline should accept confidence_weights config."""
        config = {
            "confidence_weights": {
                "match_quality": 1.0,
                "attr_completeness": 0.0,
                "text_specificity": 0.0,
                "type_consistency": 0.0,
            }
        }
        pipeline = ExtractionPipeline(sample_source_text, config=config)
        result = pipeline.process(sample_extractions)
        # Should run without error
        assert len(result["extractions"]) > 0
