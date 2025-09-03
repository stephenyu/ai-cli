"""
Provider factory for AI CLI.
"""

from typing import Dict, Type, Optional

from .base import AIProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from ..exceptions import AICliError


class UnsupportedProviderError(AICliError):
    """Raised when an unsupported provider is requested."""
    pass


class ProviderFactory:
    """Factory for creating AI provider instances."""

    # Registry of available providers
    _providers: Dict[str, Type[AIProvider]] = {
        'openai': OpenAIProvider,
        'ollama': OllamaProvider,
    }

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        Get list of available provider names.

        Returns:
            List of provider names.
        """
        return list(cls._providers.keys())

    @classmethod
    def create_provider(cls, provider_name: str, credentials) -> AIProvider:
        """
        Create a provider instance.

        Args:
            provider_name: Name of the provider (e.g., 'openai').
            credentials: Credentials for the provider (API key, config dict, etc.).

        Returns:
            Provider instance.

        Raises:
            UnsupportedProviderError: If provider is not supported.
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available = ', '.join(cls.get_available_providers())
            raise UnsupportedProviderError(
                f"Unsupported provider '{provider_name}'. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_name]
        return provider_class(credentials)

    @classmethod
    def get_provider_class(cls, provider_name: str) -> Type[AIProvider]:
        """
        Get a provider class (not instance).

        Args:
            provider_name: Name of the provider (e.g., 'openai').

        Returns:
            Provider class.

        Raises:
            UnsupportedProviderError: If provider is not supported.
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available = ', '.join(cls.get_available_providers())
            raise UnsupportedProviderError(
                f"Unsupported provider '{provider_name}'. "
                f"Available providers: {available}"
            )

        return cls._providers[provider_name]

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIProvider]) -> None:
        """
        Register a new provider.

        Args:
            name: Provider name.
            provider_class: Provider class.
        """
        cls._providers[name.lower()] = provider_class


# Convenience functions
def create_provider(provider_name: str, credentials) -> AIProvider:
    """
    Create a provider instance.

    Args:
        provider_name: Name of the provider (e.g., 'openai').
        credentials: Credentials for the provider (API key, config dict, etc.).

    Returns:
        Provider instance.

    Raises:
        UnsupportedProviderError: If provider is not supported.
    """
    return ProviderFactory.create_provider(provider_name, credentials)


def get_provider_class(provider_name: str) -> Type[AIProvider]:
    """
    Get a provider class (not instance).

    Args:
        provider_name: Name of the provider (e.g., 'openai').

    Returns:
        Provider class.

    Raises:
        UnsupportedProviderError: If provider is not supported.
    """
    return ProviderFactory.get_provider_class(provider_name)