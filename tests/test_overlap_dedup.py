"""Tests for overlap_dedup module."""

import pytest
from overlap_dedup import OverlapDeduplicator


def _make_ext(ext_type, text, start, end, **extra):
    """Helper to create a test extraction with location."""
    ext = {
        "type": ext_type,
        "text": text,
        "source_location": {"char_interval": [start, end], "line": 1},
    }
    ext.update(extra)
    return ext


class TestOverlapDeduplicator:
    """Tests for the OverlapDeduplicator class."""

    def test_no_overlap_keeps_all(self):
        dedup = OverlapDeduplicator()
        items = [
            _make_ext("entity", "aaa", 0, 10),
            _make_ext("entity", "bbb", 20, 30),
            _make_ext("entity", "ccc", 40, 50),
        ]
        result = dedup.process(items)
        assert len(result) == 3

    def test_full_overlap_removes_worse(self):
        dedup = OverlapDeduplicator()
        items = [
            _make_ext("entity", "short", 0, 10),
            _make_ext("entity", "longer text here", 0, 10, summary_cn="has summary"),
        ]
        result = dedup.process(items)
        assert len(result) == 1
        assert result[0]["text"] == "longer text here"

    def test_partial_overlap_above_threshold(self):
        dedup = OverlapDeduplicator(overlap_threshold=0.5)
        items = [
            _make_ext("entity", "abcdefgh", 0, 10),
            _make_ext("entity", "efghijkl", 4, 15),  # 6/10 = 60% overlap > 50%
        ]
        result = dedup.process(items)
        assert len(result) == 1

    def test_partial_overlap_below_threshold(self):
        dedup = OverlapDeduplicator(overlap_threshold=0.5)
        items = [
            _make_ext("entity", "abcdefgh", 0, 10),
            _make_ext("entity", "ijklmnop", 8, 20),  # only 2/10 overlap = 20%
        ]
        result = dedup.process(items)
        assert len(result) == 2

    def test_best_win_strategy(self):
        """Best-win: more attributes wins over first-come."""
        dedup = OverlapDeduplicator()
        items = [
            _make_ext("entity", "short", 0, 10),
            _make_ext("entity", "longer", 0, 10, summary_cn="summary", extra="val"),
        ]
        result = dedup.process(items)
        assert len(result) == 1
        assert "summary_cn" in result[0]

    def test_type_aware_mode_preserves_different_types(self):
        dedup = OverlapDeduplicator(type_aware=True)
        items = [
            _make_ext("entity", "same text", 0, 10),
            _make_ext("rule", "same text", 0, 10),
        ]
        result = dedup.process(items)
        assert len(result) == 2

    def test_type_aware_false_deduplicates_different_types(self):
        dedup = OverlapDeduplicator(type_aware=False)
        items = [
            _make_ext("entity", "same text", 0, 10),
            _make_ext("rule", "same text", 0, 10),
        ]
        result = dedup.process(items)
        assert len(result) == 1

    def test_no_location_preserved(self):
        dedup = OverlapDeduplicator()
        items = [
            {"type": "entity", "text": "no location"},
            _make_ext("entity", "has location", 0, 10),
        ]
        result = dedup.process(items)
        assert len(result) == 2

    def test_empty_input(self):
        dedup = OverlapDeduplicator()
        assert dedup.process([]) == []

    def test_single_item(self):
        dedup = OverlapDeduplicator()
        items = [_make_ext("entity", "only one", 0, 10)]
        result = dedup.process(items)
        assert len(result) == 1

    def test_null_interval_preserved(self):
        dedup = OverlapDeduplicator()
        items = [
            {"type": "entity", "text": "null interval", "source_location": {"char_interval": [None, None]}},
            _make_ext("entity", "valid", 0, 10),
        ]
        result = dedup.process(items)
        assert len(result) == 2

    def test_confidence_tiebreaker(self):
        """When attrs and length are equal, higher confidence wins."""
        dedup = OverlapDeduplicator()
        items = [
            {**_make_ext("entity", "same len!", 0, 10), "confidence": 0.5},
            {**_make_ext("entity", "same len!", 0, 10), "confidence": 0.9},
        ]
        result = dedup.process(items)
        assert len(result) == 1
        assert result[0]["confidence"] == 0.9
