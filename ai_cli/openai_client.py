"""
OpenAI API client for AI CLI.

DEPRECATED: This module is kept for backwards compatibility.
Use the provider system (ai_cli.providers) for new code.
"""

import warnings
from typing import Optional

from .config import DEFAULT_MODEL
from .providers.openai_provider import OpenAIProvider


class OpenAIClient:
    """
    DEPRECATED: Legacy OpenAI client wrapper.
    
    This class is kept for backwards compatibility.
    New code should use the provider system instead.
    """

    def __init__(self, api_key: str):
        """
        Initialize the OpenAI client.

        Args:
            api_key: The OpenAI API key.
        """
        warnings.warn(
            "OpenAIClient is deprecated. Use the provider system (ai_cli.providers) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._provider = OpenAIProvider(api_key)

    def validate_api_key(self) -> None:
        """
        Validate the API key by making a test call.

        Raises:
            APIKeyInvalidError: If the API key is invalid.
            OpenAIAPIError: If there's an API error.
        """
        self._provider.validate_api_key()

    def get_terminal_command(self, question: str, system_info: str, model: str = DEFAULT_MODEL, debug: bool = False) -> str:
        """
        Use OpenAI to convert a natural language question into a terminal command.

        Args:
            question: The user's natural language question.
            system_info: System information for context.
            model: The OpenAI model to use.
            debug: Whether to show debug information.

        Returns:
            The generated terminal command.

        Raises:
            OpenAIAPIError: If the API call fails.
        """
        return self._provider.generate_command(question, system_info, model, debug)