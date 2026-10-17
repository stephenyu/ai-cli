"""Tests for the provider-related behavior of the CLI commands."""

from unittest.mock import MagicMock, patch

import pytest

from ai_cli.commands import QueryCommand, ResetCommand, SetupCommand, StatusCommand
from ai_cli.config import get_provider_spec
from ai_cli.exceptions import APIKeyNotFoundError, ProviderAPIError


class TestSetupCommand:
    def test_non_interactive_full(self):
        cmd = SetupCommand()
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.get_api_key.return_value = None
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "openai"

        mock_client = MagicMock()
        api_key = "sk-ant-" + "x" * 40
        with patch("ai_cli.commands.create_client", return_value=mock_client):
            cmd.execute(provider="claude", model="claude-haiku-4-5-20251001", api_key=api_key)

        cmd.api_key_manager.store_api_key.assert_called_once_with(api_key)
        cmd.provider_config_manager.set_active.assert_called_once_with(
            "claude", "claude-haiku-4-5-20251001"
        )
        mock_client.validate_api_key.assert_called_once()

    def test_non_interactive_defaults_provider_and_model(self):
        cmd = SetupCommand()
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.get_api_key.return_value = None
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "openai"
        cmd.provider_config_manager.get_active_model.return_value = "gpt-4.1-nano-2025-04-14"

        mock_client = MagicMock()
        with patch("ai_cli.commands.create_client", return_value=mock_client):
            cmd.execute(api_key="sk-" + "x" * 40)

        cmd.provider_config_manager.set_active.assert_called_once_with(
            "openai", "gpt-4.1-nano-2025-04-14"
        )

    def test_non_interactive_proceeds_past_failed_live_validation(self):
        cmd = SetupCommand()
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.get_api_key.return_value = None
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "openai"
        cmd.provider_config_manager.get_active_model.return_value = "gpt-4.1-nano-2025-04-14"

        mock_client = MagicMock()
        mock_client.validate_api_key.side_effect = ProviderAPIError("network down")
        with patch("ai_cli.commands.create_client", return_value=mock_client):
            cmd.execute(api_key="sk-" + "x" * 40)

        # A failed live call should warn but not block storage in non-interactive mode.
        cmd.api_key_manager.store_api_key.assert_called_once()

    def test_interactive_cancel_when_declining_update(self, capsys):
        cmd = SetupCommand()
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.get_api_key.return_value = "sk-existing"
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "openai"

        # First input(): provider choice -> accept default. Second input():
        # "update existing key?" -> decline.
        with patch("builtins.input", side_effect=["", "n"]):
            cmd.execute()

        cmd.api_key_manager.store_api_key.assert_not_called()
        assert "Setup cancelled" in capsys.readouterr().out

    def test_unknown_provider_flag_is_rejected(self, capsys):
        cmd = SetupCommand()
        cmd.api_key_manager = MagicMock()
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "openai"

        cmd.execute(provider="not-a-real-provider", api_key="sk-test")

        cmd.api_key_manager.store_api_key.assert_not_called()
        assert "Unknown AI provider" in capsys.readouterr().out


class TestResolveModel:
    def test_prefills_with_current_config_for_same_provider(self):
        cmd = SetupCommand()
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_model.return_value = "gpt-4o-custom"
        spec = get_provider_spec("openai")

        with patch("builtins.input", return_value=""):
            result = cmd._resolve_model(None, "openai", "openai", False, spec)

        assert result == "gpt-4o-custom"
        cmd.provider_config_manager.get_active_model.assert_called_once_with("openai")

    def test_uses_spec_default_when_switching_provider(self):
        cmd = SetupCommand()
        cmd.provider_config_manager = MagicMock()
        spec = get_provider_spec("claude")

        with patch("builtins.input", return_value=""):
            result = cmd._resolve_model(None, "claude", "openai", False, spec)

        assert result == spec.default_model
        cmd.provider_config_manager.get_active_model.assert_not_called()

    def test_explicit_model_short_circuits(self):
        cmd = SetupCommand()
        cmd.provider_config_manager = MagicMock()
        spec = get_provider_spec("claude")

        result = cmd._resolve_model("custom-model", "claude", "openai", False, spec)

        assert result == "custom-model"
        cmd.provider_config_manager.get_active_model.assert_not_called()


