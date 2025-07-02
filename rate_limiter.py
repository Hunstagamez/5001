#!/usr/bin/env python3
"""
Project 5001 - Rate Limiting Detection and Device Rotation
Manages intelligent device rotation based on YouTube rate limiting detection.
"""

import time
import logging
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import NodeConfig
from database import Project5001Database

class RateLimitDetector:
    """Detects rate limiting from YouTube and manages device rotation."""
    
    def __init__(self, config: NodeConfig, database: Project5001Database):
        self.config = config
        self.db = database
        self.current_device_id = config.get('syncthing.device_id')
        
        # Rate limiting patterns to detect
        self.rate_limit_patterns = {
            'http_429': 'HTTP 429 Too Many Requests',
            'http_403': 'HTTP 403 Forbidden',
            'http_503': 'HTTP 503 Service Unavailable',
            'download_failure': 'Download failed',
            'speed_drop': 'Significant speed reduction',
            'connection_timeout': 'Connection timeout',
            'quota_exceeded': 'Quota exceeded'
        }
        
        # Cooldown periods (in minutes)
        self.cooldown_periods = {
            'http_429': 30,  # 30 minutes for 429
            'http_403': 60,  # 1 hour for 403
            'http_503': 15,  # 15 minutes for 503
            'download_failure': 10,  # 10 minutes for general failures
            'speed_drop': 5,  # 5 minutes for speed issues
            'connection_timeout': 5,  # 5 minutes for timeouts
            'quota_exceeded': 120  # 2 hours for quota issues
        }
    
    def detect_rate_limit(self, error_output: str, http_status: int = None, 
                         download_speed: float = None) -> Optional[str]:
        """Detect rate limiting from various signals."""
        
        # Check HTTP status codes
        if http_status:
            if http_status == 429:
                return 'http_429'
            elif http_status == 403:
                return 'http_403'
            elif http_status == 503:
                return 'http_503'
        
        # Check error output for patterns
        error_lower = error_output.lower()
        
        if '429' in error_output or 'too many requests' in error_lower:
            return 'http_429'
        elif '403' in error_output or 'forbidden' in error_lower:
            return 'http_403'
        elif '503' in error_output or 'service unavailable' in error_lower:
            return 'http_503'
        elif 'quota exceeded' in error_lower or 'quota' in error_lower:
            return 'quota_exceeded'
        elif 'timeout' in error_lower or 'connection' in error_lower:
            return 'connection_timeout'
        elif 'download failed' in error_lower or 'failed' in error_lower:
            return 'download_failure'
        
        # Check for speed drops (if we have speed data)
        if download_speed and download_speed < 10000:  # Less than 10KB/s
            return 'speed_drop'
        
        return None
    
    def record_rate_limit_event(self, device_id: str, event_type: str, 
                               details: str = None) -> bool:
        """Record a rate limiting event in the database."""
        return self.db.record_rate_limit(device_id, event_type, details)
    
    def is_device_in_cooldown(self, device_id: str) -> bool:
        """Check if a device is currently in cooldown."""
        devices = self.db.get_available_devices()
        
        for device in devices:
            if device['device_id'] == device_id:
                if device['cooldown_until']:
                    cooldown_until = datetime.fromisoformat(device['cooldown_until'])
                    if datetime.now() < cooldown_until:
                        logging.info(f"Device {device_id} is in cooldown until {cooldown_until}")
                        return True
                break
        
        return False
    
    def get_next_available_device(self) -> Optional[Dict]:
        """Get the next available device for downloading."""
        devices = self.db.get_available_devices()
        
        if not devices:
            logging.warning("No devices available for rotation")
            return None
        
        # Filter out devices in cooldown
        available_devices = []
        for device in devices:
            if not self.is_device_in_cooldown(device['device_id']):
                available_devices.append(device)
        
        if not available_devices:
            logging.warning("All devices are in cooldown")
            return None
        
        # Sort by last used (oldest first) and rate limit count (lowest first)
        available_devices.sort(key=lambda x: (
            x['last_used'] or '1970-01-01',
            x['rate_limit_count']
        ))
        
        next_device = available_devices[0]
        logging.info(f"Selected device for rotation: {next_device['device_name']}")
        return next_device
    
    def rotate_to_next_device(self) -> Optional[Dict]:
        """Rotate to the next available device."""
        next_device = self.get_next_available_device()
        
        if next_device:
            # Update current device as used
            self.db.update_device_usage(next_device['device_id'], success=True)
            self.current_device_id = next_device['device_id']
            
            logging.info(f"Rotated to device: {next_device['device_name']}")
            return next_device
        
        return None
    
    def handle_download_failure(self, error_output: str, http_status: int = None,
                               download_speed: float = None) -> bool:
        """Handle a download failure and potentially rotate devices."""
        
        # Detect rate limiting
        rate_limit_type = self.detect_rate_limit(error_output, http_status, download_speed)
        
        if rate_limit_type:
            logging.warning(f"Rate limiting detected: {rate_limit_type}")
            
            # Record the event
            self.record_rate_limit_event(
                self.current_device_id, 
                rate_limit_type, 
                f"HTTP {http_status}" if http_status else error_output[:200]
            )
            
            # Check if rotation is enabled
            if self.config.get('rotation_enabled', True):
                # Try to rotate to next device
                next_device = self.rotate_to_next_device()
                if next_device:
                    return True  # Successfully rotated
                else:
                    logging.error("No available devices for rotation")
                    return False  # No devices available
            
            return False  # Rotation disabled or failed
        
        else:
            # Not a rate limit, just a regular failure
            logging.info("Download failure (not rate limiting)")
            self.db.update_device_usage(self.current_device_id, success=False)
            return False
    
    def get_rotation_status(self) -> Dict:
        """Get current rotation status."""
        devices = self.db.get_available_devices()
        
        status = {
            'current_device': self.current_device_id,
            'total_devices': len(devices),
            'available_devices': 0,
            'devices_in_cooldown': 0,
            'device_details': []
        }
        
        for device in devices:
            in_cooldown = self.is_device_in_cooldown(device['device_id'])
            if not in_cooldown:
                status['available_devices'] += 1
            else:
                status['devices_in_cooldown'] += 1
            
            status['device_details'].append({
                'device_id': device['device_id'],
                'device_name': device['device_name'],
                'device_type': device['device_type'],
                'in_cooldown': in_cooldown,
                'rate_limit_count': device['rate_limit_count'],
                'success_count': device['success_count'],
                'failure_count': device['failure_count'],
                'last_used': device['last_used']
            })
        
        return status

