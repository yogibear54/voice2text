"""i3 status bar plugin for voice dictation tool."""
import json
from pathlib import Path
from status_manager import Status
from plugins.base import StatusPlugin


class I3StatusPlugin(StatusPlugin):
    """Plugin that writes status to a file for i3bar to read."""
    
    def __init__(self, status_file: str = "/tmp/voice2text_status"):
        """Initialize i3 status plugin.
        
        Args:
            status_file: Path to the status file that i3bar will read
        """
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.update_status(Status.NOT_STARTED)
    
    def update_status(self, status: Status):
        """Update the status file with current application state.
        
        Args:
            status: The new application status
        """
        # Create JSON block for i3bar
        if status == Status.RECORDING:
            text = "🔴 Recording..."
            color = "#ff0000"  # Red
        elif status == Status.PROCESSING:
            text = "🔄 Processing..."
            color = "#ffa500"  # Orange
        elif status == Status.IDLE:
            text = "⏸️ Idle"
            color = "#888888"  # Gray
        elif status == Status.NOT_STARTED:
            text = "⚪ Not Started"
            color = "#666666"  # Dark gray
        else:
            text = ""
            color = "#ffffff"  # White (fallback)
        
        # i3bar JSON format
        block = {
            "full_text": text,
            "color": color,
            "name": "voice2text",
            "instance": "voice2text"
        }
        
        try:
            # Write status to file
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(block, f)
        except Exception as e:
            print(f"⚠️  Failed to write i3 status: {e}")
    
    def cleanup(self):
        """Remove status file on cleanup."""
        try:
            if self.status_file.exists():
                self.status_file.unlink()
        except Exception as e:
            print(f"⚠️  Failed to cleanup i3 status file: {e}")
