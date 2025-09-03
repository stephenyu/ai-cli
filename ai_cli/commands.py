"""
CLI commands for AI CLI.
"""

import sys
from typing import Optional

from .config import MESSAGES, get_env_api_key, DEFAULT_PROVIDER, get_provider_config
from .config_manager import ConfigManager
from .api_key_manager import APIKeyManager
from .system_utils import SystemUtils
from .openai_client import OpenAIClient
from .providers import create_provider
from .providers.factory import UnsupportedProviderError, get_provider_class, ProviderFactory
from .exceptions import (
    APIKeyNotFoundError, 
    APIKeyInvalidError, 
    ClipboardError, 
    SystemInfoError,
    OpenAIAPIError
)


class BaseCommand:
    """Base class for CLI commands."""
    
    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.system_utils = SystemUtils()
        self.config_manager = ConfigManager()


class SetupCommand(BaseCommand):
    """Handles the setup command for configuring providers."""
    
    def execute(self, provider: str = None) -> None:
        """
        Execute the setup command.
        
        Args:
            provider: The AI provider to configure (optional).
        """
        print(MESSAGES["setup_header"])
        print(MESSAGES["separator"])
        print()
        
        try:
            # If no provider specified, ask user to choose
            if provider is None:
                provider = self._prompt_for_provider()
            
            # Get the provider class and run interactive setup
            provider_class = get_provider_class(provider)
            provider_name = provider_class.get_provider_display_name()
            
            # Check if configuration already exists
            if self._has_existing_config(provider):
                print(f"✅ {provider_name} is already configured.")
                response = input("Would you like to update it? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Setup cancelled.")
                    return
                print()
            
            # Run provider-specific interactive setup
            provider_instance = provider_class.setup_interactive()
            
            # Save provider selection to config file
            self.config_manager.set_provider(provider)
            
            # Save provider-specific settings to config file if applicable
            self._save_provider_settings(provider, provider_instance)
            
            print()
            print(MESSAGES["setup_complete"])
            print(MESSAGES["example_usage"])
            
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            sys.exit(1)
        except UnsupportedProviderError as e:
            print(f"❌ {e}")
            sys.exit(1)
    
    def _prompt_for_provider(self) -> str:
        """
        Prompt user to select a provider.
        
        Returns:
            Selected provider name.
        """
        available_providers = ProviderFactory.get_available_providers()
        
        print("Which AI provider would you like to use?")
        for i, provider in enumerate(available_providers, 1):
            provider_class = get_provider_class(provider)
            display_name = provider_class.get_provider_display_name()
            default_marker = " (default)" if provider == DEFAULT_PROVIDER else ""
            print(f"  {i}. {display_name} ({provider}){default_marker}")
        print()
        
        while True:
            choice = input(f"Enter choice (1-{len(available_providers)}) or provider name (default: {DEFAULT_PROVIDER}): ").strip().lower()
            
            # Handle default case
            if not choice:
                return DEFAULT_PROVIDER
            
            # Handle numeric choice
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_providers):
                    return available_providers[choice_num - 1]
                else:
                    print(f"❌ Please enter a number between 1 and {len(available_providers)}")
                    continue
            
            # Handle provider name
            if choice in available_providers:
                return choice
            
            # Handle invalid choice
            print(f"❌ Invalid choice. Available providers: {', '.join(available_providers)}")
    
    def _has_existing_config(self, provider: str) -> bool:
        """
        Check if provider already has configuration stored (not env vars).
        
        Args:
            provider: Provider name to check.
            
        Returns:
            True if configuration exists, False otherwise.
        """
        if provider.lower() == "ollama":
            # For Ollama, check config file only (no keyring)
            try:
                file_config = self.config_manager.get_provider_config("ollama")
                return bool(file_config)
            except Exception:
                return False
        else:
            try:
                # For other providers, check keyring only
                config = get_provider_config(provider)
                import keyring
                existing_key = keyring.get_password(config["keyring_service"], config["keyring_username"])
                return bool(existing_key)
            except Exception:
                return False
    
    def _save_provider_settings(self, provider: str, provider_instance) -> None:
        """
        Save provider-specific settings to config file.
        
        Args:
            provider: Provider name.
            provider_instance: Provider instance with configuration.
        """
        if provider.lower() == "ollama":
            # For Ollama, save URL and model to config file
            if hasattr(provider_instance, 'config'):
                ollama_config = {}
                if 'url' in provider_instance.config:
                    ollama_config['url'] = provider_instance.config['url']
                if 'model' in provider_instance.config:
                    ollama_config['model'] = provider_instance.config['model']
                
                if ollama_config:
                    self.config_manager.set_provider_config("ollama", ollama_config)
        
        elif provider.lower() == "openai":
            # For OpenAI, save default model if it's different from system default
            if hasattr(provider_instance, 'model'):
                openai_config = {'model': provider_instance.model}
                self.config_manager.set_provider_config("openai", openai_config)


