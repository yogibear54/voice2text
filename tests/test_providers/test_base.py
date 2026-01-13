"""Tests for the base TranscriptionProvider class."""
import pytest
from abc import ABC

from providers.base import TranscriptionProvider


@pytest.mark.unit
class TestTranscriptionProvider:
    """Test the abstract base class TranscriptionProvider."""
    
    def test_is_abstract_base_class(self):
        """Test that TranscriptionProvider is an abstract base class."""
        assert issubclass(TranscriptionProvider, ABC)
    
    def test_cannot_instantiate_base_class(self):
        """Test that TranscriptionProvider cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            TranscriptionProvider()
    
    def test_subclass_must_implement_transcribe(self):
        """Test that subclasses must implement transcribe method."""
        class IncompleteProvider(TranscriptionProvider):
            pass
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteProvider()
    
    def test_subclass_can_implement_transcribe(self):
        """Test that subclasses can be instantiated if they implement transcribe."""
        class CompleteProvider(TranscriptionProvider):
            def transcribe(self, audio_file_path: str):
                return "test transcription"
        
        provider = CompleteProvider()
        assert isinstance(provider, TranscriptionProvider)
        assert provider.transcribe("dummy") == "test transcription"
    
    def test_cleanup_is_optional(self):
        """Test that cleanup method has default implementation."""
        class ProviderWithTranscribe(TranscriptionProvider):
            def transcribe(self, audio_file_path: str):
                return "test"
        
        provider = ProviderWithTranscribe()
        # Should not raise an error
        provider.cleanup()
    
    def test_cleanup_can_be_overridden(self):
        """Test that subclasses can override cleanup method."""
        cleanup_called = []
        
        class ProviderWithCleanup(TranscriptionProvider):
            def transcribe(self, audio_file_path: str):
                return "test"
            
            def cleanup(self):
                cleanup_called.append(True)
        
        provider = ProviderWithCleanup()
        provider.cleanup()
        assert cleanup_called == [True]
    
    def test_transcribe_signature(self):
        """Test that transcribe method has correct signature."""
        import inspect
        
        sig = inspect.signature(TranscriptionProvider.transcribe)
        params = list(sig.parameters.keys())
        
        assert 'audio_file_path' in params
        assert len(params) == 1  # Only audio_file_path parameter
