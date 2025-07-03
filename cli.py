#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project 5001 - Unified CLI Menu System
Provides an interactive command-line interface for all Project 5001 operations.
"""

import os
import sys
import subprocess
import json
import time
import platform  # Added for cross-platform compatibility
import psutil  # Cross-platform process utilities
from pathlib import Path
from typing import Dict, List, Optional
import logging

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

class Project5001CLI:
    def __init__(self):
        self.status_checker = Project5001Status()
        self.config = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for CLI operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Project5001/Logs/cli.log'),
                logging.StreamHandler()
            ]
        )
    
    def print_banner(self):
        """Print Project 5001 banner."""
        print("🎧" + "="*60)
        print("   PROJECT 5001 - UNIFIED CLI MENU")
        print("   Taking back control of your music collection")
        print("="*60 + "🎧")
        print()
    
    def get_main_menu(self) -> List[Dict]:
        """Get main menu options."""
        return [
            {"id": "1", "title": "🎵 Harvester Control", "action": self.harvester_menu},
            {"id": "2", "title": "📋 Playlist Management", "action": self.playlist_menu},
            {"id": "3", "title": "📊 System Status", "action": self.status_menu},
            {"id": "4", "title": "📁 File Operations", "action": self.file_menu},
            {"id": "5", "title": "⚙️  Configuration", "action": self.config_menu},
            {"id": "6", "title": "📝 Logs & Debugging", "action": self.logs_menu},
            {"id": "7", "title": "🔄 Syncthing Operations", "action": self.syncthing_menu},
            {"id": "8", "title": "❓ Help & Documentation", "action": self.help_menu},
            {"id": "0", "title": "🚪 Exit", "action": self.exit_cli}
        ]
    
    def show_menu(self, title: str, options: List[Dict], back_action=None):
        """Display a menu with options."""
        while True:
            print(f"\n{title}")
            print("=" * len(title))
            
            for option in options:
                print(f"{option['id']}. {option['title']}")
            
            if back_action:
                print("b. Back to previous menu")
            
            choice = input(f"\nEnter your choice: ").strip().lower()
            
            if choice == 'b' and back_action:
                back_action()
                return
            
            # Find and execute the chosen action
            for option in options:
                if option['id'] == choice:
                    option['action']()
                    return
            
            print("❌ Invalid choice. Please try again.")
    
    def harvester_menu(self):
        """Harvester control menu."""
        options = [
            {"id": "1", "title": "▶️  Start Harvester (Daemon)", "action": self.start_harvester_daemon},
            {"id": "2", "title": "⏸️  Stop Harvester", "action": self.stop_harvester},
            {"id": "3", "title": "🔄 Run Single Harvest Cycle", "action": self.run_single_harvest},
            {"id": "4", "title": "📊 Harvester Status", "action": self.check_harvester_status},
            {"id": "5", "title": "🔧 Test Configuration", "action": self.test_harvester_config}
        ]
        
        self.show_menu("🎵 Harvester Control", options, self.main_menu)
    
    def playlist_menu(self):
        """Playlist management menu."""
        options = [
            {"id": "1", "title": "📋 Generate All Playlists", "action": self.generate_all_playlists},
            {"id": "2", "title": "📁 Main Archive Playlist", "action": self.generate_main_archive},
            {"id": "3", "title": "🆕 Recent Additions Playlist", "action": self.generate_recent_playlist},
            {"id": "4", "title": "📅 Monthly Playlists", "action": self.generate_monthly_playlists},
            {"id": "5", "title": "🎤 Artist Playlists", "action": self.generate_artist_playlists},
            {"id": "6", "title": "⭐ Favorites Playlist", "action": self.generate_favorites_playlist},
            {"id": "7", "title": "📂 List Existing Playlists", "action": self.list_playlists}
        ]
        
        self.show_menu("📋 Playlist Management", options, self.main_menu)
    
    def status_menu(self):
        """System status menu."""
        options = [
            {"id": "1", "title": "📊 Full System Status", "action": self.show_full_status},
            {"id": "2", "title": "📈 Database Statistics", "action": self.show_db_stats},
            {"id": "3", "title": "📁 File Statistics", "action": self.show_file_stats},
            {"id": "4", "title": "🔄 Syncthing Status", "action": self.show_syncthing_status},
            {"id": "5", "title": "🎤 Top Artists", "action": self.show_top_artists},
            {"id": "6", "title": "📊 JSON Status Output", "action": self.show_json_status}
        ]
        
        self.show_menu("📊 System Status", options, self.main_menu)
    
    def file_menu(self):
        """File operations menu."""
        options = [
            {"id": "1", "title": "🔍 Search Tracks", "action": self.search_tracks},
            {"id": "2", "title": "📁 Browse Harvest Directory", "action": self.browse_harvest_dir},
            {"id": "3", "title": "🧹 Clean Orphaned Files", "action": self.clean_orphaned_files},
            {"id": "4", "title": "📊 Storage Analysis", "action": self.storage_analysis}
        ]
        
        self.show_menu("📁 File Operations", options, self.main_menu)
    
    def config_menu(self):
        """Configuration menu."""
        options = [
            {"id": "1", "title": "⚙️  Show Current Config", "action": self.show_config},
            {"id": "2", "title": "🔧 Edit Configuration", "action": self.edit_config},
            {"id": "3", "title": "🔄 Reload Configuration", "action": self.reload_config},
            {"id": "4", "title": "📋 Validate Configuration", "action": self.validate_config}
        ]
        
        self.show_menu("⚙️  Configuration", options, self.main_menu)
    
    def logs_menu(self):
        """Logs and debugging menu."""
        options = [
            {"id": "1", "title": "📝 View Recent Logs", "action": self.view_recent_logs},
            {"id": "2", "title": "🔍 Search Logs", "action": self.search_logs},
            {"id": "3", "title": "📊 Log Statistics", "action": self.log_statistics},
            {"id": "4", "title": "🧹 Clear Old Logs", "action": self.clear_old_logs}
        ]
        
        self.show_menu("📝 Logs & Debugging", options, self.main_menu)
    
    def syncthing_menu(self):
        """Syncthing operations menu."""
        options = [
            {"id": "1", "title": "🔄 Trigger Rescan", "action": self.trigger_syncthing_rescan},
            {"id": "2", "title": "📊 Sync Status", "action": self.show_sync_status},
            {"id": "3", "title": "🔗 Test Connection", "action": self.test_syncthing_connection}
        ]
        
        self.show_menu("🔄 Syncthing Operations", options, self.main_menu)
    
    def help_menu(self):
        """Help and documentation menu."""
        options = [
            {"id": "1", "title": "📖 Quick Start Guide", "action": self.show_quick_start},
            {"id": "2", "title": "🔧 Setup Instructions", "action": self.show_setup_instructions},
            {"id": "3", "title": "📋 Available Commands", "action": self.show_available_commands},
            {"id": "4", "title": "❓ Troubleshooting", "action": self.show_troubleshooting}
        ]
        
        self.show_menu("❓ Help & Documentation", options, self.main_menu)
    
    # Harvester Actions
    def start_harvester_daemon(self):
        """Start harvester in daemon mode."""
        print("\n🔄 Starting Project 5001 Harvester in daemon mode...")
        try:
            # Check if already running
            if self.is_harvester_running():
                print("⚠️  Harvester is already running!")
                return
            
            # Start harvester
            process = subprocess.Popen([
                sys.executable, 'harvester_v2.py', 'main', '--daemon'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("✅ Harvester started successfully!")
            print(f"Process ID: {process.pid}")
            print("Check logs with: python cli.py -> Logs -> View Recent Logs")
            
        except Exception as e:
            print(f"❌ Failed to start harvester: {e}")
    
    def stop_harvester(self):
        """Stop harvester daemon."""
        print("\n⏹️  Stopping Project 5001 Harvester...")
        try:
            # Find harvester processes (cross-platform)
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
            print(f"❌ Failed to stop harvester: {e}")
    
    def run_single_harvest(self):
        """Run a single harvest cycle."""
        print("\n🔄 Running single harvest cycle...")
        try:
            result = subprocess.run([
                sys.executable, 'harvester_v2.py', 'main'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Harvest cycle completed successfully!")
                print(result.stdout)
            else:
                print("❌ Harvest cycle failed!")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Failed to run harvest cycle: {e}")
    
    def check_harvester_status(self):
        """Check if harvester is running."""
        print("\n📊 Checking harvester status...")
        if self.is_harvester_running():
            print("✅ Harvester is running")
        else:
            print("❌ Harvester is not running")
    
    def test_harvester_config(self):
        """Test harvester configuration."""
        print("\n🔧 Testing harvester configuration...")
        try:
            config = NodeConfig('main')
            if config.validate_config():
                print("✅ Configuration is valid")
            else:
                print("❌ Configuration has errors")
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
    
    def is_harvester_running(self) -> bool:
        """Check if harvester process is running (cross-platform)."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'harvester_v2.py' in ' '.join(proc.info['cmdline'] or []):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False
    
    # Playlist Actions
    def generate_all_playlists(self):
        """Generate all playlists."""
        print("\n📋 Generating all playlists...")
        try:
            generator = PlaylistGenerator()
            generator.generate_all_playlists()
            print("✅ All playlists generated successfully!")
        except Exception as e:
            print(f"❌ Failed to generate playlists: {e}")
    
    def generate_main_archive(self):
        """Generate main archive playlist."""
        print("\n📁 Generating main archive playlist...")
        try:
            generator = PlaylistGenerator()
            generator.generate_main_archive()
            print("✅ Main archive playlist generated!")
        except Exception as e:
            print(f"❌ Failed to generate main archive: {e}")
    
    def generate_recent_playlist(self):
        """Generate recent additions playlist."""
        days = input("Enter number of days (default 30): ").strip()
        days = int(days) if days.isdigit() else 30
        
        print(f"\n🆕 Generating recent additions playlist (last {days} days)...")
        try:
            generator = PlaylistGenerator()
            generator.generate_new_additions(days)
            print("✅ Recent additions playlist generated!")
        except Exception as e:
            print(f"❌ Failed to generate recent playlist: {e}")
    
    def generate_monthly_playlists(self):
        """Generate monthly playlists."""
        months = input("Enter number of months back (default 6): ").strip()
        months = int(months) if months.isdigit() else 6
        
        print(f"\n📅 Generating monthly playlists (last {months} months)...")
        try:
            generator = PlaylistGenerator()
            generator.generate_monthly_playlists(months)
            print("✅ Monthly playlists generated!")
        except Exception as e:
            print(f"❌ Failed to generate monthly playlists: {e}")
    
    def generate_artist_playlists(self):
        """Generate artist playlists."""
        min_tracks = input("Enter minimum tracks per artist (default 3): ").strip()
        min_tracks = int(min_tracks) if min_tracks.isdigit() else 3
        
        print(f"\n🎤 Generating artist playlists (min {min_tracks} tracks)...")
        try:
            generator = PlaylistGenerator()
            generator.generate_artist_playlists(min_tracks)
            print("✅ Artist playlists generated!")
        except Exception as e:
            print(f"❌ Failed to generate artist playlists: {e}")
    
    def generate_favorites_playlist(self):
        """Generate favorites playlist."""
        top_n = input("Enter number of tracks (default 100): ").strip()
        top_n = int(top_n) if top_n.isdigit() else 100
        
        print(f"\n⭐ Generating favorites playlist (top {top_n} tracks)...")
        try:
            generator = PlaylistGenerator()
            generator.generate_favorites_playlist(top_n)
            print("✅ Favorites playlist generated!")
        except Exception as e:
            print(f"❌ Failed to generate favorites playlist: {e}")
    
    def list_playlists(self):
        """List existing playlists."""
        print("\n📂 Existing playlists:")
        try:
            playlists_dir = Path("Project5001/Playlists")
            if not playlists_dir.exists():
                print("❌ Playlists directory not found")
                return
            
            playlists = list(playlists_dir.rglob('*.m3u'))
            if not playlists:
                print("ℹ️  No playlists found")
                return
            
            for playlist in sorted(playlists):
                size = playlist.stat().st_size
                print(f"  📄 {playlist.name} ({size:,} bytes)")
                
        except Exception as e:
            print(f"❌ Failed to list playlists: {e}")
    
    # Status Actions
    def show_full_status(self):
        """Show full system status."""
        print("\n📊 Full System Status:")
        self.status_checker.print_status()
    
    def show_db_stats(self):
        """Show database statistics."""
        print("\n📈 Database Statistics:")
        stats = self.status_checker.get_database_stats()
        
        if 'error' in stats:
            print(f"❌ {stats['error']}")
        else:
            print(f"Total tracks: {stats['total_tracks']:,}")
            print(f"Recent (7 days): {stats['recent_tracks']:,}")
            if stats['oldest_track'] and stats['newest_track']:
                print(f"Date range: {stats['oldest_track'][:10]} to {stats['newest_track'][:10]}")
            
            if stats['top_artists']:
                print("\nTop Artists:")
                for artist, count in stats['top_artists'][:10]:
                    print(f"  {artist}: {count} tracks")
    
    def show_file_stats(self):
        """Show file statistics."""
        print("\n📁 File Statistics:")
        stats = self.status_checker.get_file_stats()
        
        if 'error' in stats:
            print(f"❌ {stats['error']}")
        else:
            print(f"Total files: {stats['total_files']:,}")
            print(f"Total size: {stats['total_size_mb']:.1f} MB")
            print(f"Average size: {stats['average_size_mb']:.1f} MB")
    
    def show_syncthing_status(self):
        """Show Syncthing status."""
        print("\n🔄 Syncthing Status:")
        status = self.status_checker.check_syncthing_status()
        
        if status['status'] == 'connected':
            print(f"✅ Connected (v{status.get('version', 'unknown')})")
        elif status['status'] == 'not_configured':
            print("⚠️  Not configured")
        else:
            print(f"❌ Error: {status.get('message', 'Unknown error')}")
    
    def show_top_artists(self):
        """Show top artists."""
        print("\n🎤 Top Artists:")
        stats = self.status_checker.get_database_stats()
        
        if 'error' in stats or not stats['top_artists']:
            print("❌ No artist data available")
        else:
            for i, (artist, count) in enumerate(stats['top_artists'][:20], 1):
                print(f"{i:2d}. {artist}: {count} tracks")
    
    def show_json_status(self):
        """Show status in JSON format."""
        print("\n📊 JSON Status Output:")
        status = self.status_checker.get_full_status()
        print(json.dumps(status, indent=2))
    
    # File Operations
    def search_tracks(self):
        """Search for tracks."""
        query = input("Enter search term: ").strip()
        if not query:
            print("❌ No search term provided")
            return
        
        print(f"\n🔍 Searching for: '{query}'")
        try:
            # This would need to be implemented in the database module
            print("⚠️  Search functionality not yet implemented")
            print("Use the database directly or check the harvest directory")
        except Exception as e:
            print(f"❌ Search failed: {e}")
    
    def browse_harvest_dir(self):
        """Browse harvest directory."""
        print("\n📁 Harvest Directory Contents:")
        harvest_dir = Path("Project5001/Harvest")
        
        if not harvest_dir.exists():
            print("❌ Harvest directory not found")
            return
        
        files = list(harvest_dir.glob('*.mp3'))
        if not files:
            print("ℹ️  No MP3 files found")
            return
        
        print(f"Found {len(files)} MP3 files:")
        for file in sorted(files)[:20]:  # Show first 20
            size = file.stat().st_size / (1024 * 1024)  # MB
            print(f"  📄 {file.name} ({size:.1f} MB)")
        
        if len(files) > 20:
            print(f"  ... and {len(files) - 20} more files")
    
    def clean_orphaned_files(self):
        """Clean orphaned files."""
        print("\n🧹 Cleaning orphaned files...")
        print("⚠️  This feature is not yet implemented")
        print("Orphaned files are files in the harvest directory that aren't in the database")
    
    def storage_analysis(self):
        """Analyze storage usage."""
        print("\n📊 Storage Analysis:")
        stats = self.status_checker.get_file_stats()
        
        if 'error' in stats:
            print(f"❌ {stats['error']}")
            return
        
        print(f"Total storage used: {stats['total_size_mb']:.1f} MB")
        print(f"Average file size: {stats['average_size_mb']:.1f} MB")
        print(f"Total files: {stats['total_files']:,}")
        
        # Estimate storage for 5000 tracks
        estimated_5000 = stats['average_size_mb'] * 5000
        print(f"Estimated storage for 5000 tracks: {estimated_5000:.1f} MB")
    
    # Configuration Actions
    def show_config(self):
        """Show current configuration."""
        print("\n⚙️  Current Configuration:")
        try:
            config = NodeConfig('main')
            print(f"Role: {config.role}")
            print(f"Data directory: {config.config.get('data_dir', 'Not set')}")
            print(f"Harvest directory: {config.config.get('harvest_dir', 'Not set')}")
            print(f"Syncthing enabled: {config.config.get('syncthing.enabled', False)}")
            
            playlist_urls = config.config.get('playlist_urls', [])
            print(f"Playlist URLs: {len(playlist_urls)} configured")
            
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
    
    def edit_config(self):
        """Edit configuration."""
        print("\n🔧 Edit Configuration:")
        print("⚠️  Configuration editing not yet implemented")
        print("Edit the config files manually or run setup_project5001.py")
    
    def reload_config(self):
        """Reload configuration."""
        print("\n🔄 Reloading configuration...")
        try:
            self.config = NodeConfig('main')
            print("✅ Configuration reloaded")
        except Exception as e:
            print(f"❌ Failed to reload configuration: {e}")
    
    def validate_config(self):
        """Validate configuration."""
        print("\n📋 Validating configuration...")
        try:
            config = NodeConfig('main')
            if config.validate_config():
                print("✅ Configuration is valid")
            else:
                print("❌ Configuration has errors")
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
    
    # Logs Actions
    def view_recent_logs(self):
        """View recent logs."""
        print("\n📝 Recent Logs:")
        logs_dir = Path("Project5001/Logs")
        
        if not logs_dir.exists():
            print("❌ Logs directory not found")
            return
        
        log_files = list(logs_dir.glob('*.log'))
        if not log_files:
            print("ℹ️  No log files found")
            return
        
        # Show most recent log file
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        print(f"Latest log: {latest_log.name}")
        
        try:
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                print(f"Last 10 lines of {latest_log.name}:")
                print("-" * 50)
                for line in lines[-10:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"❌ Failed to read log: {e}")
    
    def search_logs(self):
        """Search logs."""
        query = input("Enter search term: ").strip()
        if not query:
            print("❌ No search term provided")
            return
        
        print(f"\n🔍 Searching logs for: '{query}'")
        print("⚠️  Log search not yet implemented")
        print("Use: grep -r 'query' Project5001/Logs/")
    
    def log_statistics(self):
        """Show log statistics."""
        print("\n📊 Log Statistics:")
        stats = self.status_checker.get_log_stats()
        
        if 'error' in stats:
            print(f"❌ {stats['error']}")
        else:
            print(f"Total log files: {stats['total_logs']}")
            for log in stats['logs']:
                print(f"  📄 {log['name']}: {log['size_mb']} MB")
    
    def clear_old_logs(self):
        """Clear old logs."""
        print("\n🧹 Clear Old Logs:")
        print("⚠️  Log clearing not yet implemented")
        print("Manually delete old log files from Project5001/Logs/")
    
    # Syncthing Actions
    def trigger_syncthing_rescan(self):
        """Trigger Syncthing rescan."""
        print("\n🔄 Triggering Syncthing rescan...")
        try:
            config = NodeConfig('main')
            if not config.get('syncthing.enabled'):
                print("❌ Syncthing not enabled")
                return
            
            # This would need to be implemented
            print("⚠️  Syncthing rescan not yet implemented")
            print("Use the Syncthing web interface or API directly")
            
        except Exception as e:
            print(f"❌ Failed to trigger rescan: {e}")
    
    def show_sync_status(self):
        """Show sync status."""
        print("\n📊 Sync Status:")
        status = self.status_checker.check_syncthing_status()
        self.show_syncthing_status()
    
    def test_syncthing_connection(self):
        """Test Syncthing connection."""
        print("\n🔗 Testing Syncthing connection...")
        status = self.status_checker.check_syncthing_status()
        
        if status['status'] == 'connected':
            print("✅ Syncthing connection successful")
        else:
            print(f"❌ Syncthing connection failed: {status.get('message', 'Unknown error')}")
    
    # Help Actions
    def show_quick_start(self):
        """Show quick start guide."""
        print("\n📖 Quick Start Guide:")
        print("1. Run setup: python setup_project5001.py")
        print("2. Start harvester: python cli.py -> Harvester -> Start Daemon")
        print("3. Check status: python cli.py -> Status -> Full System Status")
        print("4. Generate playlists: python cli.py -> Playlists -> Generate All")
        print("\nSee QUICK_START.md for detailed instructions")
    
    def show_setup_instructions(self):
        """Show setup instructions."""
        print("\n🔧 Setup Instructions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install ffmpeg and yt-dlp")
        print("3. Run setup: python setup_project5001.py")
        print("4. Configure Syncthing (if using distributed setup)")
        print("5. Add YouTube cookies to cookies.txt")
        print("\nSee README.md for full setup guide")
    
    def show_available_commands(self):
        """Show available commands."""
        print("\n📋 Available Commands:")
        print("Direct script execution:")
        print("  python harvester_v2.py main --daemon")
        print("  python generate_playlists.py all")
        print("  python status.py")
        print("  python setup_project5001.py")
        print("\nOr use this CLI menu for all operations!")
    
    def show_troubleshooting(self):
        """Show troubleshooting guide."""
        print("\n❓ Troubleshooting:")
        print("Common issues:")
        print("1. YouTube rate limiting: Check logs and wait")
        print("2. Syncthing not syncing: Check API key and folder ID")
        print("3. No downloads: Check playlist URLs and cookies")
        print("4. Database errors: Check file permissions")
        print("\nCheck logs in Project5001/Logs/ for detailed error messages")
    
    def main_menu(self):
        """Show main menu."""
        self.show_menu("🎧 Project 5001 - Main Menu", self.get_main_menu())
    
    def exit_cli(self):
        """Exit the CLI."""
        print("\n👋 Thanks for using Project 5001!")
        print("Keep fighting the good fight against playlist limits! 🎧")
        sys.exit(0)

def main():
    """Main entry point."""
    cli = Project5001CLI()
    cli.print_banner()
    cli.main_menu()

if __name__ == '__main__':
    main()