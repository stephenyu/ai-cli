"""Tests for API key manager module."""

import pytest
from unittest.mock import patch, MagicMock

from ai_cli.api_key_manager import APIKeyManager
from ai_cli.exceptions import APIKeyError, APIKeyInvalidError, APIKeyNotFoundError


class TestAPIKeyManager:
    """Test cases for APIKeyManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = APIKeyManager()
    
    def test_validate_api_key_valid(self):
        """Test validation of a valid API key."""
        valid_key = "sk-1234567890123456789012345678901234567890"
        # Should not raise any exception
        self.manager.validate_api_key(valid_key)
    
    def test_validate_api_key_empty(self):
        """Test validation of empty API key."""
        with pytest.raises(APIKeyInvalidError, match="cannot be empty"):
            self.manager.validate_api_key("")
    
    def test_validate_api_key_too_short(self):
        """Test validation of too short API key."""
        with pytest.raises(APIKeyInvalidError, match="too short"):
            self.manager.validate_api_key("sk-123")
    
    def test_validate_api_key_wrong_prefix(self):
        """Test validation of API key with wrong prefix."""
        with pytest.raises(APIKeyInvalidError, match="should start with"):
            self.manager.validate_api_key("pk-1234567890123456789012345678901234567890")
    
    def test_get_masked_key_long(self):
        """Test masking of long API key."""
        key = "sk-1234567890123456789012345678901234567890"
        masked = self.manager.get_masked_key(key)
        assert masked == "sk-12345...7890"
    
    def test_get_masked_key_short(self):
        """Test masking of short API key."""
        key = "sk-123"
        masked = self.manager.get_masked_key(key)
        assert masked == "***"
    
    @patch('ai_cli.api_key_manager.keyring')
    @patch('ai_cli.api_key_manager.get_env_api_key')
    def test_get_api_key_from_keyring(self, mock_env, mock_keyring):
        """Test getting API key from keyring."""
        test_key = "sk-test123"
        mock_keyring.get_password.return_value = test_key
        mock_env.return_value = None
        
        result = self.manager.get_api_key()
        assert result == test_key
        mock_keyring.get_password.assert_called_once()
    
    @patch('ai_cli.api_key_manager.keyring')
    @patch('ai_cli.api_key_manager.get_env_api_key')
    def test_get_api_key_from_env(self, mock_env, mock_keyring):
        """Test getting API key from environment when keyring fails."""
        test_key = "sk-test123"
        mock_keyring.get_password.return_value = None
        mock_env.return_value = test_key
        
        result = self.manager.get_api_key()
        assert result == test_key
    
    @patch('ai_cli.api_key_manager.keyring')
    def test_store_api_key_success(self, mock_keyring):
        """Test successful API key storage."""
        test_key = "sk-test123"
        mock_keyring.set_password.return_value = None
        
        # Should not raise any exception
        self.manager.store_api_key(test_key)
        mock_keyring.set_password.assert_called_once()
    
    @patch('ai_cli.api_key_manager.keyring')
    def test_store_api_key_failure(self, mock_keyring):
        """Test API key storage failure."""
        test_key = "sk-test123"
        mock_keyring.set_password.side_effect = Exception("Keyring error")
        
        with pytest.raises(APIKeyError, match="Error storing API key"):
            self.manager.store_api_key(test_key)
    
    def test_ensure_api_key_found(self):
        """Test ensure_api_key when key is available."""
        test_key = "sk-test123"
        with patch.object(self.manager, 'get_api_key', return_value=test_key):
            result = self.manager.ensure_api_key()
            assert result == test_key
    
    def test_ensure_api_key_not_found(self):
        """Test ensure_api_key when no key is available."""
        with patch.object(self.manager, 'get_api_key', return_value=None):
            with pytest.raises(APIKeyNotFoundError):
                self.manager.ensure_api_key() 