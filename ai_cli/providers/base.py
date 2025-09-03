"""
Base provider interface for AI CLI.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class CommandOutput(BaseModel):
    """Standard response format for all providers."""
    command_line: str


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str):
        """
        Initialize the provider with an API key.

        Args:
            api_key: The API key for the provider.
        """
        self.api_key = api_key

    @abstractmethod
    def validate_api_key(self) -> None:
        """
        Validate the API key by making a test call.

        Raises:
            APIKeyInvalidError: If the API key is invalid.
            ProviderAPIError: If there's an API error.
        """
        pass

    @abstractmethod
    def generate_command(
        self, 
        question: str, 
        system_info: str, 
        model: Optional[str] = None, 
        debug: bool = False
    ) -> str:
        """
        Convert a natural language question into a terminal command.

        Args:
            question: The user's natural language question.
            system_info: System information for context.
            model: The model to use (provider-specific).
            debug: Whether to show debug information.

        Returns:
            The generated terminal command.

        Raises:
            ProviderAPIError: If the API call fails.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the provider.

        Returns:
            The provider name (e.g., "OpenAI", "Claude").
        """
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """
        Get the default model for this provider.

        Returns:
            The default model name.
        """
        pass