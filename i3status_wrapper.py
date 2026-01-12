#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i3status wrapper script that pipes i3status output and injects custom status blocks.

This script reads JSON from i3status (stdin), parses it, injects the voice2text
status block, and outputs the modified JSON to stdout for i3bar.

Based on the i3status wrapper example from:
http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl

Usage:
    In your i3 config, set:
    status_command i3status | /path/to/i3status_wrapper.py
"""
import sys
import json
import os
from pathlib import Path


# Configuration - matches config.py
I3_STATUS_FILE = os.getenv('I3_STATUS_FILE', '/tmp/voice2text_status')


def read_voice2text_status():
    """Read the voice2text status from the status file.
    
    Returns:
        A dict with status block data, or None if no status file exists
    """
    status_file = Path(I3_STATUS_FILE)
    if not status_file.exists():
        return None
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
        return status_data
    except (json.JSONDecodeError, IOError):
        return None


def print_line(message):
    """Non-buffered printing to stdout."""
    sys.stdout.write(message + '\n')
    sys.stdout.flush()


def read_line():
    """Interrupted respecting reader for stdin."""
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','
        
        # Remove trailing comma if present (i3status sometimes adds it)
        line = line.rstrip(',').strip()

        j = json.loads(line)
        
        # Read voice2text status
        voice2text_block = read_voice2text_status()
        
        # Insert voice2text status block if it exists and has content
        if voice2text_block and isinstance(voice2text_block, dict):
            # Only insert if it has full_text and it's not empty
            if voice2text_block.get('full_text', '').strip():
                # Remove existing voice2text block if present (by name)
                voice2text_name = voice2text_block.get('name', 'voice2text')
                j = [b for b in j if b.get('name') != voice2text_name]
                # Append the new voice2text block
                j.append(voice2text_block)
        
        # and echo back new encoded json (compact format to match i3status)
        print_line(prefix + json.dumps(j, separators=(',', ':')))