class TestStatusCommand:
    def test_shows_active_provider_and_model(self, capsys):
        cmd = StatusCommand()
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "claude"
        cmd.provider_config_manager.get_active_model.return_value = "claude-haiku-4-5-20251001"
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.get_api_key.return_value = "sk-ant-abc"
        cmd.api_key_manager.get_masked_key.return_value = "sk-ant-ab...abcd"

        with patch("ai_cli.commands.get_env_api_key", return_value=None):
            cmd.execute()

        out = capsys.readouterr().out
        assert "Provider: Claude" in out
        assert "Model: claude-haiku-4-5-20251001" in out
        assert "AI CLI is ready to use!" in out

    def test_does_not_make_a_live_api_call(self):
        cmd = StatusCommand()
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "openai"
        cmd.provider_config_manager.get_active_model.return_value = "gpt-4.1-nano-2025-04-14"
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.get_api_key.return_value = "sk-abc"
        cmd.api_key_manager.get_masked_key.return_value = "sk-ab...abcd"

        with patch("ai_cli.commands.create_client") as mock_create, patch(
            "ai_cli.commands.get_env_api_key", return_value=None
        ):
            cmd.execute()

        mock_create.assert_not_called()


class TestResetCommand:
    def test_clears_key_and_config_on_confirm(self):
        cmd = ResetCommand()
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.get_api_key.return_value = "sk-abc"
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.has_config.return_value = True

        with patch("builtins.input", return_value="y"):
            cmd.execute()

        cmd.api_key_manager.remove_api_key.assert_called_once()
        cmd.provider_config_manager.clear.assert_called_once()

    def test_nothing_to_reset(self, capsys):
        cmd = ResetCommand()
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.get_api_key.return_value = None
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.has_config.return_value = False

        cmd.execute()

        cmd.provider_config_manager.clear.assert_not_called()
        assert "No configuration is currently set" in capsys.readouterr().out


class TestQueryCommand:
    def test_uses_active_provider_and_model(self):
        cmd = QueryCommand()
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "claude"
        cmd.provider_config_manager.get_active_model.return_value = "claude-haiku-4-5-20251001"
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.ensure_api_key.return_value = "sk-ant-abc"
        cmd.system_utils = MagicMock()
        cmd.system_utils.get_system_info.return_value = "Darwin test"

        mock_client = MagicMock()
        mock_client.get_terminal_command.return_value = "ls -la"

        with patch("ai_cli.commands.create_client", return_value=mock_client) as mock_create:
            cmd.execute("list files")

        cmd.api_key_manager.ensure_api_key.assert_called_once_with("claude")
        mock_create.assert_called_once_with("claude", "sk-ant-abc")
        mock_client.get_terminal_command.assert_called_once_with(
            "list files", "Darwin test", "claude-haiku-4-5-20251001"
        )

    def test_explicit_model_overrides_active_model(self):
        cmd = QueryCommand()
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "openai"
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.ensure_api_key.return_value = "sk-abc"
        cmd.system_utils = MagicMock()
        cmd.system_utils.get_system_info.return_value = "Darwin test"

        mock_client = MagicMock()
        mock_client.get_terminal_command.return_value = "ls -la"

        with patch("ai_cli.commands.create_client", return_value=mock_client):
            cmd.execute("list files", model="gpt-4o-override")

        cmd.provider_config_manager.get_active_model.assert_not_called()
        mock_client.get_terminal_command.assert_called_once_with(
            "list files", "Darwin test", "gpt-4o-override"
        )

    def test_exits_when_no_api_key_configured(self):
        cmd = QueryCommand()
        cmd.provider_config_manager = MagicMock()
        cmd.provider_config_manager.get_active_provider.return_value = "openai"
        cmd.api_key_manager = MagicMock()
        cmd.api_key_manager.ensure_api_key.side_effect = APIKeyNotFoundError("no key")

        with pytest.raises(SystemExit):
            cmd.execute("list files")
