"""
API key management for AI CLI.
"""

import getpass
import keyring
from typing import Optional

from .config import (
    KEYRING_SERVICE, 
    KEYRING_USERNAME, 
    OPENAI_KEY_PREFIX, 
    MIN_API_KEY_LENGTH,
    DEFAULT_PROVIDER,
    get_env_api_key,
    get_provider_config,
    get_provider_env_api_key
)
from .exceptions import APIKeyError, APIKeyNotFoundError, APIKeyInvalidError


class APIKeyManager:
    """Manages API key storage and retrieval."""
    
    def get_api_key(self) -> Optional[str]:
        """
        Get OpenAI API key from keyring first, then fall back to environment variable.
        
        Returns:
            The API key if found, None otherwise.
        """
        # Try to get from keyring first
        try:
            api_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if api_key:
                return api_key
        except Exception:
            # Keyring might not be available on some systems
            pass
        
        # Fall back to environment variable
        return get_env_api_key()
    
    def store_api_key(self, api_key: str) -> None:
        """
        Store OpenAI API key securely in the system keyring.
        
        Args:
            api_key: The API key to store.
            
        Raises:
            APIKeyError: If the key cannot be stored.
        """
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
        except Exception as e:
            raise APIKeyError(f"Error storing API key in keyring: {e}") from e
    
    def remove_api_key(self) -> None:
        """
        Remove the stored API key from the keyring.
        
        Raises:
            APIKeyError: If there's an error removing the key.
        """
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
        except keyring.errors.PasswordDeleteError:
            # Key might not exist, which is fine
            pass
        except Exception as e:
            raise APIKeyError(f"Error removing API key: {e}") from e
    
    def validate_api_key(self, api_key: str) -> None:
        """
        Validate API key format.
        
        Args:
            api_key: The API key to validate.
            
        Raises:
            APIKeyInvalidError: If the API key format is invalid.
        """
        if not api_key:
            raise APIKeyInvalidError("API key cannot be empty")
        
        if len(api_key) < MIN_API_KEY_LENGTH:
            raise APIKeyInvalidError(f"API key too short (minimum {MIN_API_KEY_LENGTH} characters)")
        
        if not api_key.startswith(OPENAI_KEY_PREFIX):
            raise APIKeyInvalidError(f"API key should start with '{OPENAI_KEY_PREFIX}'")
    
    def prompt_for_api_key(self) -> str:
        """
        Prompt user for API key input with validation.
        
        Returns:
            The validated API key.
            
        Raises:
            KeyboardInterrupt: If user cancels input.
        """
        while True:
            try:
                api_key = getpass.getpass("OpenAI API Key: ").strip()
                
                if not api_key:
                    print("❌ API key cannot be empty. Please try again.")
                    continue
                
                # Basic validation
                try:
                    self.validate_api_key(api_key)
                    return api_key
                except APIKeyInvalidError as e:
                    print(f"⚠️  Warning: {e}")
                    response = input("Continue anyway? (y/N): ").strip().lower()
                    if response in ['y', 'yes']:
                        return api_key
                    continue
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                raise
    
    def get_masked_key(self, api_key: str) -> str:
        """
        Return a masked version of the API key for display.
        
        Args:
            api_key: The API key to mask.
            
        Returns:
            Masked API key string.
        """
        if len(api_key) > 12:
            return f"{api_key[:8]}...{api_key[-4:]}"
        return "***"
    
    def ensure_api_key(self) -> str:
        """
        Ensure an API key is available, raising an exception if not.
        
        Returns:
            The API key.
            
        Raises:
            APIKeyNotFoundError: If no API key is configured.
        """
        api_key = self.get_api_key()
        if not api_key:
            raise APIKeyNotFoundError(
                "No OpenAI API key configured. "
                "Run 'ai setup' to configure your API key, or set the OPENAI_API_KEY environment variable."
            )
        return api_key

    # Provider-specific methods
    def get_provider_api_key(self, provider_name: str) -> Optional[str]:
        """
        Get API key for a specific provider from keyring first, then environment variable.
        
        Args:
            provider_name: Name of the provider.
            
        Returns:
            The API key if found, None otherwise.
        """
        try:
            config = get_provider_config(provider_name)
        except KeyError:
            # Provider not configured, fall back to legacy method for openai
            if provider_name.lower() == "openai":
                return self.get_api_key()
            return None

        # Try to get from provider-specific keyring first
        try:
            api_key = keyring.get_password(config["keyring_service"], config["keyring_username"])
            if api_key:
                return api_key
        except Exception:
            # Keyring might not be available on some systems
            pass
        
        # Fall back to provider-specific environment variable
        return get_provider_env_api_key(provider_name)

    def store_provider_api_key(self, provider_name: str, api_key: str) -> None:
        """
        Store API key for a specific provider securely in the system keyring.
        
        Args:
            provider_name: Name of the provider.
            api_key: The API key to store.
            
        Raises:
            APIKeyError: If the key cannot be stored.
        """
        try:
            config = get_provider_config(provider_name)
        except KeyError:
            # Provider not configured, fall back to legacy method for openai
            if provider_name.lower() == "openai":
                return self.store_api_key(api_key)
            raise APIKeyError(f"Provider '{provider_name}' not configured")

        try:
            keyring.set_password(config["keyring_service"], config["keyring_username"], api_key)
        except Exception as e:
            raise APIKeyError(f"Error storing {provider_name} API key in keyring: {e}") from e

    def remove_provider_api_key(self, provider_name: str) -> None:
        """
        Remove the stored API key for a specific provider from the keyring.
        
        Args:
            provider_name: Name of the provider.
            
        Raises:
            APIKeyError: If there's an error removing the key.
        """
        try:
            config = get_provider_config(provider_name)
        except KeyError:
            # Provider not configured, fall back to legacy method for openai
            if provider_name.lower() == "openai":
                return self.remove_api_key()
            raise APIKeyError(f"Provider '{provider_name}' not configured")

        try:
            keyring.delete_password(config["keyring_service"], config["keyring_username"])
        except keyring.errors.PasswordDeleteError:
            # Key might not exist, which is fine
            pass
        except Exception as e:
            raise APIKeyError(f"Error removing {provider_name} API key: {e}") from e

    def ensure_provider_api_key(self, provider_name: str) -> str:
        """
        Ensure an API key is available for a specific provider.
        
        Args:
            provider_name: Name of the provider.
            
        Returns:
            The API key.
            
        Raises:
            APIKeyNotFoundError: If no API key is configured.
        """
        api_key = self.get_provider_api_key(provider_name)
        if not api_key:
            try:
                config = get_provider_config(provider_name)
                env_var = config["env_var"]
            except KeyError:
                env_var = f"{provider_name.upper()}_API_KEY"
            
            raise APIKeyNotFoundError(
                f"No {provider_name} API key configured. "
                f"Run 'ai setup' to configure your API key, or set the {env_var} environment variable."
            )
        return api_key 