class StatusCommand(BaseCommand):
    """Handles the status command for showing configuration."""
    
    def execute(self) -> None:
        """Execute the status command."""
        print(MESSAGES["status_header"])
        print(MESSAGES["separator"])
        print()
        
        # Get current provider from config
        current_provider = self.config_manager.get_provider() or DEFAULT_PROVIDER
        
        # Check provider-specific credentials/configuration
        self._check_provider_status(current_provider)
        
        print()
        
        # Check configuration file status
        if self.config_manager.config_exists():
            print("📁 Configuration file status:")
            if current_provider:
                print(f"   Selected provider: {current_provider}")
                
                # Show provider-specific settings
                provider_config = self.config_manager.get_provider_config(current_provider)
                if provider_config:
                    for key, value in provider_config.items():
                        print(f"   {current_provider}.{key}: {value}")
            else:
                print("   No provider selected")
            print()
        else:
            print("📁 No configuration file found")
            print()
        
        # Overall status
        if self._is_provider_ready(current_provider):
            print("✅ AI CLI is ready to use!")
        else:
            print("❌ No API key configured. Run 'ai setup' to get started.")
    
    def _check_provider_status(self, provider: str) -> None:
        """
        Check and display status for a specific provider.
        
        Args:
            provider: The provider name to check.
        """
        if provider.lower() == "openai":
            # Check keyring storage (using provider-specific method)
            try:
                stored_key = self.api_key_manager.get_provider_api_key(provider)
                if stored_key:
                    masked_key = self.api_key_manager.get_masked_key(stored_key)
                    print(f"✅ API Key (keyring): {masked_key}")
                else:
                    print("❌ No API key found in keyring")
            except Exception:
                print("❌ Keyring not available")
            
            # Check environment variable
            env_key = get_env_api_key()
            if env_key:
                masked_env_key = self.api_key_manager.get_masked_key(env_key)
                print(f"✅ API Key (env var): {masked_env_key}")
            else:
                print("❌ No OPENAI_API_KEY environment variable")
                
        elif provider.lower() == "ollama":
            # For Ollama, check configuration (no keyring storage)
            import json
            from .config import get_provider_config, get_provider_env_api_key
            
            has_config = False
            
            try:
                # Check config file first
                file_config = self.config_manager.get_provider_config("ollama")
                if file_config:
                    print("✅ Ollama configuration (config file):")
                    for key, value in file_config.items():
                        print(f"   {key}: {value}")
                    has_config = True
                
                # Check environment variable
                env_config = get_provider_env_api_key(provider)
                if env_config:
                    try:
                        env_data = json.loads(env_config)
                        if not has_config:
                            print("✅ Ollama configuration (env var):")
                            for key, value in env_data.items():
                                print(f"   {key}: {value}")
                        has_config = True
                    except json.JSONDecodeError:
                        config = get_provider_config(provider)
                        print(f"⚠️  Invalid {config['env_var']} format")
                
                if not has_config:
                    print("❌ No Ollama configuration found")
                
            except KeyError:
                print(f"❌ Provider '{provider}' not configured")
                
        else:
            # Generic provider check - look for API key
            try:
                stored_key = self.api_key_manager.get_provider_api_key(provider)
                if stored_key:
                    masked_key = self.api_key_manager.get_masked_key(stored_key)
                    print(f"✅ {provider.title()} API Key: {masked_key}")
                else:
                    print(f"❌ No {provider} API key found")
            except Exception:
                print(f"❌ Error checking {provider} configuration")
    
    def _is_provider_ready(self, provider: str) -> bool:
        """
        Check if a provider is ready to use.
        
        Args:
            provider: The provider name to check.
            
        Returns:
            True if the provider is configured and ready.
        """
        if provider.lower() == "openai":
            return bool(self.api_key_manager.get_provider_api_key(provider))
        elif provider.lower() == "ollama":
            # For Ollama, check if we have configuration (no keyring check)
            try:
                from .config import get_provider_env_api_key
                import json
                
                # Check config file
                file_config = self.config_manager.get_provider_config("ollama")
                if file_config:
                    return True
                
                # Check environment variable
                env_config = get_provider_env_api_key(provider)
                if env_config:
                    try:
                        json.loads(env_config)
                        return True
                    except json.JSONDecodeError:
                        pass
                
                return False
                
            except KeyError:
                return False
        else:
            # Generic provider check
            return bool(self.api_key_manager.get_provider_api_key(provider))


