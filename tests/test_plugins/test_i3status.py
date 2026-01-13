"""Tests for I3StatusPlugin."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from plugins.i3status import I3StatusPlugin
from status_manager import Status


@pytest.mark.unit
class TestI3StatusPluginInitialization:
    """Test I3StatusPlugin initialization."""
    
    def test_init_with_default_status_file_path(self, temp_dir):
        """Test initialization with default status file path."""
        status_file = temp_dir / "voice2text_status"
        plugin = I3StatusPlugin(str(status_file))
        
        assert plugin.status_file == status_file
    
    def test_init_with_custom_status_file_path(self, temp_status_file):
        """Test initialization with custom status file path."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        assert plugin.status_file == temp_status_file
    
    def test_parent_directory_created_if_not_exists(self, temp_dir):
        """Test parent directory is created if it doesn't exist."""
        nested_path = temp_dir / "nested" / "dir" / "status.json"
        
        plugin = I3StatusPlugin(str(nested_path))
        
        assert nested_path.parent.exists()
    
    def test_initial_status_file_created_with_not_started(self, temp_status_file):
        """Test initial status file is created with NOT_STARTED status."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        assert temp_status_file.exists()
        
        with open(temp_status_file, 'r') as f:
            data = json.load(f)
            assert data['full_text'] == "⚪ Not Started"
            assert data['color'] == "#666666"


@pytest.mark.unit
class TestI3StatusPluginUpdateStatus:
    """Test I3StatusPlugin.update_status() method."""
    
    def test_recording_status_writes_correct_json(self, temp_status_file):
        """Test RECORDING status writes correct JSON."""
        plugin = I3StatusPlugin(str(temp_status_file))
        plugin.update_status(Status.RECORDING)
        
        with open(temp_status_file, 'r') as f:
            data = json.load(f)
        
        assert data['full_text'] == "🔴 Recording..."
        assert data['color'] == "#ff0000"
        assert data['name'] == "voice2text"
        assert data['instance'] == "voice2text"
    
    def test_processing_status_writes_correct_json(self, temp_status_file):
        """Test PROCESSING status writes correct JSON."""
        plugin = I3StatusPlugin(str(temp_status_file))
        plugin.update_status(Status.PROCESSING)
        
        with open(temp_status_file, 'r') as f:
            data = json.load(f)
        
        assert data['full_text'] == "🔄 Processing..."
        assert data['color'] == "#ffa500"
        assert data['name'] == "voice2text"
        assert data['instance'] == "voice2text"
    
    def test_idle_status_writes_correct_json(self, temp_status_file):
        """Test IDLE status writes correct JSON."""
        plugin = I3StatusPlugin(str(temp_status_file))
        plugin.update_status(Status.IDLE)
        
        with open(temp_status_file, 'r') as f:
            data = json.load(f)
        
        assert data['full_text'] == "⏸️ Idle"
        assert data['color'] == "#888888"
        assert data['name'] == "voice2text"
        assert data['instance'] == "voice2text"
    
    def test_not_started_status_writes_correct_json(self, temp_status_file):
        """Test NOT_STARTED status writes correct JSON."""
        plugin = I3StatusPlugin(str(temp_status_file))
        plugin.update_status(Status.NOT_STARTED)
        
        with open(temp_status_file, 'r') as f:
            data = json.load(f)
        
        assert data['full_text'] == "⚪ Not Started"
        assert data['color'] == "#666666"
        assert data['name'] == "voice2text"
        assert data['instance'] == "voice2text"
    
    def test_json_format_is_valid(self, temp_status_file):
        """Test JSON format is valid (can be parsed)."""
        plugin = I3StatusPlugin(str(temp_status_file))
        plugin.update_status(Status.RECORDING)
        
        # Should not raise
        with open(temp_status_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
    
    def test_json_contains_required_fields(self, temp_status_file):
        """Test JSON contains required fields: full_text, color, name, instance."""
        plugin = I3StatusPlugin(str(temp_status_file))
        plugin.update_status(Status.PROCESSING)
        
        with open(temp_status_file, 'r') as f:
            data = json.load(f)
        
        assert 'full_text' in data
        assert 'color' in data
        assert 'name' in data
        assert 'instance' in data
    
    def test_file_is_overwritten_on_each_update(self, temp_status_file):
        """Test file is overwritten on each status update."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        plugin.update_status(Status.RECORDING)
        with open(temp_status_file, 'r') as f:
            data1 = json.load(f)
        
        plugin.update_status(Status.PROCESSING)
        with open(temp_status_file, 'r') as f:
            data2 = json.load(f)
        
        assert data1['full_text'] == "🔴 Recording..."
        assert data2['full_text'] == "🔄 Processing..."
    
    def test_file_write_errors_are_caught(self, temp_status_file, capsys):
        """Test file write errors are caught and logged (don't crash)."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        # Make the file read-only to cause write error
        temp_status_file.chmod(0o444)
        
        try:
            # Should not raise exception
            plugin.update_status(Status.RECORDING)
            
            # Should print error message
            captured = capsys.readouterr()
            assert "Failed to write i3 status" in captured.out
        finally:
            # Restore permissions for cleanup
            temp_status_file.chmod(0o644)


@pytest.mark.unit
class TestI3StatusPluginCleanup:
    """Test I3StatusPlugin.cleanup() method."""
    
    def test_status_file_is_deleted_when_exists(self, temp_status_file):
        """Test status file is deleted when it exists."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        assert temp_status_file.exists()
        
        plugin.cleanup()
        
        assert not temp_status_file.exists()
    
    def test_cleanup_doesnt_raise_when_file_doesnt_exist(self, temp_status_file):
        """Test cleanup doesn't raise when file doesn't exist."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        # Delete file manually
        temp_status_file.unlink()
        
        # Should not raise
        plugin.cleanup()
    
    def test_cleanup_errors_are_caught(self, temp_status_file, capsys):
        """Test cleanup errors are caught and logged (don't crash)."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        # Make directory read-only to cause delete error
        temp_status_file.parent.chmod(0o555)
        
        try:
            # Should not raise exception
            plugin.cleanup()
            
            # Should print error message
            captured = capsys.readouterr()
            assert "Failed to cleanup i3 status file" in captured.out
        finally:
            # Restore permissions
            temp_status_file.parent.chmod(0o755)


@pytest.mark.unit
class TestI3StatusPluginFileOperations:
    """Test I3StatusPlugin file operations."""
    
    def test_status_file_created_in_correct_location(self, temp_status_file):
        """Test status file is created in correct location."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        assert temp_status_file.exists()
        assert temp_status_file == plugin.status_file
    
    def test_status_file_content_matches_expected_json_structure(self, temp_status_file):
        """Test status file content matches expected JSON structure."""
        plugin = I3StatusPlugin(str(temp_status_file))
        plugin.update_status(Status.IDLE)
        
        with open(temp_status_file, 'r') as f:
            data = json.load(f)
        
        # Verify structure
        assert isinstance(data, dict)
        assert 'full_text' in data
        assert 'color' in data
        assert 'name' in data
        assert 'instance' in data
        assert isinstance(data['full_text'], str)
        assert isinstance(data['color'], str)
        assert isinstance(data['name'], str)
        assert isinstance(data['instance'], str)
    
    def test_status_file_can_be_read_back_and_parsed(self, temp_status_file):
        """Test status file can be read back and parsed correctly."""
        plugin = I3StatusPlugin(str(temp_status_file))
        
        # Write different statuses
        plugin.update_status(Status.RECORDING)
        with open(temp_status_file, 'r') as f:
            data1 = json.load(f)
        assert data1['full_text'] == "🔴 Recording..."
        
        plugin.update_status(Status.PROCESSING)
        with open(temp_status_file, 'r') as f:
            data2 = json.load(f)
        assert data2['full_text'] == "🔄 Processing..."
