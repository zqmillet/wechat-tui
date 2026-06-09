#!/usr/bin/env python3
"""Check log file for errors."""
import os

log_path = os.path.expanduser('~/.wechat-tui/wechat-tui.log')
if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        lines = f.readlines()
        # Show last 50 lines
        print("Last 50 lines of log:")
        for line in lines[-50:]:
            print(line.rstrip())
else:
    print(f"Log file not found: {log_path}")