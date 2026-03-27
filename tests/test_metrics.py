"""Unit tests for whisperlivekit.metrics — WER, normalize_text, timestamp accuracy."""

import pytest
from whisperlivekit.metrics import compute_wer, compute_timestamp_accuracy, normalize_text


# ───────────────────────── normalize_text ─────────────────────────

class TestNormalizeText:
    def test_lowercases(self):
        assert normalize_text("Hello WORLD") == "hello world"

    def test_strips_punctuation(self):
        assert normalize_text("Hello, world!") == "hello world"

    def test_collapses_whitespace(self):
        assert normalize_text("  hello   world  ") == "hello world"

    def test_preserves_hyphens_in_words(self):
        result = normalize_text("well-known")
        assert "well-known" in result

    def test_preserves_apostrophes(self):
        result = normalize_text("don't")
        assert "don't" in result

    def test_handles_unicode_accents(self):
        # Portuguese accented characters should be preserved after NFC normalization
        result = normalize_text("TRANSCRIÇÃO automática")
        assert "transcrição" in result

    def test_handles_empty_string(self):
        assert normalize_text("") == ""

    def test_handles_only_punctuation(self):
        assert normalize_text("!!!...???") == ""

    def test_handles_numbers(self):
        result = normalize_text("Item 42 costs $5")
        assert "42" in result
        assert "5" in result


# ───────────────────────── compute_wer ─────────────────────────

class TestComputeWER:
    def test_identical_strings(self):
        result = compute_wer("hello world", "hello world")
        assert result["wer"] == 0.0
        assert result["substitutions"] == 0
        assert result["insertions"] == 0
        assert result["deletions"] == 0

    def test_completely_different(self):
        result = compute_wer("hello world", "foo bar")
        assert result["wer"] == 1.0  # 2 substitutions / 2 ref words
        assert result["substitutions"] == 2

    def test_empty_reference_empty_hypothesis(self):
        result = compute_wer("", "")
        assert result["wer"] == 0.0
        assert result["ref_words"] == 0
        assert result["hyp_words"] == 0

    def test_empty_reference_nonempty_hypothesis(self):
        result = compute_wer("", "extra words here")
        assert result["wer"] == 3.0  # 3 insertions / 0 ref = float(m)
        assert result["insertions"] == 3

    def test_nonempty_reference_empty_hypothesis(self):
        result = compute_wer("hello world", "")
        assert result["wer"] == 1.0  # 2 deletions / 2 ref words
        assert result["deletions"] == 2

    def test_insertion(self):
        result = compute_wer("hello world", "hello beautiful world")
        assert result["insertions"] >= 1
        assert result["wer"] > 0.0

    def test_deletion(self):
        result = compute_wer("hello beautiful world", "hello world")
        assert result["deletions"] >= 1
        assert result["wer"] > 0.0

    def test_substitution(self):
        result = compute_wer("hello world", "hello earth")
        assert result["substitutions"] == 1
        assert result["wer"] == 0.5  # 1 sub / 2 ref words

    def test_case_insensitive(self):
        result = compute_wer("Hello World", "hello world")
        assert result["wer"] == 0.0

    def test_punctuation_ignored(self):
        result = compute_wer("Hello, world!", "hello world")
        assert result["wer"] == 0.0

    def test_portuguese_text(self):
        ref = "A transcrição automática funciona bem"
        hyp = "A transcrição automática funciona bem"
        result = compute_wer(ref, hyp)
        assert result["wer"] == 0.0

    def test_ref_words_and_hyp_words_counts(self):
        result = compute_wer("one two three", "one two three four five")
        assert result["ref_words"] == 3
        assert result["hyp_words"] == 5

    def test_wer_can_exceed_one(self):
        # More errors than reference words
        result = compute_wer("hello", "one two three four five")
        assert result["wer"] > 1.0


# ───────────────────────── compute_timestamp_accuracy ─────────────────────────

class TestComputeTimestampAccuracy:
    def test_empty_predicted(self):
        ref = [{"word": "hello", "start": 0.0, "end": 0.5}]
        result = compute_timestamp_accuracy([], ref)
        assert result["n_matched"] == 0
        assert result["mae_start"] is None

    def test_empty_reference(self):
        pred = [{"word": "hello", "start": 0.0, "end": 0.5}]
        result = compute_timestamp_accuracy(pred, [])
        assert result["n_matched"] == 0
        assert result["mae_start"] is None

    def test_both_empty(self):
        result = compute_timestamp_accuracy([], [])
        assert result["n_matched"] == 0

    def test_perfect_alignment(self):
        words = [
            {"word": "hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 0.5, "end": 1.0},
        ]
        result = compute_timestamp_accuracy(words, words)
        assert result["n_matched"] == 2
        assert result["mae_start"] == 0.0
        assert result["max_delta_start"] == 0.0

    def test_offset_alignment(self):
        pred = [
            {"word": "hello", "start": 0.1, "end": 0.6},
            {"word": "world", "start": 0.6, "end": 1.1},
        ]
        ref = [
            {"word": "hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 0.5, "end": 1.0},
        ]
        result = compute_timestamp_accuracy(pred, ref)
        assert result["n_matched"] == 2
        assert abs(result["mae_start"] - 0.1) < 1e-6

    def test_no_matching_words(self):
        pred = [{"word": "foo", "start": 0.0, "end": 0.5}]
        ref = [{"word": "bar", "start": 0.0, "end": 0.5}]
        result = compute_timestamp_accuracy(pred, ref)
        assert result["n_matched"] == 0
        assert result["mae_start"] is None

    def test_partial_match(self):
        pred = [
            {"word": "hello", "start": 0.0, "end": 0.5},
            {"word": "xyz", "start": 0.5, "end": 1.0},
            {"word": "world", "start": 1.0, "end": 1.5},
        ]
        ref = [
            {"word": "hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 0.5, "end": 1.0},
        ]
        result = compute_timestamp_accuracy(pred, ref)
        assert result["n_matched"] >= 1
        assert result["n_pred"] == 3
        assert result["n_ref"] == 2

    def test_case_insensitive_matching(self):
        pred = [{"word": "Hello", "start": 0.0, "end": 0.5}]
        ref = [{"word": "hello", "start": 0.0, "end": 0.5}]
        result = compute_timestamp_accuracy(pred, ref)
        assert result["n_matched"] == 1
