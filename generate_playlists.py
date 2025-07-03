#!/usr/bin/env python3
"""
Project 5001 - Playlist Generator
Generates smart playlists from harvested music files.
"""

import os
import sqlite3
import logging
import re  # Added for filename sanitization
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DEST_DIR = Path(os.getenv('DEST_DIR', './Project5001/Harvest'))
PLAYLISTS_DIR = Path('./Project5001/Playlists')

# Fixed: Ensure logs directory exists before setting up logging
logs_dir = Path('./Project5001/Logs')
logs_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./Project5001/Logs/playlist_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PlaylistGenerator:
    def __init__(self):
        self.db_path = Path('./Project5001/harvest.db')
        self.dest_dir = DEST_DIR
        self.playlists_dir = PLAYLISTS_DIR
        self.playlists_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.playlists_dir / 'ByMonth').mkdir(exist_ok=True)
        (self.playlists_dir / 'ByArtist').mkdir(exist_ok=True)
        
        # Check which date column exists in the database
        self._date_column = self._get_date_column()
    
    def _get_date_column(self) -> str:
        """Determine which date column exists in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('PRAGMA table_info(videos)')
            columns = [row[1] for row in cursor.fetchall()]
            conn.close()
            
            # Return appropriate column name based on what exists
            return 'ts' if 'ts' in columns else 'download_date'
        except Exception:
            # Default to download_date for new databases
            return 'download_date'
    
    def get_all_tracks(self) -> List[Dict]:
        """Get all tracks from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT id, title, artist, filename, {self._date_column} 
            FROM videos 
            ORDER BY {self._date_column} ASC
        ''')
        
        tracks = []
        for row in cursor.fetchall():
            tracks.append({
                'id': row[0],
                'title': row[1],
                'artist': row[2],
                'filename': row[3],
                'date': row[4]  # Fixed: unified date field name
            })
        
        conn.close()
        return tracks
    
    def get_recent_tracks(self, days: int = 30) -> List[Dict]:
        """Get tracks added in the last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute(f'''
            SELECT id, title, artist, filename, {self._date_column} 
            FROM videos 
            WHERE {self._date_column} >= ?
            ORDER BY {self._date_column} DESC
        ''', (cutoff_date.isoformat(),))
        
        tracks = []
        for row in cursor.fetchall():
            tracks.append({
                'id': row[0],
                'title': row[1],
                'artist': row[2],
                'filename': row[3],
                'date': row[4]  # Fixed: unified date field name
            })
        
        conn.close()
        return tracks
    
    def get_tracks_by_artist(self, artist: str) -> List[Dict]:
        """Get all tracks by a specific artist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT id, title, artist, filename, {self._date_column} 
            FROM videos 
            WHERE artist LIKE ?
            ORDER BY {self._date_column} ASC
        ''', (f'%{artist}%',))
        
        tracks = []
        for row in cursor.fetchall():
            tracks.append({
                'id': row[0],
                'title': row[1],
                'artist': row[2],
                'filename': row[3],
                'date': row[4]  # Fixed: unified date field name
            })
        
        conn.close()
        return tracks
    
    def get_tracks_by_month(self, year: int, month: int) -> List[Dict]:
        """Get tracks added in a specific month."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        cursor.execute(f'''
            SELECT id, title, artist, filename, {self._date_column} 
            FROM videos 
            WHERE {self._date_column} >= ? AND {self._date_column} < ?
            ORDER BY {self._date_column} ASC
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        tracks = []
        for row in cursor.fetchall():
            tracks.append({
                'id': row[0],
                'title': row[1],
                'artist': row[2],
                'filename': row[3],
                'date': row[4]  # Fixed: unified date field name
            })
        
        conn.close()
        return tracks
    
    def write_playlist(self, tracks: List[Dict], playlist_path: Path, title: str = ""):
        """Write tracks to M3U playlist file."""
        if not tracks:
            logger.warning(f"No tracks to write to {playlist_path}")
            return
        
        with open(playlist_path, 'w', encoding='utf-8') as f:
            f.write(f"#EXTM3U\n")
            f.write(f"# {title}\n")
            f.write(f"# Generated by Project 5001 on {datetime.now().isoformat()}\n")
            f.write(f"# Total tracks: {len(tracks)}\n\n")
            
            for track in tracks:
                # Write extended info
                f.write(f"#EXTINF:-1,{track['artist']} - {track['title']}\n")
                # Write file path relative to playlist location
                relative_path = self.dest_dir / track['filename']
                f.write(f"{relative_path}\n")
        
        logger.info(f"Generated playlist: {playlist_path} ({len(tracks)} tracks)")
    
    def generate_main_archive(self):
        """Generate main archive playlist with all tracks."""
        tracks = self.get_all_tracks()
        playlist_path = self.playlists_dir / 'MainArchive.m3u'
        self.write_playlist(tracks, playlist_path, "Project 5001 - Complete Archive")
    
    def generate_new_additions(self, days: int = 30):
        """Generate playlist of recent additions."""
        tracks = self.get_recent_tracks(days)
        playlist_path = self.playlists_dir / 'NewAdditions.m3u'
        self.write_playlist(tracks, playlist_path, f"Project 5001 - New Additions (Last {days} days)")
    
    def generate_monthly_playlists(self, months_back: int = 6):
        """Generate monthly playlists for the last N months."""
        now = datetime.now()
        
        for i in range(months_back):
            # Calculate month
            if now.month - i <= 0:
                year = now.year - 1
                month = 12 + (now.month - i)
            else:
                year = now.year
                month = now.month - i
            
            tracks = self.get_tracks_by_month(year, month)
            if tracks:
                month_name = datetime(year, month, 1).strftime('%Y-%m')
                playlist_path = self.playlists_dir / 'ByMonth' / f'{month_name}.m3u'
                self.write_playlist(tracks, playlist_path, f"Project 5001 - {month_name}")
    
    def generate_artist_playlists(self, min_tracks: int = 3):
        """Generate playlists for artists with multiple tracks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get artists with multiple tracks
        cursor.execute('''
            SELECT artist, COUNT(*) as track_count
            FROM videos 
            GROUP BY artist 
            HAVING COUNT(*) >= ?
            ORDER BY track_count DESC
        ''', (min_tracks,))
        
        artists = cursor.fetchall()
        conn.close()
        
        for artist, track_count in artists:
            tracks = self.get_tracks_by_artist(artist)
            if tracks:
                # Enhanced artist name sanitization for cross-platform filenames
                safe_artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_artist = re.sub(r'\s+', ' ', safe_artist)  # Normalize whitespace
                safe_artist = safe_artist[:50] if len(safe_artist) > 50 else safe_artist  # Limit length
                safe_artist = safe_artist or "Unknown_Artist"  # Fallback for empty names
                
                playlist_path = self.playlists_dir / 'ByArtist' / f'{safe_artist}.m3u'
                self.write_playlist(tracks, playlist_path, f"Project 5001 - {artist} ({track_count} tracks)")
    
    def generate_favorites_playlist(self, top_n: int = 100):
        """Generate a 'favorites' playlist based on most recent additions."""
        tracks = self.get_recent_tracks(7)  # Last week
        if len(tracks) > top_n:
            tracks = tracks[:top_n]
        
        playlist_path = self.playlists_dir / 'Favorites.m3u'
        self.write_playlist(tracks, playlist_path, f"Project 5001 - Recent Favorites (Top {len(tracks)})")
    
    def generate_all_playlists(self):
        """Generate all playlists."""
        logger.info("Starting playlist generation")
        
        try:
            # Main playlists
            self.generate_main_archive()
            self.generate_new_additions()
            self.generate_favorites_playlist()
            
            # Monthly playlists
            self.generate_monthly_playlists()
            
            # Artist playlists
            self.generate_artist_playlists()
            
            logger.info("Playlist generation completed successfully")
            
        except Exception as e:
            logger.error(f"Error generating playlists: {e}")
            raise

def main():
    """Main entry point."""
    generator = PlaylistGenerator()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'main':
            generator.generate_main_archive()
        elif command == 'new':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            generator.generate_new_additions(days)
        elif command == 'monthly':
            months = int(sys.argv[2]) if len(sys.argv) > 2 else 6
            generator.generate_monthly_playlists(months)
        elif command == 'artists':
            min_tracks = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            generator.generate_artist_playlists(min_tracks)
        elif command == 'favorites':
            top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            generator.generate_favorites_playlist(top_n)
        else:
            print("Unknown command. Use: main, new, monthly, artists, favorites, or all")
    else:
        # Generate all playlists
        generator.generate_all_playlists()

if __name__ == '__main__':
    main() 