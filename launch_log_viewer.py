#!/usr/bin/env python3
"""
Project 5001 - Log Viewer Launcher
Launches the real-time log viewer in a new terminal window.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def launch_log_viewer():
    """Launch the log viewer in a new terminal window."""
    script_path = Path(__file__).parent / "view_harvester_logs.py"
    
    if not script_path.exists():
        print("❌ Log viewer script not found!")
        return False
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows - use start command
            subprocess.Popen([
                "start", "cmd", "/k", 
                f"python \"{script_path}\""
            ], shell=True)
            
        elif system == "Darwin":  # macOS
            # macOS - use Terminal.app
            subprocess.Popen([
                "open", "-a", "Terminal", 
                f"python3 \"{script_path}\""
            ])
            
        else:  # Linux
            # Try different terminal emulators
            terminals = [
                ["gnome-terminal", "--", "python3", str(script_path)],
                ["konsole", "-e", f"python3 {script_path}"],
                ["xterm", "-e", f"python3 {script_path}"],
                ["terminator", "-e", f"python3 {script_path}"],
                ["xfce4-terminal", "-e", f"python3 {script_path}"]
            ]
            
            for terminal_cmd in terminals:
                try:
                    subprocess.Popen(terminal_cmd)
                    break
                except FileNotFoundError:
                    continue
            else:
                print("❌ No suitable terminal emulator found")
                print("Run manually: python view_harvester_logs.py")
                return False
        
        print("✅ Log viewer launched in new terminal window")
        return True
        
    except Exception as e:
        print(f"❌ Failed to launch log viewer: {e}")
        print("Run manually: python view_harvester_logs.py")
        return False

if __name__ == "__main__":
    launch_log_viewer() 