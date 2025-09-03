"""
Tests for AI provider system.
"""

import pytest
from unittest.mock import Mock, patch

from ai_cli.providers.base import AIProvider
from ai_cli.providers.factory import ProviderFactory, UnsupportedProviderError, create_provider
from ai_cli.providers.openai_provider import OpenAIProvider
from ai_cli.exceptions import APIKeyInvalidError, OpenAIAPIError


class TestProviderFactory:
    """Tests for ProviderFactory."""
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        providers = ProviderFactory.get_available_providers()
        assert isinstance(providers, list)
        assert 'openai' in providers
    
    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = ProviderFactory.create_provider('openai', 'test-key')
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == 'test-key'
    
    def test_create_provider_case_insensitive(self):
        """Test provider creation is case insensitive."""
        provider = ProviderFactory.create_provider('OPENAI', 'test-key')
        assert isinstance(provider, OpenAIProvider)
    
    def test_create_unsupported_provider(self):
        """Test creating unsupported provider raises error."""
        with pytest.raises(UnsupportedProviderError) as exc_info:
            ProviderFactory.create_provider('unsupported', 'test-key')
        
        assert "Unsupported provider 'unsupported'" in str(exc_info.value)
        assert "Available providers: openai" in str(exc_info.value)
    
    def test_register_provider(self):
        """Test registering a new provider."""
        class TestProvider(AIProvider):
            def validate_api_key(self):
                pass
            
            def generate_command(self, question, system_info, model=None, debug=False):
                return "test command"
            
            def get_provider_name(self):
                return "Test"
            
            def get_default_model(self):
                return "test-model"
        
        # Register the provider
        ProviderFactory.register_provider('test', TestProvider)
        
        # Test it's available
        assert 'test' in ProviderFactory.get_available_providers()
        
        # Test creation
        provider = ProviderFactory.create_provider('test', 'test-key')
        assert isinstance(provider, TestProvider)
        
        # Clean up
        del ProviderFactory._providers['test']
    
    def test_create_provider_convenience_function(self):
        """Test the convenience create_provider function."""
        provider = create_provider('openai', 'test-key')
        assert isinstance(provider, OpenAIProvider)


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""
    
    def test_init(self):
        """Test provider initialization."""
        provider = OpenAIProvider('test-key')
        assert provider.api_key == 'test-key'
        assert provider.get_provider_name() == 'OpenAI'
    
    def test_get_default_model(self):
        """Test getting default model."""
        provider = OpenAIProvider('test-key')
        default_model = provider.get_default_model()
        assert isinstance(default_model, str)
        assert len(default_model) > 0
    
    @patch('ai_cli.providers.openai_provider.OpenAI')
    def test_validate_api_key_success(self, mock_openai):
        """Test successful API key validation."""
        # Setup mock
        mock_client = Mock()
        mock_client.models.list.return_value = ['model1', 'model2']
        mock_openai.return_value = mock_client
        
        # Test
        provider = OpenAIProvider('test-key')
        provider.validate_api_key()  # Should not raise
        
        # Verify
        mock_client.models.list.assert_called_once()
    
    @patch('ai_cli.providers.openai_provider.OpenAI')
    def test_validate_api_key_invalid(self, mock_openai):
        """Test API key validation with invalid key."""
        # Setup mock
        mock_client = Mock()
        mock_client.models.list.side_effect = Exception("authentication failed")
        mock_openai.return_value = mock_client
        
        # Test
        provider = OpenAIProvider('test-key')
        with pytest.raises(APIKeyInvalidError):
            provider.validate_api_key()
    
    @patch('ai_cli.providers.openai_provider.OpenAI')
    def test_validate_api_key_api_error(self, mock_openai):
        """Test API key validation with API error."""
        # Setup mock
        mock_client = Mock()
        mock_client.models.list.side_effect = Exception("network error")
        mock_openai.return_value = mock_client
        
        # Test
        provider = OpenAIProvider('test-key')
        with pytest.raises(OpenAIAPIError):
            provider.validate_api_key()
    
    @patch('ai_cli.providers.openai_provider.OpenAI')
    def test_generate_command_success(self, mock_openai):
        """Test successful command generation."""
        # Setup mock
        mock_response = Mock()
        mock_response.output_parsed.command_line = "ls -la"
        
        mock_client = Mock()
        mock_client.responses.parse.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test
        provider = OpenAIProvider('test-key')
        command = provider.generate_command("list files", "macOS", "gpt-4")
        
        # Verify
        assert command == "ls -la"
        mock_client.responses.parse.assert_called_once()
    
    @patch('ai_cli.providers.openai_provider.OpenAI')
    def test_generate_command_empty_response(self, mock_openai):
        """Test command generation with empty response."""
        # Setup mock
        mock_response = Mock()
        mock_response.output_parsed.command_line = "   "  # Empty/whitespace
        
        mock_client = Mock()
        mock_client.responses.parse.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test
        provider = OpenAIProvider('test-key')
        with pytest.raises(OpenAIAPIError, match="Empty command returned"):
            provider.generate_command("list files", "macOS")
    
    @patch('ai_cli.providers.openai_provider.OpenAI')
    def test_generate_command_api_error(self, mock_openai):
        """Test command generation with API error."""
        # Setup mock
        mock_client = Mock()
        mock_client.responses.parse.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        
        # Test
        provider = OpenAIProvider('test-key')
        with pytest.raises(OpenAIAPIError):
            provider.generate_command("list files", "macOS")
    
    @patch('ai_cli.providers.openai_provider.OpenAI')
    def test_generate_command_uses_default_model(self, mock_openai):
        """Test command generation uses default model when none specified."""
        # Setup mock
        mock_response = Mock()
        mock_response.output_parsed.command_line = "ls -la"
        
        mock_client = Mock()
        mock_client.responses.parse.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test
        provider = OpenAIProvider('test-key')
        provider.generate_command("list files", "macOS")  # No model specified
        
        # Verify default model was used
        call_args = mock_client.responses.parse.call_args
        assert 'model' in call_args.kwargs
        assert call_args.kwargs['model'] == provider.get_default_model()