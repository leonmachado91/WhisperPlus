"""Unit tests for whisperlivekit.metrics_collector — SessionMetrics computed properties."""

import json
import pytest
from whisperlivekit.metrics_collector import SessionMetrics


class TestSessionMetricsRTF:
    def test_rtf_zero_audio_duration(self):
        m = SessionMetrics(total_audio_duration_s=0.0, total_processing_time_s=5.0)
        assert m.rtf == 0.0

    def test_rtf_normal(self):
        m = SessionMetrics(total_audio_duration_s=10.0, total_processing_time_s=2.0)
        assert abs(m.rtf - 0.2) < 1e-6

    def test_rtf_realtime(self):
        # RTF = 1.0 means processing takes exactly as long as the audio
        m = SessionMetrics(total_audio_duration_s=5.0, total_processing_time_s=5.0)
        assert abs(m.rtf - 1.0) < 1e-6

    def test_rtf_faster_than_realtime(self):
        m = SessionMetrics(total_audio_duration_s=10.0, total_processing_time_s=1.0)
        assert m.rtf < 1.0


class TestSessionMetricsLatency:
    def test_avg_latency_empty(self):
        m = SessionMetrics()
        assert m.avg_latency_ms == 0.0

    def test_avg_latency_single_value(self):
        m = SessionMetrics(transcription_durations=[0.05])
        assert abs(m.avg_latency_ms - 50.0) < 1e-6

    def test_avg_latency_multiple_values(self):
        m = SessionMetrics(transcription_durations=[0.1, 0.2, 0.3])
        assert abs(m.avg_latency_ms - 200.0) < 1e-6  # avg = 0.2s = 200ms

    def test_p95_latency_empty(self):
        m = SessionMetrics()
        assert m.p95_latency_ms == 0.0

    def test_p95_latency_single_value(self):
        m = SessionMetrics(transcription_durations=[0.05])
        assert abs(m.p95_latency_ms - 50.0) < 1e-6

    def test_p95_latency_sorted_values(self):
        # 20 values from 0.01 to 0.20
        durations = [i * 0.01 for i in range(1, 21)]
        m = SessionMetrics(transcription_durations=durations)
        # 95th percentile index = int(20 * 0.95) = 19 → value 0.20
        assert m.p95_latency_ms == 200.0

    def test_p95_latency_with_outlier(self):
        durations = [0.05] * 19 + [2.0]  # One outlier
        m = SessionMetrics(transcription_durations=durations)
        assert m.p95_latency_ms == 2000.0  # The outlier IS the 95th percentile


class TestSessionMetricsToDict:
    def test_to_dict_is_json_serializable(self):
        m = SessionMetrics(
            session_start=1000.0,
            total_audio_duration_s=10.5,
            total_processing_time_s=2.1,
            n_chunks_received=100,
            n_transcription_calls=5,
            n_tokens_produced=50,
            n_responses_sent=5,
            transcription_durations=[0.1, 0.2, 0.3],
            n_silence_events=2,
            total_silence_duration_s=3.5,
        )
        d = m.to_dict()
        # Should not raise
        serialized = json.dumps(d)
        assert isinstance(serialized, str)

    def test_to_dict_has_expected_keys(self):
        m = SessionMetrics()
        d = m.to_dict()
        expected_keys = {
            "session_start", "total_audio_duration_s", "total_processing_time_s",
            "rtf", "n_chunks_received", "n_transcription_calls", "n_tokens_produced",
            "n_responses_sent", "avg_latency_ms", "p95_latency_ms",
            "n_silence_events", "total_silence_duration_s",
        }
        assert set(d.keys()) == expected_keys

    def test_to_dict_rounds_values(self):
        m = SessionMetrics(
            total_audio_duration_s=10.12345,
            total_processing_time_s=2.12345,
            transcription_durations=[0.12345],
            total_silence_duration_s=1.12345,
        )
        d = m.to_dict()
        assert d["total_audio_duration_s"] == 10.123
        assert d["total_processing_time_s"] == 2.123
        assert d["total_silence_duration_s"] == 1.123


class TestSessionMetricsDefaults:
    def test_default_values(self):
        m = SessionMetrics()
        assert m.session_start == 0.0
        assert m.total_audio_duration_s == 0.0
        assert m.n_chunks_received == 0
        assert m.transcription_durations == []
        assert m.n_silence_events == 0

    def test_separate_instances_have_independent_lists(self):
        m1 = SessionMetrics()
        m2 = SessionMetrics()
        m1.transcription_durations.append(1.0)
        assert len(m2.transcription_durations) == 0
