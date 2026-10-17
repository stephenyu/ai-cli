"""Common interface implemented by every AI provider client."""

from abc import ABC, abstractmethod


class BaseAIClient(ABC):
    """Interface a provider client must implement to plug into ai-cli."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def validate_api_key(self) -> None:
        """Validate the API key by making a cheap test call."""
        raise NotImplementedError

    @abstractmethod
    def get_terminal_command(self, question: str, system_info: str, model: str) -> str:
        """Convert a natural language question into a terminal command."""
        raise NotImplementedError
