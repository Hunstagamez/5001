#!/usr/bin/env python3
"""
Project 5001 - Real-time Harvester Log Viewer
View harvester logs in real-time in a separate terminal window.
"""

import os
import sys
import time
import signal
from pathlib import Path
from datetime import datetime

def print_banner():
    """Print the log viewer banner."""
    print("=" * 80)
    print("🎵 Project 5001 - Real-time Harvester Log Viewer")
    print("=" * 80)
    print("Press Ctrl+C to exit")
    print("=" * 80)
    print()

def follow_logs(log_file_path: str, lines: int = 10):
    """Follow logs in real-time."""
    log_file = Path(log_file_path)
    
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file_path}")
        print("Make sure the harvester is running first.")
        return
    
    print(f"📝 Following logs: {log_file_path}")
    print(f"📊 Showing last {lines} lines, then following in real-time...")
    print("-" * 80)
    
    # Show last N lines first
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            if len(all_lines) > lines:
                for line in all_lines[-lines:]:
                    print(line.rstrip())
            else:
                for line in all_lines:
                    print(line.rstrip())
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return
    
    print("-" * 80)
    print("🔄 Following new log entries...")
    print("-" * 80)
    
    # Follow new entries
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # Go to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {line.rstrip()}")
                else:
                    time.sleep(0.1)
                    
    except KeyboardInterrupt:
        print("\n\n👋 Log viewer stopped by user")
    except Exception as e:
        print(f"\n❌ Error following logs: {e}")

def check_harvester_status():
    """Check if harvester is running."""
    from harvester_manager import HarvesterManager
    
    manager = HarvesterManager()
    return manager.is_running()

def main():
    """Main entry point."""
    print_banner()
    
    # Check if harvester is running
    if not check_harvester_status():
        print("⚠️  Harvester is not currently running!")
        print("Start the harvester first with: python cli.py -> Harvester Control -> Start Harvester")
        print()
        input("Press Enter to exit...")
        return
    
    # Determine log file path
    log_file = "Project5001/Logs/harvester.log"
    
    # Get number of lines to show initially
    try:
        lines = int(input("Enter number of recent lines to show (default 10): ") or "10")
    except ValueError:
        lines = 10
    
    print()
    
    # Start following logs
    follow_logs(log_file, lines)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Log viewer stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...") 