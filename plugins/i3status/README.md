# i3status Plugin Setup Guide

This guide explains how to set up the i3status plugin to display voice2text status in your i3bar.

## Overview

The i3status plugin uses a wrapper script method that pipes i3status output through a Python script that:
1. Reads JSON from i3status (stdin)
2. Parses the i3bar JSON format
3. Injects the voice2text status block
4. Outputs the modified JSON to stdout for i3bar

## Setup Steps

### 1. Configure i3status.conf

Edit your `~/.config/i3status/config` (or `/etc/i3status.conf`) and ensure the `general` section has:

```ini
general {
    output_format = "i3bar"
    # ... other settings ...
}
```

**Note:** `output_format = "i3bar"` is the default in most modern i3status configurations, so you may already have this set.

### 2. Update i3 Config

Edit your i3 config file (usually `~/.config/i3/config`) and update the `bar` section:

**Before:**
```i3
bar {
    status_command i3status
}
```

**After:**
```i3
bar {
    status_command i3status | /path/to/voice2text/i3status_wrapper.py
}
```

**Or use an absolute path:**
```i3
bar {
    status_command i3status | /absolute/path/to/voice2text/i3status_wrapper.py
}
```

### 3. Reload i3

After making the changes, reload i3:
- Press `Mod+Shift+R` (default: `Mod` is `Super`/`Windows` key)
- Or run: `i3-msg reload`

### 4. Verify

1. Start your voice2text application (`start.py`)
2. You should see the voice2text status appear in your i3bar with the following states:
   - **⚪ Not Started** (dark gray) - When the app is created but not yet initialized
   - **⏸️ Idle** (gray) - When the app is ready and waiting for input
   - **🔴 Recording...** (red) - When recording audio (press and hold Ctrl+Alt)
   - **🔄 Processing...** (orange) - When transcribing audio
3. The status will automatically update as you use the application

## How It Works

1. **i3status** generates status blocks (CPU, memory, time, etc.) and outputs them in i3bar JSON format
2. **i3status_wrapper.py** reads this output, parses it, and injects the voice2text status block
3. **i3bar** displays all the blocks, including the injected voice2text status

The wrapper script reads the voice2text status from `/tmp/voice2text_status` (or the path specified by `I3_STATUS_FILE` environment variable), which is written by the `I3StatusPlugin` in your voice2text application.

## Status States

The voice2text application has four status states that are displayed in your i3bar:

| Status | Display | Color | Description |
|--------|---------|-------|-------------|
| **NOT_STARTED** | ⚪ Not Started | Dark Gray (#666666) | App is created but not yet initialized |
| **IDLE** | ⏸️ Idle | Gray (#888888) | App is ready and waiting for input |
| **RECORDING** | 🔴 Recording... | Red (#ff0000) | Currently recording audio |
| **PROCESSING** | 🔄 Processing... | Orange (#ffa500) | Transcribing recorded audio |

The status automatically transitions:
- `NOT_STARTED` → `IDLE` when the app finishes initialization
- `IDLE` → `RECORDING` when you press Ctrl+Alt
- `RECORDING` → `PROCESSING` when you release Ctrl+Alt
- `PROCESSING` → `IDLE` when transcription completes

## Troubleshooting

### JSON Parse Error

If you see "Error: Could not parse JSON" in your i3bar:

1. **Test the wrapper script manually:**
   ```bash
   # Test with a simple i3status-like input
   echo '{"version":1}
   [
   [{"full_text":"test"}],' | /path/to/i3status_wrapper.py
   ```
   This should output valid JSON. If it doesn't, there's an issue with the script.

2. **Check for script errors:**
   ```bash
   # Run i3status through the wrapper and capture errors
   i3status 2>&1 | /path/to/i3status_wrapper.py 2>&1 | head -20
   ```
   Look for any Python errors in the output.

3. **Verify the script is executable:**
   ```bash
   ls -l /path/to/i3status_wrapper.py
   chmod +x /path/to/i3status_wrapper.py  # if needed
   ```

4. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.6+
   ```

5. **Test without the wrapper (temporarily):**
   ```i3
   bar {
       status_command i3status
   }
   ```
   If this works, the issue is with the wrapper script.

6. **Check i3 logs:**
   ```bash
   # Check for errors
   journalctl -f | grep i3
   # Or check ~/.xsession-errors
   tail -f ~/.xsession-errors
   ```

### Status not appearing

1. Check that the status file exists:
   ```bash
   cat /tmp/voice2text_status
   ```

2. Verify the status file contains valid JSON:
   ```bash
   python3 -m json.tool /tmp/voice2text_status
   ```

3. Check that your voice2text app is running and writing to the status file:
   ```bash
   # Watch the status file
   watch -n 1 cat /tmp/voice2text_status
   ```

4. Verify the status changes as you use the app:
   - When the app first starts, you should see "⚪ Not Started"
   - After initialization, it should change to "⏸️ Idle"
   - When recording, it should show "🔴 Recording..."
   - During transcription, it should show "🔄 Processing..."

### Permission errors

Make sure the wrapper script is executable:
```bash
chmod +x /path/to/i3status_wrapper.py
```

### Python not found

The script uses `#!/usr/bin/env python3`. If Python 3 is not in your PATH, you may need to update the shebang or use the full path to python3.

## Environment Variables

You can customize the status file path by setting the `I3_STATUS_FILE` environment variable:

```bash
export I3_STATUS_FILE=/custom/path/to/status
```

Or in your i3 config:
```i3
bar {
    status_command env I3_STATUS_FILE=/custom/path i3status | /path/to/i3status_wrapper.py
}
```
