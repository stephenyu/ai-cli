"""Tests for ProviderConfigManager (active provider/model state file)."""

import pytest

from ai_cli.config import PROVIDER_CLAUDE, PROVIDER_OPENAI, get_provider_spec
from ai_cli.provider_config import ProviderConfigManager


@pytest.fixture
def manager(tmp_path, monkeypatch):
    """A ProviderConfigManager pointed at a throwaway config file."""
    config_dir = tmp_path / "ai-cli"
    config_file = config_dir / "config.json"
    monkeypatch.setattr("ai_cli.provider_config.CONFIG_DIR", config_dir)
    monkeypatch.setattr("ai_cli.provider_config.CONFIG_FILE", config_file)
    return ProviderConfigManager()


def test_defaults_when_no_config_file(manager):
    assert manager.has_config() is False
    assert manager.get_active_provider() == PROVIDER_OPENAI
    assert manager.get_active_model() == get_provider_spec(PROVIDER_OPENAI).default_model


def test_set_active_persists_provider_and_model(manager):
    manager.set_active(PROVIDER_CLAUDE, "claude-haiku-4-5-20251001")

    assert manager.has_config() is True
    assert manager.get_active_provider() == PROVIDER_CLAUDE
    assert manager.get_active_model() == "claude-haiku-4-5-20251001"


def test_get_active_model_falls_back_to_default_for_other_provider(manager):
    manager.set_active(PROVIDER_CLAUDE, "a-custom-claude-model")

    # Asking for openai's model while claude is active should NOT return
    # claude's stored model - it should fall back to openai's own default.
    assert manager.get_active_model(PROVIDER_OPENAI) == get_provider_spec(PROVIDER_OPENAI).default_model


def test_clear_removes_config_file(manager):
    manager.set_active(PROVIDER_CLAUDE, "some-model")
    assert manager.has_config() is True

    manager.clear()

    assert manager.has_config() is False
    assert manager.get_active_provider() == PROVIDER_OPENAI


def test_clear_when_nothing_configured_is_a_noop(manager):
    manager.clear()
    assert manager.has_config() is False
