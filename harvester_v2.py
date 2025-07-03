#!/usr/bin/env python3
"""
Project 5001 - Advanced Harvester v2
Core harvesting system with rate limiting detection, device rotation, and smart management.
"""

import os
import json
import logging
import time
import subprocess
import requests
import re
import platform  # Added for cross-platform compatibility
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import NodeConfig
from database import Project5001Database
from rate_limiter import RateLimitDetector, DeviceManager

class AdvancedHarvester:
    """Advanced harvester with rate limiting detection and device rotation."""
    
    def __init__(self, config: NodeConfig):
        self.config = config
        self.db = Project5001Database(config)
        self.rate_detector = RateLimitDetector(config, self.db)
        self.device_manager = DeviceManager(config, self.db)
        
        self.harvest_dir = Path(config.get('harvest_dir'))
        self.harvest_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize device if this is a main node
        if config.get('is_downloader', False):
            self._initialize_device()
    
    def _initialize_device(self):
        """Initialize this device in the rotation pool."""
        device_id = self.config.get('syncthing.device_id')
        device_name = f"{self.config.role}-{platform.node() if hasattr(platform, 'node') else 'unknown'}"
        device_type = self.config.role
        
        self.device_manager.register_device(device_id, device_name, device_type)
        logging.info(f"Initialized device: {device_name} ({device_id})")
    
    def get_playlist_videos(self, playlist_url: str) -> List[Dict]:
        """Fetch videos from a YouTube playlist using yt-dlp."""
        try:
            cmd = [
                'yt-dlp',
                '--flat-playlist',
                '--dump-json',
                '--no-warnings',
                playlist_url
            ]
            
            # FIXED: Add cookies support for playlist fetching to avoid authentication issues
            if Path('cookies.txt').exists():
                cmd.extend(['--cookies', 'cookies.txt'])
            
            logging.info(f"Fetching playlist: {playlist_url}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video_data = json.loads(line)
                        videos.append({
                            'id': video_data['id'],
                            'title': video_data['title'],
                            'uploader': video_data.get('uploader', 'Unknown Artist'),
                            'duration': video_data.get('duration'),
                            'view_count': video_data.get('view_count'),
                            'playlist_url': playlist_url
                        })
                    except json.JSONDecodeError:
                        continue
            
            logging.info(f"Found {len(videos)} videos in playlist")
            return videos
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to fetch playlist {playlist_url}: {e}")
            return []
    
    def get_unseen_videos(self, videos: List[Dict]) -> List[Dict]:
        """Filter out videos already in database."""
        unseen = []
        
        for video in videos:
            if not self.db.video_exists(video['id']):
                unseen.append(video)
        
        logging.info(f"Found {len(unseen)} new videos to harvest")
        return unseen
    
    def get_next_filename(self) -> str:
        """Get next available filename with zero-padded counter."""
        existing_files = list(self.harvest_dir.glob('*.mp3'))
        
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
        """Clean video title for filename with enhanced safety."""
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
            r'\s*\[4K\]',
            r'\s*\(4K\)',
            r'\s*\[1080P\]',
            r'\s*\(1080P\)',
            r'\s*\[720P\]',
            r'\s*\(720P\)',
        ]
        
        cleaned = title
        for suffix in suffixes:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        # Enhanced filename sanitization for cross-platform compatibility
        # Remove/replace invalid filename characters for Windows/Unix
        cleaned = re.sub(r'[<>:"/\\|?*]', '', cleaned)
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)  # Remove control characters
        cleaned = re.sub(r'[^\w\s\-\.\(\)\[\]&]', '', cleaned)  # Keep only safe characters
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
        cleaned = cleaned.strip('. ')  # Remove leading/trailing dots and spaces
        
        # Ensure filename isn't empty and isn't too long
        if not cleaned:
            cleaned = "Unknown_Title"
        if len(cleaned) > 100:  # Limit filename length
            cleaned = cleaned[:100].strip()
        
        return cleaned
    
    def extract_artist_title(self, title: str, uploader: str) -> Tuple[str, str]:
        """Extract artist and title from video title."""
        # Common patterns: "Artist - Title" or "Title - Artist"
        patterns = [
            r'^(.+?)\s*[-–—]\s*(.+)$',  # Artist - Title
            r'^(.+?)\s*:\s*(.+)$',      # Artist: Title
            r'^(.+?)\s*"\s*(.+?)\s*"',  # Artist "Title"
            r"^(.+?)\s*'\s*(.+?)\s*'",  # Artist 'Title'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, title)
            if match:
                return match.group(1).strip(), match.group(2).strip()
        
        # Fallback: use uploader as artist
        return uploader, title
    
    def download_video(self, video: Dict) -> Optional[Dict]:
        """Download a video with rate limiting detection and fallback."""
        video_id = video['id']
        title = video['title']
        uploader = video['uploader']
        
        # Extract artist and title
        artist, clean_title = self.extract_artist_title(title, uploader)
        clean_title = self.clean_title(clean_title)
        
        # Generate filename
        counter = self.get_next_filename()
        filename = f"{counter} - {artist} - {clean_title}.mp3"
        filepath = self.harvest_dir / filename
        
        # Try different quality settings
        quality_settings = [
            ('256k', 'bestaudio[ext=m4a]/bestaudio'),
            ('192k', 'bestaudio[ext=m4a]/bestaudio'),
            ('128k', 'bestaudio[ext=m4a]/bestaudio'),
            ('96k', 'bestaudio[ext=m4a]/bestaudio')
        ]
        
        for quality, format_spec in quality_settings:
            success, result = self._attempt_download(
                video_id, filepath, format_spec, quality
            )
            
            if success:
                # Tag the file
                self._tag_file(filepath, artist, clean_title, video_id)
                
                # Update database
                self.db.add_video(
                    video_id, title, artist, filename, video['playlist_url'],
                    result.get('file_size'), result.get('duration'), quality
                )
                
                logging.info(f"Successfully downloaded: {filename} ({quality})")
                return {
                    'filename': filename,
                    'quality': quality,
                    'file_size': result.get('file_size'),
                    'duration': result.get('duration')
                }
            
            # Check if we should rotate devices
            if self.rate_detector.handle_download_failure(
                result.get('error', ''), 
                result.get('http_status'),
                result.get('download_speed')
            ):
                logging.info("Device rotated, retrying download")
                continue
            else:
                break
        
        logging.error(f"Failed to download {video_id} after all attempts")
        return None
    
    def _attempt_download(self, video_id: str, filepath: Path, format_spec: str, 
                         quality: str) -> Tuple[bool, Dict]:
        """Attempt to download a video with specific settings."""
        try:
            cmd = [
                'yt-dlp',
                '-f', format_spec,
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', quality,
                '--embed-thumbnail',
                '--embed-metadata',
                '--output', str(filepath),
                '--no-warnings',
                '--newline',
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            # FIXED: Proper command construction to avoid argument order issues
            # Add cookies.txt if it exists
            if Path('cookies.txt').exists():
                cmd.extend(['--cookies', 'cookies.txt'])
            # Add ffmpeg location if specified in config
            ffmpeg_path = self.config.get('ffmpeg_path')
            if ffmpeg_path:
                cmd.extend(['--ffmpeg-location', ffmpeg_path])
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            end_time = time.time()
            
            if result.returncode == 0 and filepath.exists():
                file_size = filepath.stat().st_size
                download_speed = file_size / (end_time - start_time) if (end_time - start_time) > 0 else 0
                
                return True, {
                    'file_size': file_size,
                    'duration': None,  # Could extract from metadata
                    'download_speed': download_speed
                }
            else:
                return False, {
                    'error': result.stderr,
                    'http_status': self._extract_http_status(result.stderr),
                    'download_speed': 0
                }
                
        except subprocess.TimeoutExpired:
            return False, {
                'error': 'Download timeout',
                'http_status': None,
                'download_speed': 0
            }
        except Exception as e:
            return False, {
                'error': str(e),
                'http_status': None,
                'download_speed': 0
            }
    
    def _extract_http_status(self, error_output: str) -> Optional[int]:
        """Extract HTTP status code from error output."""
        if not error_output:
            return None
        
        # Look for HTTP status codes
        status_match = re.search(r'HTTP Error (\d+)', error_output)
        if status_match:
            return int(status_match.group(1))
        
        return None
    
    def _tag_file(self, filepath: Path, artist: str, title: str, video_id: str):
        """Add metadata tags to audio file."""
        try:
            import mutagen
            
            if filepath.suffix.lower() == '.mp3':
                from mutagen.id3 import ID3, TIT2, TPE1, TXXX, TALB
                
                audio = mutagen.File(filepath)
                if audio is None:
                    audio = mutagen.File(filepath, options=[mutagen.id3.ID3])
                
                if audio.tags is None:
                    audio.tags = ID3()
                
                audio.tags.add(TIT2(encoding=3, text=title))
                audio.tags.add(TPE1(encoding=3, text=artist))
                audio.tags.add(TALB(encoding=3, text='Project 5001'))
                audio.tags.add(TXXX(encoding=3, desc='Source', text=f'YouTube • {video_id}'))
                audio.tags.add(TXXX(encoding=3, desc='Harvested', text=datetime.now().isoformat()))
                
                audio.save()
                logging.debug(f"Tagged {filepath.name}")
                
        except ImportError:
            logging.warning("mutagen not available, skipping tagging")
        except Exception as e:
            logging.error(f"Failed to tag {filepath}: {e}")
    
    def trigger_syncthing_rescan(self):
        """Trigger Syncthing to rescan the folder."""
        if not self.config.get('syncthing.enabled'):
            return
        
        api_url = self.config.get('syncthing.api_url')
        api_key = self.config.get('syncthing.api_key')
        folder_id = self.config.get('syncthing.folder_id')
        
        if not all([api_url, api_key, folder_id]):
            logging.warning("Syncthing API not fully configured")
            return
        
        try:
            headers = {'X-API-Key': api_key}
            url = f"{api_url}/rest/db/scan"
            params = {'folder': folder_id}
            
            response = requests.post(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            logging.info("Triggered Syncthing rescan")
            
        except Exception as e:
            logging.error(f"Failed to trigger Syncthing rescan: {e}")
    
    def harvest_playlist(self, playlist_url: str) -> int:
        """Harvest a single playlist."""
        logging.info(f"Starting harvest for playlist: {playlist_url}")
        
        # Get playlist videos
        videos = self.get_playlist_videos(playlist_url)
        if not videos:
            return 0
        
        # Filter unseen videos
        unseen_videos = self.get_unseen_videos(videos)
        if not unseen_videos:
            logging.info("No new videos to harvest")
            return 0
        
        # Download videos with concurrency control
        max_concurrent = self.config.get('max_concurrent_downloads', 3)
        download_delay = self.config.get('download_delay', 2)
        
        downloaded_count = 0
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit download tasks
            future_to_video = {
                executor.submit(self.download_video, video): video 
                for video in unseen_videos
            }
            
            # Process completed downloads
            for future in as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    result = future.result()
                    if result:
                        downloaded_count += 1
                        logging.info(f"Downloaded {downloaded_count}/{len(unseen_videos)}: {video['title']}")
                    
                    # Add delay between downloads
                    time.sleep(download_delay)
                    
                except Exception as e:
                    logging.error(f"Download failed for {video['title']}: {e}")
        
        if downloaded_count > 0:
            logging.info(f"Harvested {downloaded_count} new videos from playlist")
            self.trigger_syncthing_rescan()
        
        return downloaded_count
    
    def harvest_all_playlists(self) -> int:
        """Harvest all configured playlists."""
        playlist_urls = self.config.get('playlist_urls', [])
        
        if not playlist_urls:
            logging.warning("No playlist URLs configured")
            return 0
        
        total_downloaded = 0
        
        for playlist_url in playlist_urls:
            try:
                downloaded = self.harvest_playlist(playlist_url)
                total_downloaded += downloaded
                
                # Add delay between playlists
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Failed to harvest playlist {playlist_url}: {e}")
        
        return total_downloaded
    
    def run_harvest_cycle(self):
        """Run a single harvest cycle."""
        if not self.config.get('is_downloader', False):
            logging.info("This node is not configured as a downloader")
            return
        
        logging.info("Starting harvest cycle")
        
        try:
            downloaded = self.harvest_all_playlists()
            
            if downloaded > 0:
                logging.info(f"Harvest cycle completed: {downloaded} videos downloaded")
            else:
                logging.info("Harvest cycle completed: no new videos")
                
        except Exception as e:
            logging.error(f"Harvest cycle failed: {e}")
    
    def run_daemon(self):
        """Run as continuous daemon."""
        logging.info("Starting Project 5001 Advanced Harvester daemon")
        
        check_interval = self.config.get('check_interval', 3600)
        
        while True:
            try:
                self.run_harvest_cycle()
                
                # Log rotation status
                rotation_status = self.rate_detector.get_rotation_status()
                logging.info(f"Rotation status: {rotation_status['available_devices']}/{rotation_status['total_devices']} devices available")
                
                logging.info(f"Sleeping for {check_interval} seconds")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logging.info("Harvester stopped by user")
                break
            except Exception as e:
                logging.error(f"Harvester error: {e}")
                time.sleep(60)  # Wait before retrying

def main():
    """Main entry point."""
    import sys
    
    # Determine role from command line or environment
    role = 'main'
    if len(sys.argv) > 1:
        role = sys.argv[1]
    
    # Create configuration
    config = NodeConfig(role)
    
    # Validate configuration
    if not config.validate_config():
        logging.error("Invalid configuration")
        return
    
    # Create harvester
    harvester = AdvancedHarvester(config)
    
    # Check if running as daemon
    if len(sys.argv) > 2 and sys.argv[2] == '--daemon':
        harvester.run_daemon()
    else:
        harvester.run_harvest_cycle()

if __name__ == '__main__':
    main() 