"""Tests for StatusManager class."""
from unittest.mock import MagicMock, Mock

import pytest

from status_manager import Status, StatusManager


@pytest.mark.unit
class TestStatusManagerInitialization:
    """Test StatusManager initialization."""
    
    def test_init_sets_not_started_status(self):
        """Test __init__() sets initial status to NOT_STARTED."""
        manager = StatusManager()
        assert manager.status == Status.NOT_STARTED
    
    def test_init_initializes_empty_plugins_list(self):
        """Test __init__() initializes empty plugins list."""
        manager = StatusManager()
        assert manager.plugins == []
        assert len(manager.plugins) == 0


@pytest.mark.unit
class TestStatusManagerRegisterPlugin:
    """Test StatusManager.register_plugin() method."""
    
    def test_register_valid_plugin(self, mock_plugin):
        """Test registering valid plugin (with update_status method)."""
        manager = StatusManager()
        manager.register_plugin(mock_plugin)
        
        assert len(manager.plugins) == 1
        assert mock_plugin in manager.plugins
    
    def test_plugin_initialized_with_current_status(self, mock_plugin):
        """Test plugin is initialized with current status when registered."""
        manager = StatusManager()
        manager.register_plugin(mock_plugin)
        
        # Plugin should be initialized with NOT_STARTED status
        mock_plugin.update_status.assert_called_once_with(Status.NOT_STARTED)
    
    def test_register_multiple_plugins(self, mock_plugin):
        """Test registering multiple plugins."""
        manager = StatusManager()
        plugin1 = MagicMock()
        plugin1.update_status = Mock()
        plugin2 = MagicMock()
        plugin2.update_status = Mock()
        
        manager.register_plugin(plugin1)
        manager.register_plugin(plugin2)
        
        assert len(manager.plugins) == 2
        assert plugin1 in manager.plugins
        assert plugin2 in manager.plugins
    
    def test_register_invalid_plugin_raises_error(self):
        """Test registering invalid plugin (no update_status method) raises ValueError."""
        manager = StatusManager()
        
        # Create an object that truly doesn't have update_status method
        class IncompletePlugin:
            pass
        
        incomplete_plugin = IncompletePlugin()
        
        with pytest.raises(ValueError, match="does not implement update_status method"):
            manager.register_plugin(incomplete_plugin)
        
        assert len(manager.plugins) == 0
    
    def test_plugin_list_contains_registered_plugins(self, mock_plugin):
        """Test plugin list contains registered plugins."""
        manager = StatusManager()
        manager.register_plugin(mock_plugin)
        
        assert mock_plugin in manager.plugins


@pytest.mark.unit
class TestStatusManagerSetStatus:
    """Test StatusManager.set_status() method."""
    
    def test_status_is_updated_correctly(self, mock_plugin):
        """Test status is updated correctly."""
        manager = StatusManager()
        manager.register_plugin(mock_plugin)
        
        manager.set_status(Status.RECORDING)
        
        assert manager.status == Status.RECORDING
    
    def test_all_plugins_receive_status_updates(self, mock_plugin):
        """Test all registered plugins receive status updates."""
        manager = StatusManager()
        plugin1 = MagicMock()
        plugin1.update_status = Mock()
        plugin2 = MagicMock()
        plugin2.update_status = Mock()
        
        manager.register_plugin(plugin1)
        manager.register_plugin(plugin2)
        
        manager.set_status(Status.PROCESSING)
        
        plugin1.update_status.assert_called_with(Status.PROCESSING)
        plugin2.update_status.assert_called_with(Status.PROCESSING)
    
    def test_plugin_update_errors_are_caught(self, capsys):
        """Test plugin update errors are caught and logged (don't crash)."""
        manager = StatusManager()
        
        # Create plugin that raises exception during update_status
        # First register with a working update_status, then replace it
        error_plugin = MagicMock()
        error_plugin.update_status = Mock()
        
        manager.register_plugin(error_plugin)
        
        # Now replace update_status to raise exception
        error_plugin.update_status = Mock(side_effect=Exception("Plugin error"))
        
        # Should not raise exception
        manager.set_status(Status.RECORDING)
        
        # Should print error message
        captured = capsys.readouterr()
        assert "Error updating plugin" in captured.out
        assert "Plugin error" in captured.out
    
    def test_status_transitions(self, mock_plugin):
        """Test status transitions: NOT_STARTED → IDLE → RECORDING → PROCESSING → IDLE."""
        manager = StatusManager()
        manager.register_plugin(mock_plugin)
        
        # Initial state
        assert manager.status == Status.NOT_STARTED
        
        # Transition to IDLE
        manager.set_status(Status.IDLE)
        assert manager.status == Status.IDLE
        
        # Transition to RECORDING
        manager.set_status(Status.RECORDING)
        assert manager.status == Status.RECORDING
        
        # Transition to PROCESSING
        manager.set_status(Status.PROCESSING)
        assert manager.status == Status.PROCESSING
        
        # Transition back to IDLE
        manager.set_status(Status.IDLE)
        assert manager.status == Status.IDLE


