#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project 5001 - System Initializer
One-command setup and startup for the entire Project 5001 system.
"""

import os
import sys
import subprocess
import time
import json
import platform  # Added for cross-platform compatibility
import psutil  # Cross-platform process utilities (add to requirements)
from pathlib import Path
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from status import Project5001Status
    from config import NodeConfig
    from generate_playlists import PlaylistGenerator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the Project 5001 directory")
    sys.exit(1)

class Project5001Initializer:
    def __init__(self):
        self.status_checker = Project5001Status()
        self.config = None
        
    def print_banner(self):
        """Print Project 5001 banner."""
        print("🎧" + "="*60)
        print("   PROJECT 5001 - SYSTEM INITIALIZER")
        print("   One-command setup and startup")
        print("="*60 + "🎧")
        print()
    
    def check_system_health(self) -> Dict:
        """Check overall system health."""
        print("🔍 Checking system health...")
        
        health_report = {
            'database': False,
            'harvest_dir': False,
            'playlists_dir': False,
            'logs_dir': False,
            'config': False,
            'dependencies': False,
            'syncthing': False
        }
        
        # Check database
        try:
            stats = self.status_checker.get_database_stats()
            if 'error' not in stats:
                health_report['database'] = True
                print(f"✅ Database: {stats['total_tracks']} tracks")
            else:
                print(f"❌ Database: {stats['error']}")
        except Exception as e:
            print(f"❌ Database: {e}")
        
        # Check directories
        dirs_to_check = [
            ('Project5001/Harvest', 'harvest_dir'),
            ('Project5001/Playlists', 'playlists_dir'),
            ('Project5001/Logs', 'logs_dir')
        ]
        
        for dir_path, key in dirs_to_check:
            if Path(dir_path).exists():
                health_report[key] = True
                print(f"✅ {dir_path}: Found")
            else:
                print(f"❌ {dir_path}: Missing")
        
        # Check configuration
        try:
            self.config = NodeConfig('main')
            if self.config.validate_config():
                health_report['config'] = True
                print("✅ Configuration: Valid")
            else:
                print("❌ Configuration: Invalid")
        except Exception as e:
            print(f"❌ Configuration: {e}")
        
        # Check dependencies
        try:
            import yt_dlp
            import mutagen
            import requests
            health_report['dependencies'] = True
            print("✅ Dependencies: All installed")
        except ImportError as e:
            print(f"❌ Dependencies: Missing {e}")
        
        # Check ffmpeg
        try:
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path:
                print(f"✅ FFmpeg: {ffmpeg_path}")
            else:
                print("❌ FFmpeg: Not found")
                print("   Installing automatically...")
                try:
                    from ffmpeg_installer import FFmpegInstaller
                    installer = FFmpegInstaller()
                    if installer.install_ffmpeg():
                        print("✅ FFmpeg: Installed successfully")
                    else:
                        print("❌ FFmpeg: Automatic installation failed")
                except ImportError:
                    print("❌ FFmpeg: Installer not available")
        except Exception as e:
            print(f"❌ FFmpeg: {e}")
        
        # Check Syncthing
        try:
            syncthing_status = self.status_checker.check_syncthing_status()
            if syncthing_status['status'] == 'connected':
                health_report['syncthing'] = True
                print("✅ Syncthing: Connected")
            else:
                print(f"⚠️  Syncthing: {syncthing_status['status']}")
        except Exception as e:
            print(f"❌ Syncthing: {e}")
        
        return health_report
    
    def setup_system(self):
        """Run initial system setup."""
        print("\n🏗️  Running system setup...")
        
        # Check if setup has been run before
        if Path('config/main-node.json').exists():
            print("⚠️  Configuration already exists. Run setup again? (y/N): ", end="")
            if input().lower() != 'y':
                print("Setup cancelled.")
                return
        
        try:
            # Run the setup script
            result = subprocess.run([sys.executable, 'setup_project5001.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ System setup completed successfully!")
            else:
                print("❌ Setup failed:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Setup error: {e}")
    
    def start_services(self):
        """Start all Project 5001 services."""
        print("\n🚀 Starting Project 5001 services...")
        
        # Start harvester daemon
        print("Starting harvester daemon...")
        try:
            harvester_process = subprocess.Popen([
                sys.executable, 'harvester_v2.py', 'main', '--daemon'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"✅ Harvester started (PID: {harvester_process.pid})")
            
        except Exception as e:
            print(f"❌ Failed to start harvester: {e}")
        
        # Generate initial playlists
        print("Generating initial playlists...")
        try:
            generator = PlaylistGenerator()
            generator.generate_all_playlists()
            print("✅ Initial playlists generated")
        except Exception as e:
            print(f"❌ Failed to generate playlists: {e}")
        
        print("\n🎉 Project 5001 is now running!")
        print("Use 'python cli.py' to manage the system")
        print("Use 'python status.py' to check status")
    
    def stop_services(self):
        """Stop all Project 5001 services."""
        print("\n⏹️  Stopping Project 5001 services...")
        
        try:
            # Find and stop harvester processes (cross-platform)
            harvester_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'harvester_v2.py' in ' '.join(proc.info['cmdline'] or []):
                        harvester_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if harvester_processes:
                for proc in harvester_processes:
                    try:
                        proc.terminate()  # Graceful termination
                        proc.wait(timeout=5)  # Wait up to 5 seconds
                        print(f"✅ Stopped harvester process {proc.pid}")
                    except psutil.TimeoutExpired:
                        proc.kill()  # Force kill if needed
                        print(f"✅ Force stopped harvester process {proc.pid}")
                    except Exception as e:
                        print(f"⚠️  Could not stop process {proc.pid}: {e}")
            else:
                print("ℹ️  No harvester processes found")
                
        except Exception as e:
            print(f"❌ Failed to stop services: {e}")
    
    def restart_services(self):
        """Restart all Project 5001 services."""
        print("\n🔄 Restarting Project 5001 services...")
        self.stop_services()
        time.sleep(2)
        self.start_services()
    
    def quick_start(self):
        """Quick start - check health and start if ready."""
        print("\n⚡ Quick Start Mode")
        
        health = self.check_system_health()
        
        # Check if system is ready
        critical_checks = ['database', 'harvest_dir', 'config', 'dependencies']
        ready = all(health[check] for check in critical_checks)
        
        if ready:
            print("\n✅ System is ready! Starting services...")
            self.start_services()
        else:
            print("\n❌ System not ready. Issues found:")
            for check, status in health.items():
                if not status and check in critical_checks:
                    print(f"  - {check.replace('_', ' ').title()}")
            
            print("\nRun setup first: python initialiser.py --setup")
    
    def maintenance_mode(self):
        """Run maintenance tasks."""
        print("\n🔧 Maintenance Mode")
        
        tasks = [
            ("Generate playlists", self.generate_playlists),
            ("Check database integrity", self.check_database_integrity),
            ("Clean old logs", self.clean_old_logs),
            ("Update configuration", self.update_config),
            ("Test Syncthing connection", self.test_syncthing)
        ]
        
        print("Available maintenance tasks:")
        for i, (name, _) in enumerate(tasks, 1):
            print(f"{i}. {name}")
        print("0. Run all tasks")
        print("b. Back")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '0':
            for name, task in tasks:
                print(f"\n🔄 Running: {name}")
                task()
        elif choice.isdigit() and 1 <= int(choice) <= len(tasks):
            name, task = tasks[int(choice) - 1]
            print(f"\n🔄 Running: {name}")
            task()
        elif choice.lower() == 'b':
            return
        else:
            print("❌ Invalid choice")
    
    def generate_playlists(self):
        """Generate all playlists."""
        try:
            generator = PlaylistGenerator()
            generator.generate_all_playlists()
            print("✅ All playlists generated successfully!")
        except Exception as e:
            print(f"❌ Failed to generate playlists: {e}")
    
    def check_database_integrity(self):
        """Check database integrity."""
        try:
            stats = self.status_checker.get_database_stats()
            if 'error' not in stats:
                print(f"✅ Database integrity check passed")
                print(f"  Total tracks: {stats['total_tracks']}")
                print(f"  Recent tracks: {stats['recent_tracks']}")
            else:
                print(f"❌ Database integrity check failed: {stats['error']}")
        except Exception as e:
            print(f"❌ Database check failed: {e}")
    
    def clean_old_logs(self):
        """Clean old log files."""
        try:
            logs_dir = Path("Project5001/Logs")
            if not logs_dir.exists():
                print("ℹ️  No logs directory found")
                return
            
            # Keep logs from last 30 days
            cutoff_time = time.time() - (30 * 24 * 60 * 60)
            deleted_count = 0
            
            for log_file in logs_dir.glob('*.log'):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
            
            print(f"✅ Cleaned {deleted_count} old log files")
        except Exception as e:
            print(f"❌ Failed to clean logs: {e}")
    
    def update_config(self):
        """Update configuration."""
        print("⚠️  Configuration update not yet implemented")
        print("Edit config files manually or run setup_project5001.py")
    
    def test_syncthing(self):
        """Test Syncthing connection."""
        try:
            status = self.status_checker.check_syncthing_status()
            if status['status'] == 'connected':
                print("✅ Syncthing connection successful")
            else:
                print(f"❌ Syncthing connection failed: {status.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Syncthing test failed: {e}")
    
    def show_status(self):
        """Show system status."""
        print("\n📊 System Status:")
        self.status_checker.print_status()
    
    def show_help(self):
        """Show help information."""
        print("\n📖 Project 5001 Initializer Help")
        print("=" * 40)
        print("Commands:")
        print("  --setup      Run initial system setup")
        print("  --start      Start all services")
        print("  --stop       Stop all services")
        print("  --restart    Restart all services")
        print("  --status     Show system status")
        print("  --health     Check system health")
        print("  --maintenance Run maintenance tasks")
        print("  --quick      Quick start (check health and start if ready)")
        print("  --help       Show this help")
        print()
        print("Examples:")
        print("  python initialiser.py --setup")
        print("  python initialiser.py --quick")
        print("  python initialiser.py --status")
        print()
        print("After setup, use 'python cli.py' for full management interface")

def main():
    """Main entry point."""
    initializer = Project5001Initializer()
    
    if len(sys.argv) == 1:
        # Interactive mode
        initializer.print_banner()
        initializer.quick_start()
        return
    
    # Command line mode
    command = sys.argv[1]
    
    if command == '--setup':
        initializer.setup_system()
    elif command == '--start':
        initializer.start_services()
    elif command == '--stop':
        initializer.stop_services()
    elif command == '--restart':
        initializer.restart_services()
    elif command == '--status':
        initializer.show_status()
    elif command == '--health':
        initializer.check_system_health()
    elif command == '--maintenance':
        initializer.maintenance_mode()
    elif command == '--quick':
        initializer.quick_start()
    elif command == '--help':
        initializer.show_help()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use --help for available commands")

if __name__ == '__main__':
    main() 