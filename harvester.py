#!/usr/bin/env python3
"""
Project 5001 - YouTube Playlist Harvester
Core script that polls YouTube playlists, downloads new audio, tags & renames files.
"""

import os
import sqlite3
import json
import logging
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PLAYLIST_URL = os.getenv('PLAYLIST_URL')
DEST_DIR = Path(os.getenv('DEST_DIR', './Project5001/Harvest'))
AUDIO_FMT = os.getenv('AUDIO_FMT', 'mp3')
QUALITY = os.getenv('QUALITY', '0')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '3600'))  # 1 hour default
SYNCTHING_API_URL = os.getenv('SYNCTHING_API_URL', 'http://localhost:8384')
SYNCTHING_API_KEY = os.getenv('SYNCTHING_API_KEY')
SYNCTHING_FOLDER_ID = os.getenv('SYNCTHING_FOLDER_ID')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./Project5001/Logs/activity.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PlaylistHarvester:
    def __init__(self):
        self.db_path = Path('./Project5001/harvest.db')
        self.dest_dir = DEST_DIR
        self.dest_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = Path('./Project5001/Logs')
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for tracking harvested videos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT,
                filename TEXT,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def get_playlist_videos(self) -> List[Dict]:
        """Fetch playlist videos using yt-dlp."""
        try:
            cmd = [
                'yt-dlp',
                '--flat-playlist',
                '--dump-json',
                PLAYLIST_URL
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            videos = []
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    video_data = json.loads(line)
                    videos.append({
                        'id': video_data['id'],
                        'title': video_data['title'],
                        'uploader': video_data.get('uploader', 'Unknown Artist')
                    })
            
            logger.info(f"Found {len(videos)} videos in playlist")
            return videos
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch playlist: {e}")
            return []
    
    def get_unseen_videos(self, videos: List[Dict]) -> List[Dict]:
        """Filter out videos already in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing video IDs
        cursor.execute('SELECT id FROM videos')
        existing_ids = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        
        unseen = [v for v in videos if v['id'] not in existing_ids]
        logger.info(f"Found {len(unseen)} new videos to harvest")
        return unseen
    
    def get_next_filename(self) -> str:
        """Get next available filename with zero-padded counter."""
        existing_files = list(self.dest_dir.glob('*.mp3'))
        if not existing_files:
            return "00001"
        
        # Extract numbers from existing filenames
        numbers = []
        for file in existing_files:
            match = re.match(r'^(\d+)', file.stem)
            if match:
                numbers.append(int(match.group(1)))
        
        next_num = max(numbers) + 1 if numbers else 1
        return f"{next_num:05d}"
    
    def clean_title(self, title: str) -> str:
        """Clean video title for filename."""
        # Remove common YouTube suffixes
        suffixes = [
            r'\s*\[OFFICIAL VIDEO\]',
            r'\s*\[OFFICIAL MUSIC VIDEO\]',
            r'\s*\(OFFICIAL VIDEO\)',
            r'\s*\(OFFICIAL MUSIC VIDEO\)',
            r'\s*\[MUSIC VIDEO\]',
            r'\s*\(MUSIC VIDEO\)',
            r'\s*\[LYRICS\]',
            r'\s*\(LYRICS\)',
            r'\s*\[AUDIO\]',
            r'\s*\(AUDIO\)',
            r'\s*\[HQ\]',
            r'\s*\(HQ\)',
            r'\s*\[HD\]',
            r'\s*\(HD\)',
        ]
        
        cleaned = title
        for suffix in suffixes:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        # Remove invalid filename characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def extract_artist_title(self, title: str, uploader: str) -> tuple:
        """Extract artist and title from video title."""
        # Common patterns: "Artist - Title" or "Title - Artist"
        patterns = [
            r'^(.+?)\s*[-–—]\s*(.+)$',  # Artist - Title
            r'^(.+?)\s*:\s*(.+)$',      # Artist: Title
            r'^(.+?)\s*"\s*(.+?)\s*"',  # Artist "Title"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, title)
            if match:
                return match.group(1).strip(), match.group(2).strip()
        
        # Fallback: use uploader as artist
        return uploader, title
    
    def download_video(self, video: Dict) -> Optional[str]:
        """Download video as audio file."""
        video_id = video['id']
        title = video['title']
        uploader = video['uploader']
        
        # Extract artist and title
        artist, clean_title = self.extract_artist_title(title, uploader)
        clean_title = self.clean_title(clean_title)
        
        # Generate filename
        counter = self.get_next_filename()
        filename = f"{counter} - {artist} - {clean_title}.{AUDIO_FMT}"
        filepath = self.dest_dir / filename
        
        try:
            cmd = [
                'yt-dlp',
                '-f', 'bestaudio',
                '--extract-audio',
                '--audio-format', AUDIO_FMT,
                '--audio-quality', QUALITY,
                '--embed-thumbnail',
                '--embed-metadata',
                '--output', str(filepath),
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            logger.info(f"Downloading: {title}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Tag the file with additional metadata
            self.tag_file(filepath, artist, clean_title, video_id)
            
            # Update database
            self.update_database(video_id, title, artist, filename)
            
            logger.info(f"Successfully downloaded: {filename}")
            return filename
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download {video_id}: {e}")
            return None
    
    def tag_file(self, filepath: Path, artist: str, title: str, video_id: str):
        """Add metadata tags to audio file."""
        try:
            import mutagen
            
            if AUDIO_FMT == 'mp3':
                from mutagen.id3 import ID3, TIT2, TPE1, TXXX
                
                audio = mutagen.File(filepath)
                if audio is None:
                    audio = mutagen.File(filepath, options=[mutagen.id3.ID3])
                
                if audio.tags is None:
                    audio.tags = ID3()
                
                audio.tags.add(TIT2(encoding=3, text=title))
                audio.tags.add(TPE1(encoding=3, text=artist))
                audio.tags.add(TXXX(encoding=3, desc='Source', text=f'YouTube • {video_id}'))
                
                audio.save()
                logger.debug(f"Tagged {filepath.name}")
                
        except ImportError:
            logger.warning("mutagen not available, skipping tagging")
        except Exception as e:
            logger.error(f"Failed to tag {filepath}: {e}")
    
    def update_database(self, video_id: str, title: str, artist: str, filename: str):
        """Add video to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO videos (id, title, artist, filename) VALUES (?, ?, ?, ?)',
            (video_id, title, artist, filename)
        )
        
        conn.commit()
        conn.close()
    
    def trigger_syncthing_rescan(self):
        """Trigger Syncthing to rescan the folder."""
        if not SYNCTHING_API_URL or not SYNCTHING_API_KEY or not SYNCTHING_FOLDER_ID:
            logger.warning("Syncthing API not configured, skipping rescan")
            return
        
        try:
            headers = {'X-API-Key': SYNCTHING_API_KEY}
            url = f"{SYNCTHING_API_URL}/rest/db/scan"
            params = {'folder': SYNCTHING_FOLDER_ID}
            
            response = requests.post(url, headers=headers, params=params)
            response.raise_for_status()
            
            logger.info("Triggered Syncthing rescan")
            
        except Exception as e:
            logger.error(f"Failed to trigger Syncthing rescan: {e}")
    
    def harvest(self):
        """Main harvesting process."""
        logger.info("Starting harvest cycle")
        
        # Get playlist videos
        videos = self.get_playlist_videos()
        if not videos:
            logger.warning("No videos found in playlist")
            return
        
        # Filter unseen videos
        unseen_videos = self.get_unseen_videos(videos)
        if not unseen_videos:
            logger.info("No new videos to harvest")
            return
        
        # Download new videos
        downloaded_count = 0
        for video in unseen_videos:
            filename = self.download_video(video)
            if filename:
                downloaded_count += 1
                time.sleep(2)  # Be nice to YouTube
        
        if downloaded_count > 0:
            logger.info(f"Harvested {downloaded_count} new videos")
            self.trigger_syncthing_rescan()
        else:
            logger.warning("No videos were successfully downloaded")
    
    def run_daemon(self):
        """Run as continuous daemon."""
        logger.info("Starting Project 5001 harvester daemon")
        
        while True:
            try:
                self.harvest()
                logger.info(f"Sleeping for {CHECK_INTERVAL} seconds")
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Harvester stopped by user")
                break
            except Exception as e:
                logger.error(f"Harvester error: {e}")
                time.sleep(60)  # Wait before retrying

def main():
    """Main entry point."""
    if not PLAYLIST_URL:
        logger.error("PLAYLIST_URL not set in environment")
        return
    
    harvester = PlaylistHarvester()
    
    # Check if running as daemon or single run
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        harvester.run_daemon()
    else:
        harvester.harvest()

if __name__ == '__main__':
    main() 