"""
Custom exceptions for AI CLI.
"""


class AICliError(Exception):
    """Base exception for AI CLI errors."""
    pass


class APIKeyError(AICliError):
    """Raised when there are issues with the API key."""
    pass


class APIKeyNotFoundError(APIKeyError):
    """Raised when no API key is found."""
    pass


class APIKeyInvalidError(APIKeyError):
    """Raised when the API key is invalid."""
    pass


class ClipboardError(AICliError):
    """Raised when clipboard operations fail."""
    pass


class SystemInfoError(AICliError):
    """Raised when system information cannot be retrieved."""
    pass


class UnknownProviderError(AICliError):
    """Raised when a provider name isn't one of the registered providers."""
    pass


class ProviderAPIError(AICliError):
    """Raised when an AI provider's API call fails."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class OpenAIAPIError(ProviderAPIError):
    """Raised when OpenAI API calls fail."""
    pass


class ClaudeAPIError(ProviderAPIError):
    """Raised when Claude (Anthropic) API calls fail."""
    pass


class OpenRouterAPIError(ProviderAPIError):
    """Raised when OpenRouter API calls fail."""
    pass 