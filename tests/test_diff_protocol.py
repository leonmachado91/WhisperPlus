"""Unit tests for whisperlivekit.diff_protocol — DiffTracker snapshot/diff/prune."""

from unittest.mock import MagicMock
import pytest
from whisperlivekit.diff_protocol import DiffTracker


def _make_front_data(lines, buffer_transcription="", buffer_diarization="",
                     buffer_translation="", status="transcribing"):
    """Create a mock FrontData that returns a predictable dict."""
    fd = MagicMock()
    fd.to_dict.return_value = {
        "lines": lines,
        "buffer_transcription": buffer_transcription,
        "buffer_diarization": buffer_diarization,
        "buffer_translation": buffer_translation,
        "remaining_time_transcription": 0.0,
        "remaining_time_diarization": 0.0,
        "status": status,
    }
    return fd


class TestDiffTrackerSnapshot:
    def test_first_message_is_snapshot(self):
        tracker = DiffTracker()
        fd = _make_front_data([{"text": "hello", "speaker": 1}])
        msg = tracker.to_message(fd)
        assert msg["type"] == "snapshot"
        assert msg["seq"] == 1
        assert "lines" in msg

    def test_snapshot_contains_full_state(self):
        tracker = DiffTracker()
        lines = [{"text": "line1"}, {"text": "line2"}]
        fd = _make_front_data(lines)
        msg = tracker.to_message(fd)
        assert msg["lines"] == lines
        assert "buffer_transcription" in msg


class TestDiffTrackerDiff:
    def test_second_message_is_diff(self):
        tracker = DiffTracker()
        fd1 = _make_front_data([{"text": "hello"}])
        tracker.to_message(fd1)  # snapshot

        fd2 = _make_front_data([{"text": "hello"}, {"text": "world"}])
        msg = tracker.to_message(fd2)
        assert msg["type"] == "diff"
        assert msg["seq"] == 2

    def test_diff_contains_only_new_lines(self):
        tracker = DiffTracker()
        line1 = {"text": "hello"}
        fd1 = _make_front_data([line1])
        tracker.to_message(fd1)

        line2 = {"text": "world"}
        fd2 = _make_front_data([line1, line2])
        msg = tracker.to_message(fd2)
        assert msg.get("new_lines") == [line2]
        assert "lines_pruned" not in msg

    def test_diff_no_change_produces_minimal_diff(self):
        tracker = DiffTracker()
        lines = [{"text": "hello"}]
        fd1 = _make_front_data(lines)
        tracker.to_message(fd1)

        fd2 = _make_front_data(lines)
        msg = tracker.to_message(fd2)
        assert msg["type"] == "diff"
        assert "new_lines" not in msg  # No new or changed lines
        assert "lines_pruned" not in msg

    def test_diff_with_changed_last_line(self):
        tracker = DiffTracker()
        fd1 = _make_front_data([{"text": "hel"}])
        tracker.to_message(fd1)

        fd2 = _make_front_data([{"text": "hello world"}])
        msg = tracker.to_message(fd2)
        assert msg["type"] == "diff"
        # The line changed, so it should appear in new_lines
        assert msg.get("new_lines") == [{"text": "hello world"}]

    def test_n_lines_field(self):
        tracker = DiffTracker()
        fd1 = _make_front_data([{"text": "a"}, {"text": "b"}])
        tracker.to_message(fd1)

        fd2 = _make_front_data([{"text": "a"}, {"text": "b"}, {"text": "c"}])
        msg = tracker.to_message(fd2)
        assert msg["n_lines"] == 3


class TestDiffTrackerPrune:
    def test_detects_front_pruning(self):
        tracker = DiffTracker()
        line_a = {"text": "a", "id": 1}
        line_b = {"text": "b", "id": 2}
        line_c = {"text": "c", "id": 3}

        fd1 = _make_front_data([line_a, line_b, line_c])
        tracker.to_message(fd1)

        # Remove first line (prune from front)
        fd2 = _make_front_data([line_b, line_c])
        msg = tracker.to_message(fd2)
        assert msg.get("lines_pruned") == 1

    def test_all_lines_pruned(self):
        tracker = DiffTracker()
        fd1 = _make_front_data([{"text": "old1"}, {"text": "old2"}])
        tracker.to_message(fd1)

        fd2 = _make_front_data([{"text": "completely_new"}])
        msg = tracker.to_message(fd2)
        # old1 and old2 not found → all prev pruned
        assert msg.get("lines_pruned") == 2

    def test_empty_lines_after_content(self):
        tracker = DiffTracker()
        fd1 = _make_front_data([{"text": "a"}, {"text": "b"}])
        tracker.to_message(fd1)

        fd2 = _make_front_data([])
        msg = tracker.to_message(fd2)
        assert msg.get("lines_pruned") == 2
        assert msg["n_lines"] == 0


class TestDiffTrackerReset:
    def test_reset_produces_new_snapshot(self):
        tracker = DiffTracker()
        fd1 = _make_front_data([{"text": "hello"}])
        tracker.to_message(fd1)
        assert tracker.seq == 1

        tracker.reset()

        fd2 = _make_front_data([{"text": "world"}])
        msg = tracker.to_message(fd2)
        assert msg["type"] == "snapshot"
        assert msg["seq"] == 1  # Seq reset to 0, then incremented to 1


class TestDiffTrackerSeqMonotonic:
    def test_seq_increments(self):
        tracker = DiffTracker()
        seqs = []
        for i in range(5):
            fd = _make_front_data([{"text": f"line_{i}"}])
            msg = tracker.to_message(fd)
            seqs.append(msg["seq"])
        assert seqs == [1, 2, 3, 4, 5]


class TestDiffTrackerErrorField:
    def test_error_included_when_present(self):
        tracker = DiffTracker()
        fd1 = _make_front_data([])
        tracker.to_message(fd1)  # snapshot

        fd2 = MagicMock()
        fd2.to_dict.return_value = {
            "lines": [],
            "buffer_transcription": "",
            "buffer_diarization": "",
            "buffer_translation": "",
            "remaining_time_transcription": 0.0,
            "remaining_time_diarization": 0.0,
            "status": "error",
            "error": "Model failed to load",
        }
        msg = tracker.to_message(fd2)
        assert msg["error"] == "Model failed to load"

    def test_error_omitted_when_absent(self):
        tracker = DiffTracker()
        fd1 = _make_front_data([])
        tracker.to_message(fd1)

        fd2 = _make_front_data([])
        msg = tracker.to_message(fd2)
        assert "error" not in msg
