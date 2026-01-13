"""Unit tests for ReplicateProvider with mocking."""
import os
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import requests

from providers.replicate import ReplicateProvider


@pytest.mark.unit
class TestReplicateProviderInitialization:
    """Test ReplicateProvider initialization."""
    
    def test_initializes_with_api_token(self, mock_api_token, mock_api_settings):
        """Test provider initializes with API token."""
        provider = ReplicateProvider(api_token=mock_api_token, api_settings=mock_api_settings)
        assert provider.api_token == mock_api_token
        assert provider.api_settings == mock_api_settings
    
    def test_initializes_with_env_token(self, mock_api_settings):
        """Test provider initializes with token from environment."""
        os.environ['REPLICATE_API_TOKEN'] = 'env_token_123'
        provider = ReplicateProvider(api_settings=mock_api_settings)
        assert provider.api_token == 'env_token_123'
        del os.environ['REPLICATE_API_TOKEN']
    
    def test_raises_error_without_token(self, mock_api_settings):
        """Test provider raises error without API token."""
        if 'REPLICATE_API_TOKEN' in os.environ:
            del os.environ['REPLICATE_API_TOKEN']
        
        with pytest.raises(ValueError, match="REPLICATE_API_TOKEN not found"):
            ReplicateProvider(api_token=None, api_settings=mock_api_settings)
    
    def test_uses_config_api_settings_by_default(self, mock_api_token):
        """Test provider uses config.API_SETTINGS by default."""
        provider = ReplicateProvider(api_token=mock_api_token)
        import config
        assert provider.api_settings == config.API_SETTINGS
    
    def test_accepts_custom_api_settings(self, mock_api_token, mock_api_settings):
        """Test provider accepts custom api_settings."""
        custom_settings = {'model': 'custom/model', 'task': 'translate'}
        provider = ReplicateProvider(api_token=mock_api_token, api_settings=custom_settings)
        assert provider.api_settings == custom_settings


