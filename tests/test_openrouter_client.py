"""Tests for the OpenRouter client."""

from unittest.mock import MagicMock, patch

import pytest

from ai_cli.exceptions import APIKeyInvalidError, OpenRouterAPIError
from ai_cli.openrouter_client import OPENROUTER_BASE_URL, OpenRouterClient


@patch("ai_cli.openrouter_client.OpenAI")
def test_client_uses_openrouter_base_url(mock_openai_cls):
    OpenRouterClient("sk-or-test")
    mock_openai_cls.assert_called_once_with(api_key="sk-or-test", base_url=OPENROUTER_BASE_URL)


@patch("ai_cli.openrouter_client.OpenAI")
def test_validate_api_key_success(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    client = OpenRouterClient("sk-or-test")
    client.validate_api_key()  # should not raise

    # /key is the authenticated endpoint - /models is public and would
    # validate nothing.
    mock_client.get.assert_called_once_with("/key", cast_to=dict)
    mock_client.models.list.assert_not_called()


@patch("ai_cli.openrouter_client.OpenAI")
def test_validate_api_key_invalid(mock_openai_cls):
    mock_client = MagicMock()
    mock_client.get.side_effect = Exception("Unauthorized request")
    mock_openai_cls.return_value = mock_client

    client = OpenRouterClient("sk-or-bad")
    with pytest.raises(APIKeyInvalidError):
        client.validate_api_key()


@patch("ai_cli.openrouter_client.OpenAI")
def test_get_terminal_command_success(mock_openai_cls):
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "find . -name '*.py'"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_cls.return_value = mock_client

    client = OpenRouterClient("sk-or-test")
    command = client.get_terminal_command(
        "find python files", "Darwin", "anthropic/claude-3.5-haiku"
    )

    assert command == "find . -name '*.py'"
    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "anthropic/claude-3.5-haiku"


@patch("ai_cli.openrouter_client.OpenAI")
def test_get_terminal_command_api_failure_wrapped(mock_openai_cls):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("boom")
    mock_openai_cls.return_value = mock_client

    client = OpenRouterClient("sk-or-test")
    with pytest.raises(OpenRouterAPIError, match="Error calling OpenRouter API"):
        client.get_terminal_command("do something", "Darwin", "anthropic/claude-3.5-haiku")
