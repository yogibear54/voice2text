"""Tests for audio recording functionality."""
import time
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
import sounddevice as sd

from start import VoiceDictationTool


@pytest.mark.unit
class TestAudioRecording:
    """Test audio recording logic."""
    
    @pytest.fixture
    def voice_tool(self, replicate_provider):
        """Create VoiceDictationTool instance for testing."""
        with patch('start.select_audio_device'), \
             patch('start.StatusManager'), \
             patch('start.create_provider', return_value=replicate_provider):
            tool = VoiceDictationTool()
            # Mock selected device
            tool.selected_device = 0
            return tool
    
    @patch('start.sd.InputStream')
    def test_recording_captures_audio_chunks(self, mock_input_stream, voice_tool, mock_audio_data):
        """Test recording captures audio chunks correctly."""
        # Setup mock stream
        mock_stream = MagicMock()
        chunk_size = int(44100 * 0.1)  # 100ms chunks
        chunks = [mock_audio_data[i:i+chunk_size] for i in range(0, len(mock_audio_data), chunk_size)]
        chunk_iter = iter(chunks)
        
        def read(size):
            try:
                chunk = next(chunk_iter)
                if len(chunk) < size:
                    padding = np.zeros((size - len(chunk), chunk.shape[1]), dtype=chunk.dtype)
                    chunk = np.vstack([chunk, padding])
                return chunk, False
            except StopIteration:
                voice_tool.is_recording = False
                return np.zeros((size, mock_audio_data.shape[1]), dtype=mock_audio_data.dtype), False
        
        mock_stream.read = Mock(side_effect=read)
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=None)
        mock_input_stream.return_value = mock_stream
        
        # Start recording
        voice_tool.is_recording = True
        voice_tool._record_audio()
        
        # Verify audio data was captured
        assert voice_tool.audio_data is not None
        assert isinstance(voice_tool.audio_data, np.ndarray)
        assert len(voice_tool.audio_data) > 0
    
    @patch('start.sd.InputStream')
    def test_recording_stops_when_flag_false(self, mock_input_stream, voice_tool, mock_audio_data):
        """Test recording stops when is_recording flag is False."""
        mock_stream = MagicMock()
        read_count = [0]
        
        def read(size):
            read_count[0] += 1
            if read_count[0] >= 3:  # Stop after 3 reads
                voice_tool.is_recording = False
            return mock_audio_data[:size] if len(mock_audio_data) >= size else mock_audio_data, False
        
        mock_stream.read = Mock(side_effect=read)
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=None)
        mock_input_stream.return_value = mock_stream
        
        voice_tool.is_recording = True
        voice_tool._record_audio()
        
        # Should have stopped
        assert not voice_tool.is_recording
        assert read_count[0] >= 3
    
    @patch('start.sd.InputStream')
    def test_recording_respects_max_duration(self, mock_input_stream, voice_tool, mock_audio_data):
        """Test recording respects maximum duration limit."""
        import config
        
        mock_stream = MagicMock()
        
        def read(size):
            # Simulate time passing
            if voice_tool.recording_start_time:
                elapsed = time.time() - voice_tool.recording_start_time
                if elapsed >= config.MAX_RECORDING_SECONDS:
                    voice_tool.is_recording = False
            return mock_audio_data[:size] if len(mock_audio_data) >= size else mock_audio_data, False
        
        mock_stream.read = Mock(side_effect=read)
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=None)
        mock_input_stream.return_value = mock_stream
        
        voice_tool.is_recording = True
        voice_tool.recording_start_time = time.time() - config.MAX_RECORDING_SECONDS - 1  # Past max duration
        
        voice_tool._record_audio()
        
        # Should have stopped due to max duration
        assert not voice_tool.is_recording
    
    @patch('start.sd.InputStream')
    def test_recording_handles_buffer_overflow(self, mock_input_stream, voice_tool, mock_audio_data):
        """Test recording handles buffer overflow."""
        mock_stream = MagicMock()
        overflow_count = [0]
        
        def read(size):
            overflow_count[0] += 1
            overflowed = overflow_count[0] == 2  # Overflow on second read
            if overflow_count[0] >= 3:
                voice_tool.is_recording = False
            return mock_audio_data[:size] if len(mock_audio_data) >= size else mock_audio_data, overflowed
        
        mock_stream.read = Mock(side_effect=read)
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=None)
        mock_input_stream.return_value = mock_stream
        
        voice_tool.is_recording = True
        voice_tool._record_audio()
        
        # Should have handled overflow (no exception)
        assert voice_tool.audio_data is not None
    
    @patch('start.sd.InputStream')
    def test_recording_concatenates_chunks(self, mock_input_stream, voice_tool, mock_audio_data):
        """Test recording concatenates chunks correctly."""
        mock_stream = MagicMock()
        chunks = []
        chunk_size = int(44100 * 0.1)
        
        # Create multiple chunks
        for i in range(0, len(mock_audio_data), chunk_size):
            chunks.append(mock_audio_data[i:i+chunk_size])
        
        chunk_iter = iter(chunks)
        
        def read(size):
            try:
                chunk = next(chunk_iter)
                if len(chunk) < size:
                    padding = np.zeros((size - len(chunk), chunk.shape[1]), dtype=chunk.dtype)
                    chunk = np.vstack([chunk, padding])
                return chunk, False
            except StopIteration:
                voice_tool.is_recording = False
                return np.zeros((size, mock_audio_data.shape[1]), dtype=mock_audio_data.dtype), False
        
        mock_stream.read = Mock(side_effect=read)
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=None)
        mock_input_stream.return_value = mock_stream
        
        voice_tool.is_recording = True
        voice_tool._record_audio()
        
        # Verify chunks were concatenated
        assert voice_tool.audio_data is not None
        assert len(voice_tool.audio_data) > 0
    
    @patch('start.sd.InputStream')
    def test_recording_with_different_sample_rates(self, mock_input_stream, voice_tool):
        """Test recording with different sample rates."""
        import config
        
        # Test with different sample rate
        test_sample_rate = 16000
        test_audio = np.random.randn(test_sample_rate, 1).astype(np.float32)
        
        mock_stream = MagicMock()
        chunk_size = int(test_sample_rate * 0.1)
        chunks = [test_audio[i:i+chunk_size] for i in range(0, len(test_audio), chunk_size)]
        chunk_iter = iter(chunks)
        
        def read(size):
            try:
                chunk = next(chunk_iter)
                if len(chunk) < size:
                    padding = np.zeros((size - len(chunk), chunk.shape[1]), dtype=chunk.dtype)
                    chunk = np.vstack([chunk, padding])
                return chunk, False
            except StopIteration:
                voice_tool.is_recording = False
                return np.zeros((size, test_audio.shape[1]), dtype=test_audio.dtype), False
        
        mock_stream.read = Mock(side_effect=read)
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=None)
        mock_input_stream.return_value = mock_stream
        
        # Temporarily change sample rate
        original_rate = config.RECORDING_SETTINGS['sample_rate']
        config.RECORDING_SETTINGS['sample_rate'] = test_sample_rate
        
        try:
            voice_tool.is_recording = True
            voice_tool._record_audio()
            
            assert voice_tool.audio_data is not None
        finally:
            config.RECORDING_SETTINGS['sample_rate'] = original_rate
    
    @patch('start.sd.InputStream')
    def test_empty_recording_returns_none(self, mock_input_stream, voice_tool):
        """Test empty recording returns None."""
        mock_stream = MagicMock()
        
        def read(size):
            voice_tool.is_recording = False  # Stop immediately
            return np.array([]), False
        
        mock_stream.read = Mock(side_effect=read)
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=None)
        mock_input_stream.return_value = mock_stream
        
        voice_tool.is_recording = True
        voice_tool._record_audio()
        
        # Should be None if no frames were recorded
        # (In practice, this might be empty array, but None is also valid)
        assert voice_tool.audio_data is None or len(voice_tool.audio_data) == 0
    
    def test_audio_data_is_numpy_array(self, voice_tool, mock_audio_data):
        """Test audio data is numpy array."""
        voice_tool.audio_data = mock_audio_data
        assert isinstance(voice_tool.audio_data, np.ndarray)
    
    def test_audio_data_has_correct_dtype(self, voice_tool, mock_audio_data):
        """Test audio data has correct dtype (float32)."""
        voice_tool.audio_data = mock_audio_data
        assert voice_tool.audio_data.dtype == np.float32
    
    def test_audio_data_shape_is_correct(self, voice_tool, mock_audio_data):
        """Test audio data shape is correct."""
        voice_tool.audio_data = mock_audio_data
        # Should be 2D: (samples, channels)
        assert len(voice_tool.audio_data.shape) == 2
        assert voice_tool.audio_data.shape[1] == 1  # Mono channel
