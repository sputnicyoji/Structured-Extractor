"""Tests for confidence_scorer module."""

import pytest
from confidence_scorer import ConfidenceScorer


class TestConfidenceScorer:
    """Tests for the ConfidenceScorer class."""

    def test_exact_match_high_confidence(self):
        scorer = ConfidenceScorer()
        extractions = [{
            "type": "rule",
            "text": "if condition then do action",
            "summary_cn": "条件判断规则",
            "condition": "满足条件",
            "action": "执行动作",
            "source_location": {"match_type": "exact"},
        }]
        result = scorer.process(extractions)
        assert result[0]["confidence"] >= 0.8

    def test_no_match_low_confidence(self):
        scorer = ConfidenceScorer()
        extractions = [{
            "type": "entity",
            "text": "x",
            "source_location": {"match_type": "none"},
        }]
        result = scorer.process(extractions)
        assert result[0]["confidence"] < 0.4

    def test_confidence_between_0_and_1(self):
        scorer = ConfidenceScorer()
        extractions = [
            {"type": "entity", "text": "a" * 500, "source_location": {"match_type": "exact"}},
            {"type": "entity", "text": "", "source_location": {"match_type": "none"}},
            {"type": "unknown_type", "text": "test", "source_location": {"match_type": "fuzzy"}},
        ]
        result = scorer.process(extractions)
        for item in result:
            assert 0.0 <= item["confidence"] <= 1.0

    def test_type_aware_attr_completeness_rule(self):
        """Rule with condition+action should score higher than rule without."""
        scorer = ConfidenceScorer()
        rule_complete = {
            "type": "rule",
            "text": "if x then y",
            "summary_cn": "完整规则",
            "condition": "x > 0",
            "action": "执行y",
            "source_location": {"match_type": "exact"},
        }
        rule_incomplete = {
            "type": "rule",
            "text": "if x then y",
            "summary_cn": "不完整规则",
            "source_location": {"match_type": "exact"},
        }
        result = scorer.process([rule_complete, rule_incomplete])
        assert result[0]["confidence"] > result[1]["confidence"]

    def test_type_aware_attr_completeness_event(self):
        """Event with event_type+direction should score higher."""
        scorer = ConfidenceScorer()
        event_complete = {
            "type": "event",
            "text": "OnClick event fires",
            "summary_cn": "点击事件",
            "event_type": "click",
            "direction": "publish",
            "source_location": {"match_type": "exact"},
        }
        event_incomplete = {
            "type": "event",
            "text": "OnClick event fires",
            "summary_cn": "点击事件",
            "source_location": {"match_type": "exact"},
        }
        result = scorer.process([event_complete, event_incomplete])
        assert result[0]["confidence"] > result[1]["confidence"]

    def test_type_consistency_correct_attrs(self):
        """Entity with entity_name+entity_kind should get high type_consistency."""
        scorer = ConfidenceScorer()
        correct = {
            "type": "entity",
            "text": "class Foo",
            "entity_name": "Foo",
            "entity_kind": "class",
            "source_location": {"match_type": "exact"},
        }
        wrong_attrs = {
            "type": "entity",
            "text": "class Foo",
            "condition": "x > 0",       # rule attribute on entity
            "action": "do something",    # rule attribute on entity
            "source_location": {"match_type": "exact"},
        }
        result = scorer.process([correct, wrong_attrs])
        assert result[0]["confidence"] > result[1]["confidence"]

    def test_custom_weights(self):
        """Custom weights should be applied."""
        # Weight match_quality to 100%
        scorer = ConfidenceScorer(weights={
            "match_quality": 1.0,
            "attr_completeness": 0.0,
            "text_specificity": 0.0,
            "type_consistency": 0.0,
        })
        exact = {"type": "entity", "text": "test", "source_location": {"match_type": "exact"}}
        fuzzy = {"type": "entity", "text": "test", "source_location": {"match_type": "fuzzy"}}
        result = scorer.process([exact, fuzzy])
        assert result[0]["confidence"] == 1.0
        assert result[1]["confidence"] == 0.6

    def test_text_specificity_optimal_range(self):
        scorer = ConfidenceScorer()
        optimal = {"type": "entity", "text": "a" * 50, "source_location": {"match_type": "exact"}}
        too_short = {"type": "entity", "text": "ab", "source_location": {"match_type": "exact"}}
        too_long = {"type": "entity", "text": "a" * 800, "source_location": {"match_type": "exact"}}

        result = scorer.process([optimal, too_short, too_long])
        assert result[0]["confidence"] > result[1]["confidence"]
        assert result[0]["confidence"] > result[2]["confidence"]

    def test_no_source_location(self):
        scorer = ConfidenceScorer()
        extractions = [{"type": "entity", "text": "no location info"}]
        result = scorer.process(extractions)
        assert "confidence" in result[0]
        assert result[0]["confidence"] >= 0.0

    def test_unknown_type_fallback(self):
        scorer = ConfidenceScorer()
        extractions = [{"type": "custom_type", "text": "some text", "source_location": {"match_type": "exact"}}]
        result = scorer.process(extractions)
        assert "confidence" in result[0]

    def test_preserves_original_fields(self):
        scorer = ConfidenceScorer()
        extractions = [{"type": "entity", "text": "test", "custom": "value"}]
        result = scorer.process(extractions)
        assert result[0]["custom"] == "value"

    def test_does_not_mutate_input(self):
        scorer = ConfidenceScorer()
        original = {"type": "entity", "text": "test"}
        scorer.process([original])
        assert "confidence" not in original
