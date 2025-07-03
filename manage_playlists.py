#!/usr/bin/env python3
"""
Project 5001 - YouTube Playlist Manager
Standalone script for managing YouTube playlists that the harvester monitors.
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import NodeConfig
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the Project 5001 directory")
    sys.exit(1)

def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_playlist_info(playlist_url: str) -> dict:
    """Get information about a YouTube playlist."""
    try:
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--flat-playlist',
            '--dump-json',
            '--no-warnings',
            '--playlist-items', '1',  # Just get first video for playlist info
            playlist_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return None
        
        # Parse the first video to get playlist info
        lines = result.stdout.strip().split('\n')
        if not lines or not lines[0]:
            return None
        
        video_data = json.loads(lines[0])
        
        # Get playlist info from the video data
        playlist_info = {
            'title': video_data.get('playlist_title', 'Unknown'),
            'uploader': video_data.get('playlist_uploader', 'Unknown'),
            'video_count': video_data.get('playlist_count', 0),
            'playlist_id': video_data.get('playlist_id', 'Unknown')
        }
        
        return playlist_info
        
    except Exception as e:
        logging.error(f"Failed to get playlist info for {playlist_url}: {e}")
        return None

def list_playlists():
    """List all YouTube playlists currently being monitored."""
    print("\n📋 Current YouTube Playlists:")
    try:
        config = NodeConfig('main')
        playlist_urls = config.get('playlist_urls', [])
        
        if not playlist_urls:
            print("ℹ️  No YouTube playlists configured")
            return
        
        for i, url in enumerate(playlist_urls, 1):
            print(f"  {i}. {url}")
            
            # Try to get playlist info
            try:
                playlist_info = get_playlist_info(url)
                if playlist_info:
                    print(f"     📝 Title: {playlist_info.get('title', 'Unknown')}")
                    print(f"     👤 Channel: {playlist_info.get('uploader', 'Unknown')}")
                    print(f"     📊 Videos: {playlist_info.get('video_count', 'Unknown')}")
            except Exception as e:
                print(f"     ⚠️  Could not fetch playlist info: {e}")
            print()
            
    except Exception as e:
        print(f"❌ Failed to list playlists: {e}")

def add_playlist():
    """Add a new YouTube playlist to monitor."""
    print("\n➕ Add YouTube Playlist")
    print("Enter a YouTube playlist URL to start monitoring:")
    
    url = input("Playlist URL: ").strip()
    if not url:
        print("❌ No URL provided")
        return
    
    # Validate URL format
    if 'youtube.com/playlist' not in url:
        print("❌ Please enter a valid YouTube playlist URL")
        return
    
    try:
        config = NodeConfig('main')
        playlist_urls = config.get('playlist_urls', [])
        
        # Check if already exists
        if url in playlist_urls:
            print("⚠️  This playlist is already being monitored")
            return
        
        # Test the playlist URL
        print("🔍 Testing playlist URL...")
        playlist_info = get_playlist_info(url)
        if not playlist_info:
            print("❌ Could not access playlist. Please check the URL and try again.")
            return
        
        # Add to configuration
        playlist_urls.append(url)
        config.set('playlist_urls', playlist_urls)
        config.save_config()
        
        print("✅ Playlist added successfully!")
        print(f"📝 Title: {playlist_info.get('title', 'Unknown')}")
        print(f"👤 Channel: {playlist_info.get('uploader', 'Unknown')}")
        print(f"📊 Videos: {playlist_info.get('video_count', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Failed to add playlist: {e}")

def remove_playlist():
    """Remove a YouTube playlist from monitoring."""
    print("\n➖ Remove YouTube Playlist")
    try:
        config = NodeConfig('main')
        playlist_urls = config.get('playlist_urls', [])
        
        if not playlist_urls:
            print("ℹ️  No playlists configured")
            return
        
        print("Current playlists:")
        for i, url in enumerate(playlist_urls, 1):
            print(f"  {i}. {url}")
        
        choice = input("\nEnter playlist number to remove (or 'cancel'): ").strip()
        if choice.lower() == 'cancel':
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(playlist_urls):
                removed_url = playlist_urls.pop(index)
                config.set('playlist_urls', playlist_urls)
                config.save_config()
                print(f"✅ Removed playlist: {removed_url}")
            else:
                print("❌ Invalid playlist number")
        except ValueError:
            print("❌ Please enter a valid number")
            
    except Exception as e:
        print(f"❌ Failed to remove playlist: {e}")

def test_playlist():
    """Test a YouTube playlist URL to see if it's accessible."""
    print("\n🔍 Test YouTube Playlist URL")
    url = input("Enter playlist URL to test: ").strip()
    
    if not url:
        print("❌ No URL provided")
        return
    
    if 'youtube.com/playlist' not in url:
        print("❌ Please enter a valid YouTube playlist URL")
        return
    
    print("🔍 Testing playlist...")
    try:
        playlist_info = get_playlist_info(url)
        if playlist_info:
            print("✅ Playlist is accessible!")
            print(f"📝 Title: {playlist_info.get('title', 'Unknown')}")
            print(f"👤 Channel: {playlist_info.get('uploader', 'Unknown')}")
            print(f"📊 Videos: {playlist_info.get('video_count', 'Unknown')}")
            print(f"🔗 URL: {url}")
        else:
            print("❌ Could not access playlist")
    except Exception as e:
        print(f"❌ Error testing playlist: {e}")

