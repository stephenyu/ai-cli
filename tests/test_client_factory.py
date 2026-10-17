"""Tests for the provider client factory."""

import pytest

from ai_cli.claude_client import ClaudeClient
from ai_cli.client_factory import create_client
from ai_cli.config import PROVIDER_CLAUDE, PROVIDER_OPENAI, PROVIDER_OPENROUTER
from ai_cli.exceptions import UnknownProviderError
from ai_cli.openai_client import OpenAIClient
from ai_cli.openrouter_client import OpenRouterClient


def test_create_client_openai():
    client = create_client(PROVIDER_OPENAI, "sk-test")
    assert isinstance(client, OpenAIClient)
    assert client.api_key == "sk-test"


def test_create_client_claude():
    client = create_client(PROVIDER_CLAUDE, "sk-ant-test")
    assert isinstance(client, ClaudeClient)


def test_create_client_openrouter():
    client = create_client(PROVIDER_OPENROUTER, "sk-or-test")
    assert isinstance(client, OpenRouterClient)


def test_create_client_unknown_provider_raises():
    with pytest.raises(UnknownProviderError):
        create_client("not-a-real-provider", "sk-test")
