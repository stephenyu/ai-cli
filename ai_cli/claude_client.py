"""Anthropic Claude API client for AI CLI."""

import anthropic

from .base_client import BaseAIClient
from .exceptions import APIKeyInvalidError, ClaudeAPIError
from .prompts import build_system_prompt

MAX_RESPONSE_TOKENS = 256


class ClaudeClient(BaseAIClient):
    """Handles Anthropic Claude API interactions."""

    def __init__(self, api_key: str):
        """
        Initialize the Claude client.

        Args:
            api_key: The Anthropic API key.
        """
        super().__init__(api_key)
        self.client = anthropic.Anthropic(api_key=api_key)

    def validate_api_key(self) -> None:
        """
        Validate the API key by making a test call.

        Raises:
            APIKeyInvalidError: If the API key is invalid.
            ClaudeAPIError: If there's an API error.
        """
        try:
            self.client.models.list()
        except Exception as e:
            if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                raise APIKeyInvalidError(f"Invalid API key: {e}") from e
            else:
                raise ClaudeAPIError(f"API validation error: {e}", e) from e

    def get_terminal_command(self, question: str, system_info: str, model: str) -> str:
        """
        Use Claude to convert a natural language question into a terminal command.

        Args:
            question: The user's natural language question.
            system_info: System information for context.
            model: The Claude model to use.

        Returns:
            The generated terminal command.

        Raises:
            ClaudeAPIError: If the API call fails.
        """
        system_prompt = build_system_prompt(system_info)

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=MAX_RESPONSE_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": question}],
            )

            command = response.content[0].text.strip()
            if not command:
                raise ClaudeAPIError("Empty command returned from API")

            return command

        except ClaudeAPIError:
            raise
        except Exception as e:
            raise ClaudeAPIError(f"Error calling Claude API: {e}", e) from e