@pytest.mark.unit
class TestStatusManagerGetStatus:
    """Test StatusManager.get_status() method."""
    
    def test_returns_current_status(self):
        """Test returns current status."""
        manager = StatusManager()
        assert manager.get_status() == Status.NOT_STARTED
    
    def test_returns_correct_status_after_updates(self):
        """Test returns correct status after updates."""
        manager = StatusManager()
        
        manager.set_status(Status.RECORDING)
        assert manager.get_status() == Status.RECORDING
        
        manager.set_status(Status.PROCESSING)
        assert manager.get_status() == Status.PROCESSING


@pytest.mark.unit
class TestStatusManagerCleanup:
    """Test StatusManager.cleanup() method."""
    
    def test_calls_cleanup_on_plugins_with_method(self, mock_plugin):
        """Test calls cleanup() on all plugins that have it."""
        manager = StatusManager()
        manager.register_plugin(mock_plugin)
        
        manager.cleanup()
        
        mock_plugin.cleanup.assert_called_once()
    
    def test_plugins_without_cleanup_dont_cause_errors(self):
        """Test plugins without cleanup() method don't cause errors."""
        manager = StatusManager()
        
        # Plugin without cleanup method
        plugin_no_cleanup = MagicMock()
        plugin_no_cleanup.update_status = Mock()
        # No cleanup method
        
        manager.register_plugin(plugin_no_cleanup)
        
        # Should not raise
        manager.cleanup()
    
    def test_cleanup_errors_are_caught(self, capsys):
        """Test cleanup errors are caught and logged (don't crash)."""
        manager = StatusManager()
        
        # Plugin with cleanup that raises exception
        error_plugin = MagicMock()
        error_plugin.update_status = Mock()
        error_plugin.cleanup = Mock(side_effect=Exception("Cleanup error"))
        
        manager.register_plugin(error_plugin)
        
        # Should not raise exception
        manager.cleanup()
        
        # Should print error message
        captured = capsys.readouterr()
        assert "Error cleaning up plugin" in captured.out
        assert "Cleanup error" in captured.out
    
    def test_cleanup_works_with_multiple_plugins(self):
        """Test cleanup works with multiple plugins."""
        manager = StatusManager()
        
        plugin1 = MagicMock()
        plugin1.update_status = Mock()
        plugin1.cleanup = Mock()
        
        plugin2 = MagicMock()
        plugin2.update_status = Mock()
        plugin2.cleanup = Mock()
        
        manager.register_plugin(plugin1)
        manager.register_plugin(plugin2)
        
        manager.cleanup()
        
        plugin1.cleanup.assert_called_once()
        plugin2.cleanup.assert_called_once()
