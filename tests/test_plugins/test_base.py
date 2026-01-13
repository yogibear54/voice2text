"""Tests for StatusPlugin base class."""
import pytest

from plugins.base import StatusPlugin
from status_manager import Status


@pytest.mark.unit
class TestStatusPluginAbstractClass:
    """Test StatusPlugin abstract base class."""
    
    def test_is_abstract_cannot_instantiate(self):
        """Test StatusPlugin is abstract (cannot instantiate directly)."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            StatusPlugin()
    
    def test_subclass_without_update_status_cannot_instantiate(self):
        """Test subclass without update_status() cannot be instantiated."""
        class IncompletePlugin(StatusPlugin):
            pass
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompletePlugin()
    
    def test_subclass_with_update_status_can_instantiate(self):
        """Test subclass with update_status() can be instantiated."""
        class CompletePlugin(StatusPlugin):
            def update_status(self, status: Status):
                pass
        
        plugin = CompletePlugin()
        assert isinstance(plugin, StatusPlugin)


@pytest.mark.unit
class TestStatusPluginDefaultCleanup:
    """Test StatusPlugin default cleanup() method."""
    
    def test_default_cleanup_exists_and_doesnt_raise(self):
        """Test default cleanup() exists and doesn't raise."""
        class TestPlugin(StatusPlugin):
            def update_status(self, status: Status):
                pass
        
        plugin = TestPlugin()
        # Should not raise
        plugin.cleanup()
    
    def test_subclasses_can_override_cleanup(self):
        """Test subclasses can override cleanup()."""
        cleanup_called = []
        
        class PluginWithCleanup(StatusPlugin):
            def update_status(self, status: Status):
                pass
            
            def cleanup(self):
                cleanup_called.append(True)
        
        plugin = PluginWithCleanup()
        plugin.cleanup()
        
        assert cleanup_called == [True]
