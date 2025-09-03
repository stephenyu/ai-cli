"""
Configuration file manager for AI CLI.

Handles reading and writing the ~/.ai-cli.toml configuration file
for non-sensitive settings like provider selection and provider-specific configurations.
"""

import os
import toml
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """Manages the ~/.ai-cli.toml configuration file."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional path to config file (defaults to ~/.ai-cli.toml).
        """
        if config_path is None:
            self.config_path = Path.home() / ".ai-cli.toml"
        else:
            self.config_path = Path(config_path)
        
        self._config_cache: Optional[Dict[str, Any]] = None
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary. Empty dict if file doesn't exist.
        """
        if self._config_cache is not None:
            return self._config_cache
            
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self._config_cache = toml.load(f)
            else:
                self._config_cache = {}
        except Exception:
            # If config file is corrupted or unreadable, start with empty config
            self._config_cache = {}
            
        return self._config_cache
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save.
            
        Raises:
            Exception: If unable to save configuration.
        """
        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_path, 'w') as f:
                toml.dump(config, f)
            # Update cache
            self._config_cache = config.copy()
        except Exception as e:
            raise Exception(f"Could not save configuration to {self.config_path}: {e}")
    
    def get_provider(self) -> Optional[str]:
        """
        Get the currently selected provider.
        
        Returns:
            Provider name or None if not set.
        """
        config = self.load_config()
        return config.get("general", {}).get("provider")
    
    def set_provider(self, provider: str) -> None:
        """
        Set the currently selected provider.
        
        Args:
            provider: Provider name to set.
        """
        config = self.load_config()
        if "general" not in config:
            config["general"] = {}
        config["general"]["provider"] = provider
        self.save_config(config)
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider: Provider name.
            
        Returns:
            Provider configuration dictionary. Empty dict if not set.
        """
        config = self.load_config()
        return config.get(provider, {})
    
    def set_provider_config(self, provider: str, provider_config: Dict[str, Any]) -> None:
        """
        Set configuration for a specific provider.
        
        Args:
            provider: Provider name.
            provider_config: Configuration dictionary for the provider.
        """
        config = self.load_config()
        config[provider] = provider_config
        self.save_config(config)
    
    def get_provider_setting(self, provider: str, setting: str) -> Any:
        """
        Get a specific setting for a provider.
        
        Args:
            provider: Provider name.
            setting: Setting name.
            
        Returns:
            Setting value or None if not found.
        """
        provider_config = self.get_provider_config(provider)
        return provider_config.get(setting)
    
    def set_provider_setting(self, provider: str, setting: str, value: Any) -> None:
        """
        Set a specific setting for a provider.
        
        Args:
            provider: Provider name.
            setting: Setting name.
            value: Setting value.
        """
        config = self.load_config()
        if provider not in config:
            config[provider] = {}
        config[provider][setting] = value
        self.save_config(config)
    
    def remove_provider_config(self, provider: str) -> None:
        """
        Remove all configuration for a specific provider.
        
        Args:
            provider: Provider name.
        """
        config = self.load_config()
        if provider in config:
            del config[provider]
            self.save_config(config)
    
    def reset_config(self) -> None:
        """Remove the configuration file entirely."""
        if self.config_path.exists():
            self.config_path.unlink()
        self._config_cache = {}
    
    def config_exists(self) -> bool:
        """
        Check if configuration file exists.
        
        Returns:
            True if config file exists, False otherwise.
        """
        return self.config_path.exists()
    
    def get_config_path(self) -> Path:
        """
        Get the path to the configuration file.
        
        Returns:
            Path to the configuration file.
        """
        return self.config_path