def show_stats():
    """Show statistics for all monitored YouTube playlists."""
    print("\n📊 YouTube Playlist Statistics")
    try:
        config = NodeConfig('main')
        playlist_urls = config.get('playlist_urls', [])
        
        if not playlist_urls:
            print("ℹ️  No playlists configured")
            return
        
        total_videos = 0
        accessible_playlists = 0
        
        for i, url in enumerate(playlist_urls, 1):
            print(f"\n📋 Playlist {i}: {url}")
            try:
                playlist_info = get_playlist_info(url)
                if playlist_info:
                    accessible_playlists += 1
                    video_count = playlist_info.get('video_count', 0)
                    total_videos += video_count
                    print(f"   ✅ Accessible")
                    print(f"   📝 Title: {playlist_info.get('title', 'Unknown')}")
                    print(f"   👤 Channel: {playlist_info.get('uploader', 'Unknown')}")
                    print(f"   📊 Videos: {video_count}")
                else:
                    print(f"   ❌ Not accessible")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n📈 Summary:")
        print(f"   Total playlists: {len(playlist_urls)}")
        print(f"   Accessible playlists: {accessible_playlists}")
        print(f"   Total videos: {total_videos}")
        
    except Exception as e:
        print(f"❌ Failed to get playlist statistics: {e}")

def show_help():
    """Show help information."""
    print("""
🎧 Project 5001 - YouTube Playlist Manager
==========================================

This script helps you manage the YouTube playlists that Project 5001 monitors
for downloading music.

Available commands:
  list     - Show all currently monitored playlists
  add      - Add a new playlist to monitor
  remove   - Remove a playlist from monitoring
  test     - Test if a playlist URL is accessible
  stats    - Show statistics for all playlists
  help     - Show this help message

Examples:
  python manage_playlists.py list
  python manage_playlists.py add
  python manage_playlists.py test
""")

def main():
    """Main entry point."""
    setup_logging()
    
    if len(sys.argv) < 2:
        print("🎧 Project 5001 - YouTube Playlist Manager")
        print("=" * 50)
        print("Available commands: list, add, remove, test, stats, help")
        print("Use 'python manage_playlists.py help' for more information")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_playlists()
    elif command == 'add':
        add_playlist()
    elif command == 'remove':
        remove_playlist()
    elif command == 'test':
        test_playlist()
    elif command == 'stats':
        show_stats()
    elif command == 'help':
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python manage_playlists.py help' for available commands")

if __name__ == '__main__':
    main() 