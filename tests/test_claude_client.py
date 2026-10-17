"""Tests for the Claude (Anthropic) client."""

from unittest.mock import MagicMock, patch

import pytest

from ai_cli.claude_client import ClaudeClient
from ai_cli.exceptions import APIKeyInvalidError, ClaudeAPIError


@patch("ai_cli.claude_client.anthropic.Anthropic")
def test_validate_api_key_success(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    client = ClaudeClient("sk-ant-test")
    client.validate_api_key()  # should not raise

    mock_client.models.list.assert_called_once()


@patch("ai_cli.claude_client.anthropic.Anthropic")
def test_validate_api_key_invalid(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.models.list.side_effect = Exception("authentication failed")
    mock_anthropic_cls.return_value = mock_client

    client = ClaudeClient("sk-ant-bad")
    with pytest.raises(APIKeyInvalidError):
        client.validate_api_key()


@patch("ai_cli.claude_client.anthropic.Anthropic")
def test_validate_api_key_other_error(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.models.list.side_effect = Exception("network timeout")
    mock_anthropic_cls.return_value = mock_client

    client = ClaudeClient("sk-ant-test")
    with pytest.raises(ClaudeAPIError):
        client.validate_api_key()


@patch("ai_cli.claude_client.anthropic.Anthropic")
def test_get_terminal_command_success(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_block = MagicMock()
    mock_block.text = "ls -ltu"
    mock_response = MagicMock()
    mock_response.content = [mock_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_client

    client = ClaudeClient("sk-ant-test")
    command = client.get_terminal_command("sort by last access", "Darwin", "claude-haiku-4-5-20251001")

    assert command == "ls -ltu"
    mock_client.messages.create.assert_called_once()
    _, kwargs = mock_client.messages.create.call_args
    assert kwargs["model"] == "claude-haiku-4-5-20251001"


@patch("ai_cli.claude_client.anthropic.Anthropic")
def test_get_terminal_command_empty_response_raises(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_block = MagicMock()
    mock_block.text = "   "
    mock_response = MagicMock()
    mock_response.content = [mock_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_client

    client = ClaudeClient("sk-ant-test")
    with pytest.raises(ClaudeAPIError, match="Empty command"):
        client.get_terminal_command("do nothing", "Darwin", "claude-haiku-4-5-20251001")


@patch("ai_cli.claude_client.anthropic.Anthropic")
def test_get_terminal_command_api_failure_wrapped(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("boom")
    mock_anthropic_cls.return_value = mock_client

    client = ClaudeClient("sk-ant-test")
    with pytest.raises(ClaudeAPIError, match="Error calling Claude API"):
        client.get_terminal_command("do something", "Darwin", "claude-haiku-4-5-20251001")
