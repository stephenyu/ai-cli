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


class OpenAIAPIError(AICliError):
    """Raised when OpenAI API calls fail."""
    
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error 