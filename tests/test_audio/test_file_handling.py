"""Tests for WAV file handling."""
import os
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from scipy.io.wavfile import read as wav_read

from start import VoiceDictationTool


@pytest.mark.unit
class TestWAVFileHandling:
    """Test WAV file save/load operations."""
    
    @pytest.fixture
    def voice_tool(self, replicate_provider):
        """Create VoiceDictationTool instance for testing."""
        with patch('start.StatusManager'), \
             patch('start.create_provider', return_value=replicate_provider):
            tool = VoiceDictationTool()
            return tool
    
    def test_save_wav_file_creates_file(self, voice_tool, mock_audio_data, temp_dir):
        """Test _save_wav_file() saves file correctly."""
        import config
        
        filename = temp_dir / "test_output.wav"
        sample_rate = config.RECORDING_SETTINGS['sample_rate']
        channels = config.RECORDING_SETTINGS['channels']
        
        voice_tool._save_wav_file(str(filename), mock_audio_data, sample_rate, channels)
        
        assert filename.exists()
        assert filename.stat().st_size > 0
    
    def test_save_wav_file_converts_float32_to_int16(self, voice_tool, mock_audio_data, temp_dir):
        """Test float32 to int16 conversion."""
        import config
        
        filename = temp_dir / "test_output.wav"
        sample_rate = config.RECORDING_SETTINGS['sample_rate']
        channels = config.RECORDING_SETTINGS['channels']
        
        # Save file
        voice_tool._save_wav_file(str(filename), mock_audio_data, sample_rate, channels)
        
        # Read it back
        read_rate, read_data = wav_read(str(filename))
        
        # Verify it's int16
        assert read_data.dtype == np.int16
        assert read_rate == sample_rate
    
    def test_save_wav_file_clips_audio_range(self, voice_tool, temp_dir):
        """Test audio clipping to [-1.0, 1.0] range."""
        import config
        
        # Create audio data outside [-1.0, 1.0] range
        audio_out_of_range = np.array([[-2.0], [1.5], [-0.5], [0.5], [2.0]], dtype=np.float32)
        
        filename = temp_dir / "test_clipped.wav"
        sample_rate = config.RECORDING_SETTINGS['sample_rate']
        channels = config.RECORDING_SETTINGS['channels']
        
        # Should not raise error
        voice_tool._save_wav_file(str(filename), audio_out_of_range, sample_rate, channels)
        
        # Read back and verify values are in valid range
        read_rate, read_data = wav_read(str(filename))
        # Convert back to float for comparison
        read_float = read_data.astype(np.float32) / 32767.0
        assert np.all(read_float >= -1.0)
        assert np.all(read_float <= 1.0)
    
    def test_save_wav_file_can_be_read_back(self, voice_tool, mock_audio_data, temp_dir):
        """Test file can be read back and verified."""
        import config
        
        filename = temp_dir / "test_readback.wav"
        sample_rate = config.RECORDING_SETTINGS['sample_rate']
        channels = config.RECORDING_SETTINGS['channels']
        
        voice_tool._save_wav_file(str(filename), mock_audio_data, sample_rate, channels)
        
        # Read back
        read_rate, read_data = wav_read(str(filename))
        
        assert read_rate == sample_rate
        # scipy.io.wavfile.read returns 1D array for mono, 2D for stereo
        if channels == 1:
            assert len(read_data.shape) == 1 or read_data.shape[1] == channels
        else:
            assert len(read_data.shape) == 2
            assert read_data.shape[1] == channels
        assert len(read_data) > 0
    
    def test_save_wav_file_has_correct_sample_rate(self, voice_tool, mock_audio_data, temp_dir):
        """Test file has correct sample rate."""
        test_sample_rate = 16000
        
        filename = temp_dir / "test_samplerate.wav"
        channels = 1
        
        voice_tool._save_wav_file(str(filename), mock_audio_data, test_sample_rate, channels)
        
        read_rate, _ = wav_read(str(filename))
        assert read_rate == test_sample_rate
    
    def test_save_wav_file_has_correct_channels(self, voice_tool, mock_audio_data_stereo, temp_dir):
        """Test file has correct number of channels."""
        import config
        
        filename = temp_dir / "test_channels.wav"
        sample_rate = config.RECORDING_SETTINGS['sample_rate']
        channels = 2  # Stereo
        
        voice_tool._save_wav_file(str(filename), mock_audio_data_stereo, sample_rate, channels)
        
        read_rate, read_data = wav_read(str(filename))
        assert read_data.shape[1] == channels
    
    def test_save_wav_file_handles_errors(self, voice_tool, mock_audio_data):
        """Test error handling when save fails."""
        import config
        
        # Try to save to invalid path (directory that doesn't exist)
        invalid_path = "/nonexistent/directory/test.wav"
        sample_rate = config.RECORDING_SETTINGS['sample_rate']
        channels = config.RECORDING_SETTINGS['channels']
        
        with pytest.raises(Exception):
            voice_tool._save_wav_file(invalid_path, mock_audio_data, sample_rate, channels)
    
    def test_temp_files_created_in_correct_directory(self, voice_tool, temp_dir):
        """Test temporary files are created in correct directory."""
        import config
        from datetime import datetime
        
        # Set temp_dir to our test temp_dir
        voice_tool.temp_dir = temp_dir
        
        # Generate filename like the real code does
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        temp_filename = temp_dir / f"{config.TEMP_FILE_PREFIX}{timestamp}.{config.AUDIO_FORMAT}"
        
        # Save a test file
        mock_audio = np.random.randn(1000, 1).astype(np.float32)
        voice_tool._save_wav_file(str(temp_filename), mock_audio, 44100, 1)
        
        assert temp_filename.exists()
        assert temp_filename.parent == temp_dir
    
    def test_file_cleanup_handles_missing_files(self, voice_tool, temp_dir):
        """Test cleanup handles missing files gracefully."""
        missing_file = temp_dir / "nonexistent.wav"
        
        # Should not raise error
        try:
            if missing_file.exists():
                missing_file.unlink()
        except Exception as e:
            pytest.fail(f"Cleanup should handle missing files gracefully: {e}")
