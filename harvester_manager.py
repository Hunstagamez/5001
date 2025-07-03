#!/usr/bin/env python3
"""
Project 5001 - Harvester Manager
Manages single instance control, PID files, and real-time status monitoring.
"""

import os
import sys
import time
import signal
import subprocess
import threading
import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import platform

class HarvesterManager:
    """Manages harvester instance control and monitoring."""
    
    def __init__(self):
        self.pid_file = Path("Project5001/harvester.pid")
        self.status_file = Path("Project5001/harvester_status.json")
        self.log_file = Path("Project5001/Logs/harvester.log")
        
        # Ensure directories exist
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def is_running(self) -> bool:
        """Check if harvester is currently running."""
        # Check PID file first
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process is actually running
                if self._is_process_running(pid):
                    return True
                else:
                    # Process is dead, clean up PID file
                    self._cleanup_pid_file()
                    return False
            except (ValueError, FileNotFoundError):
                self._cleanup_pid_file()
                return False
        
        # Fallback to process detection
        return self._detect_harvester_process()
    
    def start_harvester(self, daemon_mode: bool = True) -> Dict:
        """Start the harvester with single instance control."""
        if self.is_running():
            return {
                "success": False,
                "message": "Harvester is already running",
                "pid": self._get_pid()
            }
        
        try:
            # Start harvester process
            cmd = [sys.executable, 'harvester_v2.py', 'main']
            if daemon_mode:
                cmd.append('--daemon')
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment to see if it starts successfully
            time.sleep(2)
            
            if process.poll() is None:  # Process is still running
                # Write PID file
                with open(self.pid_file, 'w') as f:
                    f.write(str(process.pid))
                
                # Initialize status
                self._update_status({
                    "pid": process.pid,
                    "start_time": datetime.now().isoformat(),
                    "status": "running",
                    "daemon_mode": daemon_mode,
                    "last_activity": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "message": "Harvester started successfully",
                    "pid": process.pid
                }
            else:
                # Process failed to start
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "message": f"Failed to start harvester: {stderr}",
                    "stdout": stdout,
                    "stderr": stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error starting harvester: {e}"
            }
    
    def stop_harvester(self) -> Dict:
        """Stop the harvester gracefully."""
        if not self.is_running():
            return {
                "success": False,
                "message": "Harvester is not running"
            }
        
        try:
            pid = self._get_pid()
            if not pid:
                return {
                    "success": False,
                    "message": "Could not determine harvester PID"
                }
            
            # Try graceful shutdown first
            if platform.system() == "Windows":
                subprocess.run(['taskkill', '/PID', str(pid), '/F'], 
                             capture_output=True, text=True)
            else:
                os.kill(pid, signal.SIGTERM)
                
                # Wait for graceful shutdown
                for _ in range(10):
                    if not self._is_process_running(pid):
                        break
                    time.sleep(1)
                
                # Force kill if still running
                if self._is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
            
            # Clean up
            self._cleanup_pid_file()
            self._update_status({
                "status": "stopped",
                "stop_time": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "message": "Harvester stopped successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping harvester: {e}"
            }
    
    def get_status(self) -> Dict:
        """Get current harvester status."""
        if not self.is_running():
            return {
                "running": False,
                "status": "stopped"
            }
        
        # Load status from file
        status = self._load_status()
        if not status:
            status = {
                "running": True,
                "status": "running",
                "pid": self._get_pid()
            }
        
        status["running"] = True
        return status
    
    def get_recent_logs(self, lines: int = 50) -> List[str]:
        """Get recent log entries."""
        if not self.log_file.exists():
            return []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception:
            return []
    
    def follow_logs(self, callback=None):
        """Follow logs in real-time."""
        if not self.log_file.exists():
            return
        
        def follow():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        if callback:
                            callback(line.strip())
                        else:
                            print(line.strip())
                    else:
                        time.sleep(0.1)
        
        # Start following in a separate thread
        thread = threading.Thread(target=follow, daemon=True)
        thread.start()
        return thread
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True)
                return str(pid) in result.stdout
            else:
                os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
                return True
        except (OSError, subprocess.SubprocessError):
            return False
    
    def _detect_harvester_process(self) -> bool:
        """Detect harvester process using system commands."""
        try:
            # Fixed: Use psutil for more reliable cross-platform process detection
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('harvester_v2.py' in arg for arg in cmdline):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            return False
        except ImportError:
            # Fallback to platform-specific commands if psutil not available
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                                          capture_output=True, text=True)
                    return result.returncode == 0 and 'harvester_v2.py' in result.stdout
                else:
                    result = subprocess.run(['pgrep', '-f', 'harvester_v2.py'], 
                                          capture_output=True, text=True)
                    return result.returncode == 0
            except Exception:
                return False
    
    def _get_pid(self) -> Optional[int]:
        """Get PID from PID file."""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, FileNotFoundError):
                pass
        return None
    
    def _cleanup_pid_file(self):
        """Remove PID file."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception:
            pass
    
    def _update_status(self, status_update: Dict):
        """Update status file."""
        try:
            current_status = self._load_status() or {}
            current_status.update(status_update)
            
            with open(self.status_file, 'w') as f:
                json.dump(current_status, f, indent=2)
        except Exception:
            pass
    
    def _load_status(self) -> Optional[Dict]:
        """Load status from file."""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None 