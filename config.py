#!/usr/bin/env python3
"""
Project 5001 - Configuration Management
Handles different node roles and settings for the distributed system.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NodeConfig:
    """Configuration management for different node types."""
    
    ROLES = ['main', 'secondary', 'mobile']
    
    def __init__(self, role: str = None):
        self.role = role or os.getenv('NODE_ROLE', 'main')
        self.config_dir = Path('./config')
        self.config_dir.mkdir(exist_ok=True)
        
        # Load role-specific configuration
        self.config = self.load_config()
        
        # Setup logging
        self.setup_logging()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration for the current role."""
        config_file = self.config_dir / f'{self.role}-node.json'
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Return default configuration
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the current role."""
        base_config = {
            'node_role': self.role,
            'data_dir': './Project5001',
            'harvest_dir': './Project5001/Harvest',
            'playlists_dir': './Project5001/Playlists',
            'logs_dir': './Project5001/Logs',
            'database_file': './Project5001/harvest.db',
            'audio_format': 'mp3',
            'audio_quality': '256k',
            'check_interval': 3600,  # 1 hour
            'max_retries': 3,
            'retry_delay': 60,
            'rate_limit_cooldown': 300,  # 5 minutes
            'syncthing': {
                'enabled': False,
                'api_url': 'http://localhost:8384',
                'api_key': '',
                'folder_id': '',
                'device_id': ''
            }
        }
        
        # Role-specific configurations
        if self.role == 'main':
            base_config.update({
                'is_downloader': True,
                'is_coordinator': True,
                'playlist_urls': [],
                'rotation_enabled': True,
                'max_concurrent_downloads': 3,
                'download_delay': 2,  # seconds between downloads
                'syncthing': {
                    'enabled': True,
                    'api_url': 'http://localhost:8384',
                    'api_key': '',
                    'folder_id': '',
                    'device_id': ''
                }
            })
        
        elif self.role == 'secondary':
            base_config.update({
                'is_downloader': False,
                'is_coordinator': False,
                'main_node_address': '',
                'main_node_device_id': '',
                'syncthing': {
                    'enabled': True,
                    'api_url': 'http://localhost:8384',
                    'api_key': '',
                    'folder_id': '',
                    'device_id': ''
                }
            })
        
        elif self.role == 'mobile':
            base_config.update({
                'is_downloader': False,
                'is_coordinator': False,
                'priority_sync': True,
                'background_sync': True,
                'max_storage_gb': 2000,  # 2TB
                'syncthing': {
                    'enabled': True,
                    'api_url': 'http://localhost:8384',
                    'api_key': '',
                    'folder_id': '',
                    'device_id': ''
                }
            })
        
        return base_config
    
    def save_config(self):
        """Save current configuration to file."""
        config_file = self.config_dir / f'{self.role}-node.json'
        
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        logging.info(f"Configuration saved to {config_file}")
    
    def setup_logging(self):
        """Setup logging for the node."""
        log_dir = Path(self.config['logs_dir'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'{self.role}-node.log'),
                logging.StreamHandler()
            ]
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        errors = []
        
        # Check required fields based on role
        if self.role == 'main':
            if not self.get('playlist_urls'):
                errors.append("Main node requires playlist URLs")
            if not self.get('syncthing.api_key'):
                errors.append("Main node requires Syncthing API key")
        
        elif self.role == 'secondary':
            if not self.get('main_node_address'):
                errors.append("Secondary node requires main node address")
        
        # Check common requirements
        if self.get('syncthing.enabled'):
            if not self.get('syncthing.folder_id'):
                errors.append("Syncthing folder ID required when enabled")
        
        if errors:
            for error in errors:
                logging.error(f"Configuration error: {error}")
            return False
        
        return True
    
    def create_directories(self):
        """Create necessary directories."""
        directories = [
            self.config['data_dir'],
            self.config['harvest_dir'],
            self.config['playlists_dir'],
            self.config['logs_dir']
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        logging.info("Directory structure created")

def create_node_config(role: str, **kwargs) -> NodeConfig:
    """Create and configure a node."""
    config = NodeConfig(role)
    
    # Set provided values
    for key, value in kwargs.items():
        config.set(key, value)
    
    # Create directories
    config.create_directories()
    
    # Validate configuration
    if not config.validate_config():
        raise ValueError("Invalid configuration")
    
    # Save configuration
    config.save_config()
    
    return config

if __name__ == '__main__':
    # Test configuration
    config = NodeConfig('main')
    print(f"Node role: {config.role}")
    print(f"Configuration: {json.dumps(config.config, indent=2)}") 