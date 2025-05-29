"""
CLI commands for AI CLI.
"""

import sys
from typing import Optional

from .config import MESSAGES, get_env_api_key
from .api_key_manager import APIKeyManager
from .system_utils import SystemUtils
from .openai_client import OpenAIClient
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


class SetupCommand(BaseCommand):
    """Handles the setup command for configuring API key."""
    
    def execute(self) -> None:
        """Execute the setup command."""
        print(MESSAGES["setup_header"])
        print(MESSAGES["separator"])
        print()
        
        # Check if key already exists
        existing_key = self.api_key_manager.get_api_key()
        if existing_key:
            print("✅ OpenAI API key is already configured.")
            response = input("Would you like to update it? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Setup cancelled.")
                return
            print()
        
        print(MESSAGES["api_key_prompt"])
        print(MESSAGES["api_key_url"])
        print()
        
        try:
            # Get API key from user
            api_key = self.api_key_manager.prompt_for_api_key()
            
            print()
            print(MESSAGES["testing_key"])
            
            # Test the API key
            client = OpenAIClient(api_key)
            try:
                client.validate_api_key()
                print("✅ API key is valid!")
            except (APIKeyInvalidError, OpenAIAPIError) as e:
                print(f"❌ API key test failed: {e}")
                response = input("Store the key anyway? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Setup cancelled.")
                    return
            
            print()
            print(MESSAGES["storing_key"])
            
            # Store the API key
            try:
                self.api_key_manager.store_api_key(api_key)
                print("✅ API key stored securely in system keyring!")
                print()
                print(MESSAGES["setup_complete"])
                print(MESSAGES["example_usage"])
            except Exception as e:
                print(f"❌ Failed to store API key securely: {e}")
                print("You can still use the OPENAI_API_KEY environment variable as a fallback.")
                
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            sys.exit(1)


class StatusCommand(BaseCommand):
    """Handles the status command for showing configuration."""
    
    def execute(self) -> None:
        """Execute the status command."""
        print(MESSAGES["status_header"])
        print(MESSAGES["separator"])
        print()
        
        # Check keyring storage
        try:
            stored_key = self.api_key_manager.get_api_key()
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
        
        print()
        
        # Overall status
        final_key = self.api_key_manager.get_api_key()
        if final_key:
            print("✅ AI CLI is ready to use!")
        else:
            print("❌ No API key configured. Run 'ai setup' to get started.")


class ResetCommand(BaseCommand):
    """Handles the reset command for removing API key."""
    
    def execute(self) -> None:
        """Execute the reset command."""
        print(MESSAGES["reset_header"])
        print(MESSAGES["separator"])
        print()
        
        existing_key = self.api_key_manager.get_api_key()
        if not existing_key:
            print("❌ No API key is currently configured.")
            return
        
        print("⚠️  This will remove your stored OpenAI API key.")
        response = input("Are you sure? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            try:
                self.api_key_manager.remove_api_key()
                print("✅ API key removed successfully.")
            except Exception as e:
                print(f"⚠️  Could not remove API key from keyring: {e}")
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
            model: The OpenAI model to use.
        """
        try:
            # Get API key
            api_key = self.api_key_manager.ensure_api_key()
            
            # Get system information
            try:
                system_info = self.system_utils.get_system_info()
            except SystemInfoError:
                system_info = "Unknown system"
            
            # Initialize OpenAI client and get command
            client = OpenAIClient(api_key)
            command = client.get_terminal_command(question, system_info, model)
            
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
        except OpenAIAPIError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
            sys.exit(1) 