class ResetCommand(BaseCommand):
    """Handles the reset command for removing all provider configurations."""
    
    def execute(self) -> None:
        """Execute the reset command."""
        print(MESSAGES["reset_header"])
        print(MESSAGES["separator"])
        print()
        
        # Check for any existing configurations
        has_configs = False
        config_summary = []
        
        # Check each provider for existing configurations
        available_providers = ProviderFactory.get_available_providers()
        for provider in available_providers:
            if self._has_existing_config(provider):
                has_configs = True
                provider_class = get_provider_class(provider)
                display_name = provider_class.get_provider_display_name()
                config_summary.append(display_name)
        
        if not has_configs:
            print("❌ No provider configurations found.")
            return
        
        # Show what will be removed
        config_list = ", ".join(config_summary)
        print(f"⚠️  This will remove all stored provider configurations: {config_list}")
        response = input("Are you sure? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            removed_count = 0
            errors = []
            
            # Remove configurations for each provider
            for provider in available_providers:
                if self._has_existing_config(provider):
                    try:
                        self._remove_provider_config(provider)
                        provider_class = get_provider_class(provider)
                        display_name = provider_class.get_provider_display_name()
                        print(f"✅ {display_name} configuration removed successfully.")
                        removed_count += 1
                    except Exception as e:
                        provider_class = get_provider_class(provider)
                        display_name = provider_class.get_provider_display_name()
                        error_msg = f"Could not remove {display_name} configuration: {e}"
                        errors.append(error_msg)
                        print(f"⚠️  {error_msg}")
            
            # Also remove legacy OpenAI key if it exists
            try:
                self.api_key_manager.remove_api_key()
                print("✅ Legacy OpenAI configuration removed successfully.")
            except Exception:
                # Ignore errors for legacy key removal - it may not exist
                pass
            
            # Remove config file
            try:
                if self.config_manager.config_exists():
                    self.config_manager.reset_config()
                    print("✅ Configuration file removed successfully.")
            except Exception as e:
                print(f"⚠️  Could not remove configuration file: {e}")
            
            if removed_count > 0:
                print(f"🎉 Reset complete! Removed {removed_count} provider configuration(s).")
            
            if errors:
                print("\n⚠️  Some configurations could not be removed:")
                for error in errors:
                    print(f"   • {error}")
        else:
            print("Reset cancelled.")
    
    def _has_existing_config(self, provider: str) -> bool:
        """
        Check if provider already has configuration stored.
        
        Args:
            provider: Provider name to check.
            
        Returns:
            True if configuration exists, False otherwise.
        """
        if provider.lower() == "ollama":
            # For Ollama, check config file and environment variable only
            try:
                import json
                from .config import get_provider_env_api_key
                
                # Check config file
                file_config = self.config_manager.get_provider_config("ollama")
                if file_config:
                    return True
                
                # Check environment variable
                env_config = get_provider_env_api_key(provider)
                if env_config:
                    try:
                        json.loads(env_config)
                        return True
                    except json.JSONDecodeError:
                        pass
                
                return False
            except Exception:
                return False
        else:
            try:
                # Check if we can get existing credentials/config
                existing_key = self.api_key_manager.get_provider_api_key(provider)
                return bool(existing_key)
            except Exception:
                return False
    
    def _remove_provider_config(self, provider: str) -> None:
        """
        Remove configuration for a specific provider.
        
        Args:
            provider: Provider name.
            
        Raises:
            Exception: If removal fails.
        """
        config = get_provider_config(provider)
        
        if provider.lower() == "ollama":
            # For Ollama, remove from config file only
            # But also clean up any legacy keyring entries
            import keyring
            try:
                keyring.delete_password(config["keyring_service"], config["keyring_username"])
            except Exception:
                # If keyring deletion fails, it might not exist - that's OK
                pass
        else:
            # For other providers, remove from keyring
            import keyring
            try:
                keyring.delete_password(config["keyring_service"], config["keyring_username"])
            except Exception:
                # If keyring deletion fails, it might not exist - that's OK
                pass


class QueryCommand(BaseCommand):
    """Handles the query command for generating terminal commands."""
    
    def execute(self, question: str, copy_to_clipboard: bool = False, model: str = None, debug: bool = False, provider: str = None) -> None:
        """
        Execute the query command.
        
        Args:
            question: The user's question.
            copy_to_clipboard: Whether to copy the result to clipboard.
            model: The model to use.
            debug: Whether to show debug information.
            provider: The AI provider to use.
        """
        if provider is None:
            # Try to get provider from config file first, then fall back to default
            provider = self.config_manager.get_provider() or DEFAULT_PROVIDER
            
        try:
            # Get credentials for the provider
            credentials = self._get_provider_credentials(provider)
            
            # Get system information
            try:
                system_info = self.system_utils.get_system_info()
            except SystemInfoError:
                system_info = "Unknown system"
            
            # Create provider instance and get command
            ai_provider = create_provider(provider, credentials)
            command = ai_provider.generate_command(question, system_info, model, debug)
            
            # Output the command
            print(command)
            
            # Handle clipboard if requested
            if copy_to_clipboard:
                try:
                    self.system_utils.copy_to_clipboard(command)
                    print(MESSAGES["clipboard_success"], file=sys.stderr)
                except ClipboardError:
                    print(MESSAGES["clipboard_failed"], file=sys.stderr)
            
        except APIKeyNotFoundError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)
        except UnsupportedProviderError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)
        except OpenAIAPIError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _get_provider_credentials(self, provider: str):
        """
        Get credentials for the specified provider.
        
        Args:
            provider: Provider name.
            
        Returns:
            Provider-specific credentials.
            
        Raises:
            APIKeyNotFoundError: If no credentials are configured.
        """
        if provider.lower() == "openai":
            # For OpenAI, return API key directly
            return self.api_key_manager.ensure_provider_api_key(provider)
        elif provider.lower() == "ollama":
            # For Ollama, get config from config file or environment (no keyring)
            import json
            from .config import get_provider_config, get_provider_env_api_key
            
            try:
                config = get_provider_config(provider)
                
                # Try config file first
                file_config = self.config_manager.get_provider_config("ollama")
                if file_config:
                    return file_config
                
                # Fall back to environment variable
                env_config = get_provider_env_api_key(provider)
                if env_config:
                    return json.loads(env_config)
                
                # If nothing found, raise error
                raise APIKeyNotFoundError(
                    f"No {provider} configuration found. "
                    f"Run 'ai setup' to configure your provider, or set the {config['env_var']} environment variable."
                )
                
            except json.JSONDecodeError:
                raise APIKeyNotFoundError(f"Invalid {provider} configuration format.")
        else:
            # For other providers, use generic API key approach
            return self.api_key_manager.ensure_provider_api_key(provider) 