class DeviceManager:
    """Manages device registration and health monitoring."""
    
    def __init__(self, config: NodeConfig, database: Project5001Database):
        self.config = config
        self.db = database
    
    def register_device(self, device_id: str, device_name: str, device_type: str) -> bool:
        """Register a new device in the rotation pool."""
        return self.db.add_device(device_id, device_name, device_type)
    
    def get_device_health(self, device_id: str) -> Dict:
        """Get health statistics for a device."""
        devices = self.db.get_available_devices()
        
        for device in devices:
            if device['device_id'] == device_id:
                success_rate = 0
                if device['success_count'] + device['failure_count'] > 0:
                    success_rate = device['success_count'] / (device['success_count'] + device['failure_count'])
                
                return {
                    'device_id': device['device_id'],
                    'device_name': device['device_name'],
                    'device_type': device['device_type'],
                    'is_active': device['is_active'],
                    'success_count': device['success_count'],
                    'failure_count': device['failure_count'],
                    'success_rate': round(success_rate * 100, 2),
                    'rate_limit_count': device['rate_limit_count'],
                    'last_used': device['last_used'],
                    'last_rate_limit': device['last_rate_limit']
                }
        
        return {}
    
    def deactivate_device(self, device_id: str) -> bool:
        """Deactivate a device from rotation."""
        try:
            conn = self.db.db_path
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE device_rotation 
                SET is_active = 0
                WHERE device_id = ?
            ''', (device_id,))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Deactivated device: {device_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to deactivate device {device_id}: {e}")
            return False
    
    def reactivate_device(self, device_id: str) -> bool:
        """Reactivate a device in rotation."""
        try:
            conn = self.db.db_path
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE device_rotation 
                SET is_active = 1, cooldown_until = NULL
                WHERE device_id = ?
            ''', (device_id,))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Reactivated device: {device_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to reactivate device {device_id}: {e}")
            return False

if __name__ == '__main__':
    # Test rate limiting detection
    config = NodeConfig('main')
    db = Project5001Database(config)
    
    detector = RateLimitDetector(config, db)
    device_manager = DeviceManager(config, db)
    
    # Test rate limit detection
    test_errors = [
        "HTTP Error 429: Too Many Requests",
        "HTTP Error 403: Forbidden",
        "Download failed: Connection timeout",
        "Quota exceeded for this API"
    ]
    
    for error in test_errors:
        rate_limit_type = detector.detect_rate_limit(error)
        print(f"Error: {error}")
        print(f"Detected: {rate_limit_type}")
        print() 