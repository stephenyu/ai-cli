"""
Base provider interface for AI CLI.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel


class CommandOutput(BaseModel):
    """Standard response format for all providers."""
    command_line: str


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, credentials: Any = None):
        """
        Initialize the provider with credentials.

        Args:
            credentials: Provider-specific credentials (API key, config dict, etc.).
        """
        self.credentials = credentials

    @classmethod
    @abstractmethod
    def setup_interactive(cls) -> 'AIProvider':
        """
        Interactive setup for this provider.
        
        Returns:
            Configured provider instance.
            
        Raises:
            KeyboardInterrupt: If user cancels setup.
            APIKeyInvalidError: If credentials are invalid.
        """
        pass

    @classmethod
    @abstractmethod
    def get_provider_display_name(cls) -> str:
        """
        Get the display name of the provider for user prompts.

        Returns:
            The provider display name (e.g., "OpenAI", "Ollama").
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> None:
        """
        Validate the credentials by making a test call.

        Raises:
            APIKeyInvalidError: If the credentials are invalid.
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
            The provider name (e.g., "OpenAI", "Ollama").
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