"""Tests for configuration module."""

import os
import pytest
from unittest.mock import patch

from ai_cli.config import (
    DEFAULT_MODEL,
    KEYRING_SERVICE,
    KEYRING_USERNAME,
    OPENAI_KEY_PREFIX,
    CLIPBOARD_COMMANDS,
    get_env_api_key
)


def test_constants():
    """Test that configuration constants are properly defined."""
    assert DEFAULT_MODEL == "gpt-4.1-nano-2025-04-14"
    assert KEYRING_SERVICE == "ai-cli"
    assert KEYRING_USERNAME == "openai-api-key"
    assert OPENAI_KEY_PREFIX == "sk-"
    assert isinstance(CLIPBOARD_COMMANDS, dict)
    assert len(CLIPBOARD_COMMANDS) > 0


def test_get_env_api_key_exists():
    """Test getting API key from environment when it exists."""
    test_key = "sk-test123456789"
    with patch.dict(os.environ, {"OPENAI_API_KEY": test_key}):
        assert get_env_api_key() == test_key


def test_get_env_api_key_missing():
    """Test getting API key from environment when it doesn't exist."""
    with patch.dict(os.environ, {}, clear=True):
        assert get_env_api_key() is None


def test_clipboard_commands_structure():
    """Test that clipboard commands have the correct structure."""
    for tool, command in CLIPBOARD_COMMANDS.items():
        assert isinstance(tool, str)
        assert isinstance(command, list)
        assert len(command) > 0
        assert command[0] == tool 