@pytest.mark.unit
class TestReplicateProviderUpload:
    """Test ReplicateProvider file upload functionality."""
    
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    def test_upload_success_returns_url(self, mock_file, mock_post, replicate_provider, 
                                       mock_replicate_upload_response, test_audio_file):
        """Test successful file upload returns URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        url = replicate_provider._upload_audio_to_replicate(str(test_audio_file))
        
        assert url == 'https://replicate.delivery/test/audio.wav'
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://api.replicate.com/v1/files'
        assert 'Authorization' in call_args[1]['headers']
        assert call_args[1]['headers']['Authorization'] == f'Bearer {replicate_provider.api_token}'
    
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    def test_upload_handles_http_401_error(self, mock_file, mock_post, replicate_provider, test_audio_file):
        """Test upload handles 401 Unauthorized error."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'detail': 'Unauthorized'}
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        url = replicate_provider._upload_audio_to_replicate(str(test_audio_file))
        
        assert url is None
    
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    def test_upload_handles_http_404_error(self, mock_file, mock_post, replicate_provider, test_audio_file):
        """Test upload handles 404 Not Found error."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'detail': 'Not found'}
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        url = replicate_provider._upload_audio_to_replicate(str(test_audio_file))
        
        assert url is None
    
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    def test_upload_handles_http_500_error(self, mock_file, mock_post, replicate_provider, test_audio_file):
        """Test upload handles 500 Internal Server Error."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'detail': 'Internal server error'}
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        url = replicate_provider._upload_audio_to_replicate(str(test_audio_file))
        
        assert url is None
    
    @patch('providers.replicate.requests.post')
    def test_upload_handles_network_error(self, mock_post, replicate_provider, test_audio_file):
        """Test upload handles network errors."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")
        
        url = replicate_provider._upload_audio_to_replicate(str(test_audio_file))
        
        assert url is None
    
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    def test_upload_handles_missing_url_in_response(self, mock_file, mock_post, replicate_provider, test_audio_file):
        """Test upload handles missing URL in response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'urls': {}}  # No 'get' key
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        url = replicate_provider._upload_audio_to_replicate(str(test_audio_file))
        
        assert url is None
    
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    def test_upload_sends_correct_form_data(self, mock_file, mock_post, replicate_provider, test_audio_file):
        """Test upload sends correct form data."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'urls': {'get': 'http://test.url'}}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        replicate_provider._upload_audio_to_replicate(str(test_audio_file))
        
        call_args = mock_post.call_args
        assert 'files' in call_args[1]
        assert 'content' in call_args[1]['files']
        # Verify file tuple structure
        file_tuple = call_args[1]['files']['content']
        assert len(file_tuple) == 3
        assert file_tuple[2] == 'application/octet-stream'


@pytest.mark.unit
class TestReplicateProviderTranscription:
    """Test ReplicateProvider transcription functionality."""
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_string_response(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                       replicate_provider, test_audio_file, mock_replicate_upload_response,
                                       mock_replicate_transcribe_string):
        """Test transcription with string response."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.return_value = mock_replicate_transcribe_string
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result == mock_replicate_transcribe_string.strip()
        mock_replicate_run.assert_called_once()
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_dict_response_with_text_key(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                                    replicate_provider, test_audio_file, 
                                                    mock_replicate_upload_response, mock_replicate_transcribe_dict):
        """Test transcription with dict response containing 'text' key."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.return_value = mock_replicate_transcribe_dict
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result == mock_replicate_transcribe_dict['text'].strip()
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_dict_response_without_text_key(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                                       replicate_provider, test_audio_file,
                                                       mock_replicate_upload_response):
        """Test transcription with dict response without 'text' key."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.return_value = {'other_key': 'test value'}
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result == 'test value'
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_list_response(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                     replicate_provider, test_audio_file, mock_replicate_upload_response,
                                     mock_replicate_transcribe_list):
        """Test transcription with list/iterable response."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.return_value = mock_replicate_transcribe_list
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result == ' '.join(mock_replicate_transcribe_list).strip()
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_empty_result(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                    replicate_provider, test_audio_file, mock_replicate_upload_response):
        """Test transcription with empty result."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.return_value = ""
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result is None
    
    @patch('os.path.exists')
    def test_transcribe_handles_missing_file(self, mock_exists, replicate_provider):
        """Test transcription handles missing file."""
        mock_exists.return_value = False
        
        result = replicate_provider.transcribe('nonexistent.wav')
        
        assert result is None
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_passes_correct_parameters(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                                  replicate_provider, test_audio_file, mock_replicate_upload_response,
                                                  mock_replicate_transcribe_string):
        """Test transcription passes correct model and parameters to replicate.run."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.return_value = mock_replicate_transcribe_string
        
        replicate_provider.transcribe(str(test_audio_file))
        
        call_args = mock_replicate_run.call_args
        assert call_args[0][0] == replicate_provider.api_settings['model']
        assert 'input' in call_args[1]
        input_params = call_args[1]['input']
        assert input_params['task'] == replicate_provider.api_settings['task']
        assert input_params['language'] == replicate_provider.api_settings['language']
        assert input_params['timestamp'] == replicate_provider.api_settings['timestamp']
        assert input_params['batch_size'] == replicate_provider.api_settings['batch_size']
        assert input_params['diarise_audio'] == replicate_provider.api_settings['diarise_audio']


@pytest.mark.unit
class TestReplicateProviderErrorHandling:
    """Test ReplicateProvider error handling."""
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_handles_404_error(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                         replicate_provider, test_audio_file, mock_replicate_upload_response):
        """Test transcription handles 404 error."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.side_effect = Exception("404 Model not found")
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result is None
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_handles_rate_limit_error(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                                 replicate_provider, test_audio_file, mock_replicate_upload_response):
        """Test transcription handles rate limit error."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.side_effect = Exception("rate limit exceeded")
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result is None
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_handles_network_error(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                              replicate_provider, test_audio_file, mock_replicate_upload_response):
        """Test transcription handles network error."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.side_effect = Exception("network connection error")
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result is None
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake audio data')
    @patch('os.path.exists')
    def test_transcribe_handles_401_error(self, mock_exists, mock_file, mock_post, mock_replicate_run,
                                        replicate_provider, test_audio_file, mock_replicate_upload_response):
        """Test transcription handles 401 unauthorized error."""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json.return_value = mock_replicate_upload_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        mock_replicate_run.side_effect = Exception("401 unauthorized")
        
        result = replicate_provider.transcribe(str(test_audio_file))
        
        assert result is None
    
    @patch('providers.replicate.requests.post')
    def test_upload_returns_none_on_failure(self, mock_post, replicate_provider, test_audio_file):
        """Test upload returns None on failure (not exception)."""
        mock_post.side_effect = Exception("Upload failed")
        
        result = replicate_provider._upload_audio_to_replicate(str(test_audio_file))
        
        assert result is None
    
    @patch('providers.replicate.replicate.run')
    @patch('providers.replicate.requests.post')
    def test_transcribe_returns_none_on_failure(self, mock_post, mock_replicate_run, replicate_provider):
        """Test transcribe returns None on failure (not exception)."""
        mock_post.side_effect = Exception("Upload failed")
        
        result = replicate_provider.transcribe("test.wav")
        
        assert result is None
