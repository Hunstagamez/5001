#!/usr/bin/env python3
"""
Project 5001 - Database Management
Handles SQLite database for tracking videos, sync status, and device rotation.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from config import NodeConfig

class Project5001Database:
    """Database management for Project 5001."""
    
    def __init__(self, config: NodeConfig):
        self.config = config
        self.db_path = Path(config.get('database_file'))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Videos table - tracks all harvested videos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT,
                filename TEXT,
                playlist_url TEXT,
                file_size INTEGER,
                duration INTEGER,
                quality TEXT,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sync status table - tracks sync across devices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_status (
                device_id TEXT,
                video_id TEXT,
                sync_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                file_path TEXT,
                PRIMARY KEY (device_id, video_id),
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        ''')
        
        # Device rotation table - tracks download device rotation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_rotation (
                device_id TEXT PRIMARY KEY,
                device_name TEXT,
                device_type TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_used TIMESTAMP,
                rate_limit_count INTEGER DEFAULT 0,
                last_rate_limit TIMESTAMP,
                cooldown_until TIMESTAMP,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0
            )
        ''')
        
        # Download history table - tracks download attempts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                device_id TEXT,
                attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error_message TEXT,
                download_speed REAL,
                file_size INTEGER,
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        ''')
        
        # Rate limiting events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                details TEXT,
                resolved BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logging.info("Database initialized successfully")
    
    def add_video(self, video_id: str, title: str, artist: str, filename: str, 
                  playlist_url: str, file_size: int = None, duration: int = None, 
                  quality: str = None) -> bool:
        """Add a video to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO videos 
                (id, title, artist, filename, playlist_url, file_size, duration, quality, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (video_id, title, artist, filename, playlist_url, file_size, 
                  duration, quality, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Added video to database: {title}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add video {video_id}: {e}")
            return False
    
    def get_video(self, video_id: str) -> Optional[Dict]:
        """Get video information from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, artist, filename, playlist_url, file_size, 
                       duration, quality, download_date, last_modified
                FROM videos WHERE id = ?
            ''', (video_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'artist': row[2],
                    'filename': row[3],
                    'playlist_url': row[4],
                    'file_size': row[5],
                    'duration': row[6],
                    'quality': row[7],
                    'download_date': row[8],
                    'last_modified': row[9]
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Failed to get video {video_id}: {e}")
            return None
    
    def video_exists(self, video_id: str) -> bool:
        """Check if video exists in database."""
        return self.get_video(video_id) is not None
    
    def get_all_videos(self, limit: int = None) -> List[Dict]:
        """Get all videos from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT id, title, artist, filename, playlist_url, file_size, 
                       duration, quality, download_date, last_modified
                FROM videos 
                ORDER BY download_date DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'title': row[1],
                'artist': row[2],
                'filename': row[3],
                'playlist_url': row[4],
                'file_size': row[5],
                'duration': row[6],
                'quality': row[7],
                'download_date': row[8],
                'last_modified': row[9]
            } for row in rows]
            
        except Exception as e:
            logging.error(f"Failed to get videos: {e}")
            return []
    
    def get_recent_videos(self, days: int = 7) -> List[Dict]:
        """Get videos added in the last N days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT id, title, artist, filename, playlist_url, file_size, 
                       duration, quality, download_date, last_modified
                FROM videos 
                WHERE download_date >= ?
                ORDER BY download_date DESC
            ''', (cutoff_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'title': row[1],
                'artist': row[2],
                'filename': row[3],
                'playlist_url': row[4],
                'file_size': row[5],
                'duration': row[6],
                'quality': row[7],
                'download_date': row[8],
                'last_modified': row[9]
            } for row in rows]
            
        except Exception as e:
            logging.error(f"Failed to get recent videos: {e}")
            return []
    
    def update_sync_status(self, device_id: str, video_id: str, status: str, 
                          file_path: str = None) -> bool:
        """Update sync status for a device and video."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sync_status 
                (device_id, video_id, sync_date, status, file_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (device_id, video_id, datetime.now().isoformat(), status, file_path))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to update sync status: {e}")
            return False
    
    def get_sync_status(self, device_id: str = None, video_id: str = None) -> List[Dict]:
        """Get sync status information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT device_id, video_id, sync_date, status, file_path
                FROM sync_status
                WHERE 1=1
            '''
            params = []
            
            if device_id:
                query += ' AND device_id = ?'
                params.append(device_id)
            
            if video_id:
                query += ' AND video_id = ?'
                params.append(video_id)
            
            query += ' ORDER BY sync_date DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'device_id': row[0],
                'video_id': row[1],
                'sync_date': row[2],
                'status': row[3],
                'file_path': row[4]
            } for row in rows]
            
        except Exception as e:
            logging.error(f"Failed to get sync status: {e}")
            return []
    
    def add_device(self, device_id: str, device_name: str, device_type: str) -> bool:
        """Add a device to the rotation pool."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO device_rotation 
                (device_id, device_name, device_type, is_active)
                VALUES (?, ?, ?, 1)
            ''', (device_id, device_name, device_type))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Added device to rotation: {device_name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add device: {e}")
            return False
    
    def get_available_devices(self) -> List[Dict]:
        """Get all available devices for rotation."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT device_id, device_name, device_type, is_active, 
                       last_used, rate_limit_count, last_rate_limit, 
                       cooldown_until, success_count, failure_count
                FROM device_rotation 
                WHERE is_active = 1
                ORDER BY last_used ASC NULLS FIRST
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'device_id': row[0],
                'device_name': row[1],
                'device_type': row[2],
                'is_active': bool(row[3]),
                'last_used': row[4],
                'rate_limit_count': row[5],
                'last_rate_limit': row[6],
                'cooldown_until': row[7],
                'success_count': row[8],
                'failure_count': row[9]
            } for row in rows]
            
        except Exception as e:
            logging.error(f"Failed to get available devices: {e}")
            return []
    
    def update_device_usage(self, device_id: str, success: bool = True) -> bool:
        """Update device usage statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            if success:
                cursor.execute('''
                    UPDATE device_rotation 
                    SET last_used = ?, success_count = success_count + 1
                    WHERE device_id = ?
                ''', (now, device_id))
            else:
                cursor.execute('''
                    UPDATE device_rotation 
                    SET last_used = ?, failure_count = failure_count + 1
                    WHERE device_id = ?
                ''', (now, device_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to update device usage: {e}")
            return False
    
    def record_rate_limit(self, device_id: str, event_type: str, details: str = None) -> bool:
        """Record a rate limiting event."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cooldown_until = (datetime.now() + timedelta(minutes=5)).isoformat()
            
            # Update device rotation table
            cursor.execute('''
                UPDATE device_rotation 
                SET rate_limit_count = rate_limit_count + 1,
                    last_rate_limit = ?,
                    cooldown_until = ?
                WHERE device_id = ?
            ''', (now, cooldown_until, device_id))
            
            # Add to rate limit events table
            cursor.execute('''
                INSERT INTO rate_limit_events 
                (device_id, event_type, details)
                VALUES (?, ?, ?)
            ''', (device_id, event_type, details))
            
            conn.commit()
            conn.close()
            
            logging.warning(f"Rate limit recorded for device {device_id}: {event_type}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to record rate limit: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total videos
            cursor.execute('SELECT COUNT(*) FROM videos')
            total_videos = cursor.fetchone()[0]
            
            # Recent videos (last 7 days)
            cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM videos WHERE download_date >= ?', (cutoff_date,))
            recent_videos = cursor.fetchone()[0]
            
            # Total file size
            cursor.execute('SELECT SUM(file_size) FROM videos WHERE file_size IS NOT NULL')
            total_size = cursor.fetchone()[0] or 0
            
            # Device count
            cursor.execute('SELECT COUNT(*) FROM device_rotation WHERE is_active = 1')
            active_devices = cursor.fetchone()[0]
            
            # Sync status summary
            cursor.execute('SELECT status, COUNT(*) FROM sync_status GROUP BY status')
            sync_summary = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_videos': total_videos,
                'recent_videos': recent_videos,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'active_devices': active_devices,
                'sync_summary': sync_summary
            }
            
        except Exception as e:
            logging.error(f"Failed to get database stats: {e}")
            return {}

if __name__ == '__main__':
    # Test database
    config = NodeConfig('main')
    db = Project5001Database(config)
    
    # Test adding a video
    db.add_video('test123', 'Test Song', 'Test Artist', '00001 - Test Artist - Test Song.mp3', 
                 'https://youtube.com/playlist?list=test')
    
    # Test getting stats
    stats = db.get_database_stats()
    print(f"Database stats: {stats}") 