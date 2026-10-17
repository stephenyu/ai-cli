"""
CLI commands for AI CLI.
"""

import sys
from typing import Optional

from .config import MESSAGES, PROVIDERS, get_env_api_key, get_provider_spec
from .api_key_manager import APIKeyManager
from .client_factory import create_client
from .provider_config import ProviderConfigManager
from .system_utils import SystemUtils
from .exceptions import (
    APIKeyNotFoundError,
    APIKeyInvalidError,
    ClipboardError,
    SystemInfoError,
    ProviderAPIError,
    UnknownProviderError,
)


class BaseCommand:
    """Base class for CLI commands."""

    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.system_utils = SystemUtils()
        self.provider_config_manager = ProviderConfigManager()


class SetupCommand(BaseCommand):
    """Handles the setup command for configuring a provider and its API key."""

    def execute(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """
        Execute the setup command.

        Args:
            provider: The provider to configure. If omitted, prompts
                interactively (or defaults to the currently active provider
                when an api_key is also passed, for non-interactive use).
            model: The model to use for that provider. If omitted, prompts
                interactively (or falls back to a default for non-interactive use).
            api_key: The API key to store. If omitted, prompts interactively.
                Passing this puts setup in non-interactive mode.
        """
        print(MESSAGES["setup_header"])
        print(MESSAGES["separator"])
        print()

        non_interactive = api_key is not None
        current_provider = self.provider_config_manager.get_active_provider()

        try:
            resolved_provider = self._resolve_provider(provider, current_provider, non_interactive)
        except UnknownProviderError as e:
            print(f"❌ {e}")
            return

        spec = get_provider_spec(resolved_provider)
        has_existing_key = bool(self.api_key_manager.get_api_key(resolved_provider))

        if not non_interactive and has_existing_key and resolved_provider == current_provider:
            print(f"✅ {spec.label} API key is already configured.")
            response = input("Would you like to update it? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Setup cancelled.")
                return
            print()

        try:
            if api_key is None:
                print(f"Please enter your {spec.label} API key.")
                print(f"You can find your API key at: {spec.key_url}")
                print()
                api_key = self.api_key_manager.prompt_for_api_key(resolved_provider)
            else:
                try:
                    self.api_key_manager.validate_api_key(api_key, resolved_provider)
                except APIKeyInvalidError as e:
                    print(f"⚠️  Warning: {e}")

            print()
            print(MESSAGES["testing_key"])

            # Test the API key
            try:
                client = create_client(resolved_provider, api_key)
                client.validate_api_key()
                print("✅ API key is valid!")
            except (APIKeyInvalidError, ProviderAPIError) as e:
                print(f"❌ API key test failed: {e}")
                if non_interactive:
                    print("Proceeding anyway (non-interactive mode).")
                else:
                    response = input("Store the key anyway? (y/N): ").strip().lower()
                    if response not in ['y', 'yes']:
                        print("Setup cancelled.")
                        return

            resolved_model = self._resolve_model(
                model, resolved_provider, current_provider, non_interactive, spec
            )

            print()
            print(MESSAGES["storing_key"])

            # Store the API key and active provider/model
            try:
                self.api_key_manager.store_api_key(api_key)
                self.provider_config_manager.set_active(resolved_provider, resolved_model)
                print("✅ API key stored securely in system keyring!")
                print(f"✅ Active provider set to {spec.label} (model: {resolved_model})")
                print()
                print(MESSAGES["setup_complete"])
                print(MESSAGES["example_usage"])
            except Exception as e:
                print(f"❌ Failed to store configuration: {e}")
                print(f"You can still use the {spec.env_var} environment variable as a fallback.")

        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            sys.exit(1)

    def _resolve_provider(
        self, provider: Optional[str], current_provider: str, non_interactive: bool
    ) -> str:
        """Resolve which provider to configure, prompting interactively if needed."""
        if provider is not None:
            get_provider_spec(provider)  # raises UnknownProviderError if invalid
            return provider

        if non_interactive:
            return current_provider

        print("Which AI provider would you like to use?")
        provider_ids = list(PROVIDERS.keys())
        for idx, pid in enumerate(provider_ids, start=1):
            marker = " (current)" if pid == current_provider else ""
            print(f"  {idx}. {PROVIDERS[pid].label}{marker}")

        default_idx = provider_ids.index(current_provider) + 1
        while True:
            choice = input(f"Choice [{default_idx}]: ").strip()
            if not choice:
                return current_provider
            if choice.isdigit() and 1 <= int(choice) <= len(provider_ids):
                return provider_ids[int(choice) - 1]
            if choice in provider_ids:
                return choice
            print("❌ Invalid choice, please try again.")

    def _resolve_model(
        self,
        model: Optional[str],
        resolved_provider: str,
        current_provider: str,
        non_interactive: bool,
        spec,
    ) -> str:
        """Resolve which model to use, prompting interactively if needed."""
        if model is not None:
            return model

        # Pre-fill with the currently configured model for this provider, if
        # we're re-running setup for the provider that's already active.
        default_model = (
            self.provider_config_manager.get_active_model(resolved_provider)
            if resolved_provider == current_provider
            else spec.default_model
        )

        if non_interactive:
            return default_model

        print()
        entered = input(f"Model to use [{default_model}]: ").strip()
        return entered or default_model


class StatusCommand(BaseCommand):
    """Handles the status command for showing configuration."""

    def execute(self) -> None:
        """Execute the status command. Reports configured state only — no live API call."""
        print(MESSAGES["status_header"])
        print(MESSAGES["separator"])
        print()

        provider = self.provider_config_manager.get_active_provider()
        spec = get_provider_spec(provider)
        model = self.provider_config_manager.get_active_model(provider)

        print(f"Provider: {spec.label}")
        print(f"Model: {model}")
        print()

        # Check keyring storage
        try:
            stored_key = self.api_key_manager.get_api_key(provider)
            if stored_key:
                masked_key = self.api_key_manager.get_masked_key(stored_key)
                print(f"✅ API Key (keyring): {masked_key}")
            else:
                print("❌ No API key found in keyring")
        except Exception:
            print("❌ Keyring not available")

        # Check environment variable
        env_key = get_env_api_key(provider)
        if env_key:
            masked_env_key = self.api_key_manager.get_masked_key(env_key)
            print(f"✅ API Key (env var {spec.env_var}): {masked_env_key}")
        else:
            print(f"❌ No {spec.env_var} environment variable")

        print()

        # Overall status
        final_key = self.api_key_manager.get_api_key(provider)
        if final_key:
            print("✅ AI CLI is ready to use!")
        else:
            print("❌ No API key configured. Run 'ai setup' to get started.")


class ResetCommand(BaseCommand):
    """Handles the reset command for removing the API key, provider and model."""

    def execute(self) -> None:
        """Execute the reset command."""
        print(MESSAGES["reset_header"])
        print(MESSAGES["separator"])
        print()

        existing_key = self.api_key_manager.get_api_key()
        has_config = self.provider_config_manager.has_config()
        if not existing_key and not has_config:
            print("❌ No configuration is currently set.")
            return

        print("⚠️  This will remove your stored API key and provider/model settings.")
        response = input("Are you sure? (y/N): ").strip().lower()

        if response in ['y', 'yes']:
            try:
                self.api_key_manager.remove_api_key()
            except Exception as e:
                print(f"⚠️  Could not remove API key from keyring: {e}")
            self.provider_config_manager.clear()
            print("✅ Configuration removed successfully.")
            print("Reset complete.")
        else:
            print("Reset cancelled.")


class QueryCommand(BaseCommand):
    """Handles the query command for generating terminal commands."""
    
    def execute(self, question: str, copy_to_clipboard: bool = False, model: str = None) -> None:
        """
        Execute the query command.

        Args:
            question: The user's question.
            copy_to_clipboard: Whether to copy the result to clipboard.
            model: The model to use. Defaults to the active provider's configured model.
        """
        try:
            # Get the active provider and its API key
            provider = self.provider_config_manager.get_active_provider()
            api_key = self.api_key_manager.ensure_api_key(provider)
            resolved_model = model or self.provider_config_manager.get_active_model(provider)

            # Get system information
            try:
                system_info = self.system_utils.get_system_info()
            except SystemInfoError:
                system_info = "Unknown system"

            # Initialize the active provider's client and get command
            client = create_client(provider, api_key)
            command = client.get_terminal_command(question, system_info, resolved_model)

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
        except ProviderAPIError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
            sys.exit(1) 