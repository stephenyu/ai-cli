"""Active provider/model configuration storage for AI CLI."""

import json
from typing import Optional

from .config import CONFIG_DIR, CONFIG_FILE, DEFAULT_PROVIDER, get_provider_spec


class ProviderConfigManager:
    """Manages the on-disk record of which provider/model is active.

    This only ever stores non-secret state (provider name, model id). The
    API key itself lives in the keyring via APIKeyManager.
    """

    def _read(self) -> dict:
        if not CONFIG_FILE.exists():
            return {}
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}

    def has_config(self) -> bool:
        """Whether an active-provider config file exists."""
        return CONFIG_FILE.exists()

    def get_active_provider(self) -> str:
        """Get the currently active provider, defaulting to DEFAULT_PROVIDER."""
        return self._read().get("provider", DEFAULT_PROVIDER)

    def get_active_model(self, provider: Optional[str] = None) -> str:
        """
        Get the model configured for a provider.

        Args:
            provider: The provider to get the model for. Defaults to the
                currently active provider.

        Returns:
            The stored model for that provider if it's the active one,
            otherwise that provider's default model.
        """
        data = self._read()
        resolved_provider = provider or data.get("provider", DEFAULT_PROVIDER)
        stored_model = (
            data.get("model") if data.get("provider") == resolved_provider else None
        )
        return stored_model or get_provider_spec(resolved_provider).default_model

    def set_active(self, provider: str, model: str) -> None:
        """Persist the active provider and model."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps({"provider": provider, "model": model}, indent=2))

    def clear(self) -> None:
        """Remove the active-provider config file, if present."""
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
