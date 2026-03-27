"""Unit tests for TranscriptionFileExporter from server_with_export.py."""

import os
import sys
import tempfile
from unittest.mock import MagicMock

import pytest

# server_with_export.py uses parse_args() at module level which calls sys.argv.
# We need to patch sys.argv before importing, otherwise argparse will fail
# because pytest's arguments aren't valid for the server's parser.
# We do a targeted import of just the class.

@pytest.fixture
def exporter_class():
    """Import TranscriptionFileExporter without triggering the full server module init."""
    # We can't import server_with_export directly because it calls parse_args() at module level.
    # Instead, we extract the class source or use importlib tricks.
    # Simplest approach: add the project root and import with sys.argv patched.
    original_argv = sys.argv[:]
    sys.argv = ["test", "--model", "tiny"]
    try:
        # Force re-import if already cached
        if "server_with_export" in sys.modules:
            mod = sys.modules["server_with_export"]
        else:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "server_with_export",
                os.path.join(os.path.dirname(__file__), "..", "server_with_export.py"),
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules["server_with_export"] = mod
            spec.loader.exec_module(mod)
        yield mod.TranscriptionFileExporter
    finally:
        sys.argv = original_argv


def _make_response(lines=None, buffer_transcription="", buffer_diarization=""):
    """Create a mock response that mimics FrontData.to_dict()."""
    if lines is None:
        lines = []
    mock = MagicMock()
    mock.to_dict.return_value = {
        "lines": lines,
        "buffer_transcription": buffer_transcription,
        "buffer_diarization": buffer_diarization,
        "buffer_translation": "",
        "remaining_time_transcription": 0.0,
        "remaining_time_diarization": 0.0,
        "status": "transcribing",
    }
    return mock


class TestExporterCreation:
    def test_creates_file_on_init(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)
        assert os.path.exists(filepath)

    def test_file_has_header(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert content.startswith("# Transcription started at")

    def test_creates_parent_directories(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "subdir" / "deep" / "transcript.txt")
        exporter = exporter_class(filepath)
        assert os.path.exists(filepath)


class TestExporterProcessResponse:
    def test_writes_speaker_lines(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(lines=[
            {"text": "Olá mundo", "speaker": 0, "start": "0:00:01", "end": "0:00:03"},
        ])
        exporter.process_response(response)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert "Olá mundo" in content
        assert "Speaker 0" in content

    def test_skips_silence_segments(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(lines=[
            {"text": "Real speech", "speaker": 0, "start": "0:00:01", "end": "0:00:03"},
            {"text": "[silence]", "speaker": -2, "start": "0:00:03", "end": "0:00:05"},
            {"text": "More speech", "speaker": 1, "start": "0:00:05", "end": "0:00:07"},
        ])
        exporter.process_response(response)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert "Real speech" in content
        assert "More speech" in content
        assert "[silence]" not in content

    def test_skips_empty_text(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(lines=[
            {"text": "", "speaker": 0, "start": "0:00:01", "end": "0:00:03"},
            {"text": "   ", "speaker": 0, "start": "0:00:03", "end": "0:00:05"},
        ])
        exporter.process_response(response)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        # Only the header should be present, no speaker lines
        assert "Speaker 0" not in content

    def test_includes_buffer_text(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(
            lines=[{"text": "Hello", "speaker": 0, "start": "0:00:01", "end": "0:00:03"}],
            buffer_transcription="partial words being",
        )
        exporter.process_response(response)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert "[...processing...]" in content
        assert "partial words being" in content

    def test_no_buffer_when_empty(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(
            lines=[{"text": "Hello", "speaker": 0, "start": "0:00:01", "end": "0:00:03"}],
            buffer_transcription="",
        )
        exporter.process_response(response)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert "[...processing...]" not in content


class TestExporterOptimization:
    def test_identical_content_does_not_rewrite(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(lines=[
            {"text": "Same content", "speaker": 0, "start": "0:00:01", "end": "0:00:03"},
        ])

        # First write
        exporter.process_response(response)
        mtime1 = os.path.getmtime(filepath)

        # Force a small time difference
        import time
        time.sleep(0.05)

        # Second write with identical content — should be skipped
        exporter.process_response(response)
        mtime2 = os.path.getmtime(filepath)

        # File should NOT have been modified
        assert mtime1 == mtime2

    def test_different_content_triggers_rewrite(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        r1 = _make_response(lines=[
            {"text": "First", "speaker": 0, "start": "0:00:01", "end": "0:00:02"},
        ])
        exporter.process_response(r1)

        r2 = _make_response(lines=[
            {"text": "First", "speaker": 0, "start": "0:00:01", "end": "0:00:02"},
            {"text": "Second", "speaker": 1, "start": "0:00:02", "end": "0:00:04"},
        ])
        exporter.process_response(r2)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert "Second" in content


class TestExporterSpeakerLabels:
    def test_speaker_with_valid_id(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(lines=[
            {"text": "Hello", "speaker": 3, "start": "0:00:01", "end": "0:00:02"},
        ])
        exporter.process_response(response)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert "Speaker 3" in content

    def test_speaker_without_id(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(lines=[
            {"text": "Hello", "speaker": -1, "start": "0:00:01", "end": "0:00:02"},
        ])
        exporter.process_response(response)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert "Speaker ?" in content

    def test_timestamp_format_in_output(self, exporter_class, tmp_path):
        filepath = str(tmp_path / "transcript.txt")
        exporter = exporter_class(filepath)

        response = _make_response(lines=[
            {"text": "Test", "speaker": 0, "start": "0:01:30", "end": "0:01:35"},
        ])
        exporter.process_response(response)

        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        assert "0:01:30" in content
        assert "0:01:35" in content
