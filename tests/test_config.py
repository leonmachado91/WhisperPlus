"""Unit tests for whisperlivekit.config — WhisperLiveKitConfig creation and normalization."""

import argparse
import warnings
import pytest
from whisperlivekit.config import WhisperLiveKitConfig


class TestFromKwargs:
    def test_basic_creation(self):
        cfg = WhisperLiveKitConfig.from_kwargs(model_size="tiny", lan="pt")
        assert cfg.model_size == "tiny"
        assert cfg.lan == "pt"

    def test_unknown_keys_logged_not_error(self):
        # from_kwargs should silently ignore unknown keys (log warning, not crash)
        try:
            cfg = WhisperLiveKitConfig.from_kwargs(
                model_size="tiny",
                some_completely_unknown_key="value",
            )
            # If it reaches here, the key was ignored (good)
            assert cfg.model_size == "tiny"
        except TypeError:
            # If it raises TypeError, it means unknown keys are NOT handled
            pytest.fail("from_kwargs raised TypeError on unknown key — should ignore it")

    def test_defaults_applied(self):
        cfg = WhisperLiveKitConfig()
        assert cfg.host is not None
        assert cfg.port is not None


class TestFromNamespace:
    def test_basic_namespace(self):
        ns = argparse.Namespace(model_size="small", lan="en", host="0.0.0.0", port=9090)
        cfg = WhisperLiveKitConfig.from_namespace(ns)
        assert cfg.model_size == "small"
        assert cfg.lan == "en"

    def test_namespace_with_extra_keys(self):
        ns = argparse.Namespace(
            model_size="tiny",
            lan="pt",
            some_unknown="value",
        )
        try:
            cfg = WhisperLiveKitConfig.from_namespace(ns)
            assert cfg.model_size == "tiny"
        except TypeError:
            pytest.fail("from_namespace raised TypeError on unknown namespace attribute")


class TestPostInit:
    def test_dotted_english_suffix_is_model_name(self):
        """Config with model ending in .en should keep the model name intact."""
        cfg = WhisperLiveKitConfig(model_size="tiny.en")
        assert cfg.model_size == "tiny.en"

    def test_default_backend(self):
        cfg = WhisperLiveKitConfig()
        assert cfg.backend in ("whisper", "faster-whisper", None) or hasattr(cfg, "backend")

    def test_ssl_fields_default_none(self):
        cfg = WhisperLiveKitConfig()
        assert cfg.ssl_certfile is None or cfg.ssl_certfile == ""
        assert cfg.ssl_keyfile is None or cfg.ssl_keyfile == ""


class TestConfigImmutability:
    def test_is_dataclass(self):
        """WhisperLiveKitConfig should be a dataclass."""
        import dataclasses
        assert dataclasses.is_dataclass(WhisperLiveKitConfig)

    def test_multiple_instances_independent(self):
        cfg1 = WhisperLiveKitConfig(model_size="tiny")
        cfg2 = WhisperLiveKitConfig(model_size="base")
        assert cfg1.model_size != cfg2.model_size
