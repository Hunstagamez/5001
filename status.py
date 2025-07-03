#!/usr/bin/env python3
"""
Project 5001 - Status Checker
Monitor the health and statistics of your music archive.
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Project5001Status:
    def __init__(self):
        self.db_path = Path('./Project5001/harvest.db')
        self.dest_dir = Path(os.getenv('DEST_DIR', './Project5001/Harvest'))
        self.playlists_dir = Path('./Project5001/Playlists')
        self.logs_dir = Path('./Project5001/Logs')
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        if not self.db_path.exists():
            return {"error": "Database not found"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total tracks
        cursor.execute('SELECT COUNT(*) FROM videos')
        total_tracks = cursor.fetchone()[0]
        
        # Recent tracks (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM videos WHERE download_date >= ?', (week_ago,))
        recent_tracks = cursor.fetchone()[0]
        
        # Top artists
        cursor.execute('''
            SELECT artist, COUNT(*) as count 
            FROM videos 
            GROUP BY artist 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        top_artists = cursor.fetchall()
        
        # Oldest and newest tracks
        cursor.execute('SELECT MIN(download_date), MAX(download_date) FROM videos')
        oldest, newest = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_tracks": total_tracks,
            "recent_tracks": recent_tracks,
            "top_artists": top_artists,
            "oldest_track": oldest,
            "newest_track": newest
        }
    
    def get_file_stats(self) -> Dict:
        """Get file system statistics."""
        if not self.dest_dir.exists():
            return {"error": "Harvest directory not found"}
        
        # Count audio files
        audio_files = list(self.dest_dir.glob('*.mp3'))
        total_size = sum(f.stat().st_size for f in audio_files)
        
        # Get file size distribution
        size_ranges = {
            "0-5MB": 0,
            "5-10MB": 0,
            "10-15MB": 0,
            "15MB+": 0
        }
        
        for file in audio_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            if size_mb < 5:
                size_ranges["0-5MB"] += 1
            elif size_mb < 10:
                size_ranges["5-10MB"] += 1
            elif size_mb < 15:
                size_ranges["10-15MB"] += 1
            else:
                size_ranges["15MB+"] += 1
        
        return {
            "total_files": len(audio_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "size_distribution": size_ranges,
            "average_size_mb": round(total_size / len(audio_files) / (1024 * 1024), 2) if audio_files else 0
        }
    
    def get_playlist_stats(self) -> Dict:
        """Get playlist statistics."""
        if not self.playlists_dir.exists():
            return {"error": "Playlists directory not found"}
        
        playlists = list(self.playlists_dir.rglob('*.m3u'))
        
        playlist_info = []
        for playlist in playlists:
            try:
                with open(playlist, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Count non-comment lines (actual tracks)
                    track_count = len([line for line in lines if not line.startswith('#') and line.strip()])
                    playlist_info.append({
                        "name": playlist.name,
                        "path": str(playlist.relative_to(self.playlists_dir)),
                        "tracks": track_count
                    })
            except Exception as e:
                playlist_info.append({
                    "name": playlist.name,
                    "error": str(e)
                })
        
        return {
            "total_playlists": len(playlists),
            "playlists": playlist_info
        }
    
    def get_log_stats(self) -> Dict:
        """Get log file statistics."""
        if not self.logs_dir.exists():
            return {"error": "Logs directory not found"}
        
        log_files = list(self.logs_dir.glob('*.log'))
        
        log_info = []
        for log_file in log_files:
            try:
                stat = log_file.stat()
                log_info.append({
                    "name": log_file.name,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                log_info.append({
                    "name": log_file.name,
                    "error": str(e)
                })
        
        return {
            "total_logs": len(log_files),
            "logs": log_info
        }
    
    def check_syncthing_status(self) -> Dict:
        """Check Syncthing status."""
        try:
            import requests
            from dotenv import load_dotenv
            load_dotenv()
            
            api_url = os.getenv('SYNCTHING_API_URL')
            api_key = os.getenv('SYNCTHING_API_KEY')
            
            if not api_url or not api_key:
                return {"status": "not_configured"}
            
            headers = {'X-API-Key': api_key}
            response = requests.get(f"{api_url}/rest/system/status", headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "connected",
                    "version": data.get('version'),
                    "uptime": data.get('uptime')
                }
            else:
                return {"status": "error", "code": response.status_code}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_full_status(self) -> Dict:
        """Get complete system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "database": self.get_database_stats(),
            "files": self.get_file_stats(),
            "playlists": self.get_playlist_stats(),
            "logs": self.get_log_stats(),
            "syncthing": self.check_syncthing_status()
        }
    
    def print_status(self):
        """Print formatted status to console."""
        status = self.get_full_status()
        
        print("🎧 Project 5001 Status Report")
        print("=" * 50)
        print(f"Generated: {status['timestamp']}")
        print()
        
        # Database stats
        db = status['database']
        if 'error' not in db:
            print("📊 Database Statistics:")
            print(f"  Total tracks: {db['total_tracks']:,}")
            print(f"  Recent (7 days): {db['recent_tracks']:,}")
            if db['oldest_track'] and db['newest_track']:
                print(f"  Date range: {db['oldest_track'][:10]} to {db['newest_track'][:10]}")
            print()
            
            if db['top_artists']:
                print("🎤 Top Artists:")
                for artist, count in db['top_artists'][:5]:
                    print(f"  {artist}: {count} tracks")
                print()
        else:
            print(f"❌ Database: {db['error']}")
            print()
        
        # File stats
        files = status['files']
        if 'error' not in files:
            print("📁 File Statistics:")
            print(f"  Total files: {files['total_files']:,}")
            print(f"  Total size: {files['total_size_mb']:.1f} MB")
            print(f"  Average size: {files['average_size_mb']:.1f} MB")
            print()
        else:
            print(f"❌ Files: {files['error']}")
            print()
        
        # Playlist stats
        playlists = status['playlists']
        if 'error' not in playlists:
            print("📋 Playlists:")
            print(f"  Total playlists: {playlists['total_playlists']}")
            for playlist in playlists['playlists'][:5]:  # Show first 5
                if 'error' not in playlist:
                    print(f"  {playlist['name']}: {playlist['tracks']} tracks")
            print()
        else:
            print(f"❌ Playlists: {playlists['error']}")
            print()
        
        # Syncthing status
        syncthing = status['syncthing']
        print("🔄 Syncthing Status:")
        if syncthing['status'] == 'connected':
            print(f"  ✅ Connected (v{syncthing.get('version', 'unknown')})")
        elif syncthing['status'] == 'not_configured':
            print("  ⚠️  Not configured")
        else:
            print(f"  ❌ Error: {syncthing.get('message', 'Unknown error')}")
        print()
        
        # Health summary
        print("🏥 Health Summary:")
        issues = []
        
        if 'error' in db:
            issues.append("Database not found")
        elif db['total_tracks'] == 0:
            issues.append("No tracks harvested")
        
        if 'error' in files:
            issues.append("Harvest directory not found")
        elif files['total_files'] == 0:
            issues.append("No audio files found")
        
        if syncthing['status'] == 'error':
            issues.append("Syncthing connection failed")
        
        if issues:
            print("  ❌ Issues detected:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("  ✅ All systems operational")
        
        print()

def main():
    """Main entry point."""
    status_checker = Project5001Status()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        # Output JSON for programmatic use
        import json
        print(json.dumps(status_checker.get_full_status(), indent=2))
    else:
        # Print formatted status
        status_checker.print_status()

if __name__ == '__main__':
    main() 