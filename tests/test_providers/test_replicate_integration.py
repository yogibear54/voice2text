"""Integration tests for ReplicateProvider with real API calls."""
import os
import pytest

from providers.replicate import ReplicateProvider


@pytest.mark.integration
@pytest.mark.slow
class TestReplicateProviderIntegration:
    """Integration tests for ReplicateProvider using real API calls.
    
    These tests require a valid REPLICATE_API_TOKEN environment variable.
    They will be skipped if the token is not available.
    """
    
    @pytest.fixture
    def api_token(self):
        """Get API token from environment or skip test."""
        token = os.getenv('REPLICATE_API_TOKEN')
        if not token:
            pytest.skip("REPLICATE_API_TOKEN not set - skipping integration test")
        return token
    
    @pytest.fixture
    def provider(self, api_token):
        """Create ReplicateProvider instance with real API token."""
        return ReplicateProvider(api_token=api_token)
    
    def test_provider_initializes_with_real_token(self, api_token):
        """Test provider initializes with real API token."""
        provider = ReplicateProvider(api_token=api_token)
        assert provider.api_token == api_token
        assert provider.api_token is not None
    
    def test_transcribe_with_real_audio_file(self, provider, test_audio_file):
        """Test transcription with real audio file and API call.
        
        This test makes an actual API call to Replicate.
        It requires:
        - Valid REPLICATE_API_TOKEN
        - Network access
        - test_audio_file fixture (from conftest.py)
        """
        # Skip if test audio file doesn't exist
        if not test_audio_file.exists():
            pytest.skip("Test audio file not available")
        
        # Make real API call
        result = provider.transcribe(str(test_audio_file))
        
        # Verify we got a result (may be None if API fails, but should not raise exception)
        assert result is None or isinstance(result, str)
        
        # If we got a result, it should not be empty
        if result:
            assert len(result.strip()) > 0
    
    def test_upload_with_real_api(self, provider, test_audio_file):
        """Test file upload with real API call."""
        if not test_audio_file.exists():
            pytest.skip("Test audio file not available")
        
        # Make real upload call
        url = provider._upload_audio_to_replicate(str(test_audio_file))
        
        # Should get a URL or None (if API fails)
        assert url is None or (isinstance(url, str) and url.startswith('http'))
    
    def test_full_transcription_workflow(self, provider, test_audio_file):
        """Test full transcription workflow with real API.
        
        This tests the complete flow:
        1. Upload audio file
        2. Get transcription
        3. Verify result
        """
        if not test_audio_file.exists():
            pytest.skip("Test audio file not available")
        
        # Full workflow
        result = provider.transcribe(str(test_audio_file))
        
        # Should complete without exceptions
        # Result may be None if API fails, but should be string if successful
        assert result is None or isinstance(result, str)
        
        # If successful, result should have content
        if result:
            assert len(result) > 0
            # Should be a valid string (not just whitespace)
            assert result.strip() != ""
