"""Tests for the provider registry and provider-aware config helpers."""

import os
import pytest
from unittest.mock import patch

from ai_cli.config import (
    DEFAULT_PROVIDER,
    PROVIDER_CLAUDE,
    PROVIDER_OPENAI,
    PROVIDER_OPENROUTER,
    PROVIDERS,
    get_env_api_key,
    get_provider_spec,
)
from ai_cli.exceptions import UnknownProviderError


def test_default_provider_is_openai():
    assert DEFAULT_PROVIDER == PROVIDER_OPENAI


def test_providers_registry_has_all_three():
    assert set(PROVIDERS.keys()) == {PROVIDER_OPENAI, PROVIDER_CLAUDE, PROVIDER_OPENROUTER}


def test_get_provider_spec_known():
    spec = get_provider_spec(PROVIDER_CLAUDE)
    assert spec.name == PROVIDER_CLAUDE
    assert spec.env_var == "ANTHROPIC_API_KEY"
    assert spec.key_prefix == "sk-ant-"


def test_get_provider_spec_unknown_raises():
    with pytest.raises(UnknownProviderError):
        get_provider_spec("not-a-real-provider")


def test_get_env_api_key_defaults_to_openai():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-abc"}, clear=True):
        assert get_env_api_key() == "sk-abc"


def test_get_env_api_key_per_provider():
    with patch.dict(
        os.environ,
        {"ANTHROPIC_API_KEY": "sk-ant-abc", "OPENROUTER_API_KEY": "sk-or-abc"},
        clear=True,
    ):
        assert get_env_api_key(PROVIDER_CLAUDE) == "sk-ant-abc"
        assert get_env_api_key(PROVIDER_OPENROUTER) == "sk-or-abc"
        assert get_env_api_key(PROVIDER_OPENAI) is None
