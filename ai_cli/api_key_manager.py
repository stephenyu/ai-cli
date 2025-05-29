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
    get_env_api_key
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