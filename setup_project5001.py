#!/usr/bin/env python3
"""
Project 5001 - Interactive Setup Script
Configures the distributed music harvesting system for different node types.
"""

import os
import sys
import json
import subprocess
import getpass
from pathlib import Path
from typing import Dict, List
import shutil
import zipfile
import urllib.request
import platform

def print_banner():
    """Print Project 5001 banner."""
    print("🎧" + "="*50)
    print("   PROJECT 5001 - DISTRIBUTED MUSIC HARVESTER")
    print("   Taking back control of your music collection")
    print("="*50 + "🎧")
    print()

def check_ffmpeg() -> str:
    """Ensure ffmpeg is available. If not, download and extract it locally."""
    # Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        print(f"✅ ffmpeg found: {ffmpeg_path}")
        return ffmpeg_path

    # If not, check local bin
    local_bin = Path('Project5001') / 'bin'
    local_bin.mkdir(parents=True, exist_ok=True)
    local_ffmpeg = local_bin / 'ffmpeg.exe'
    if local_ffmpeg.exists():
        print(f"✅ ffmpeg found: {local_ffmpeg}")
        return str(local_ffmpeg)

    # Download for Windows only
    if platform.system() == 'Windows':
        print("❌ ffmpeg not found. Downloading ffmpeg for Windows...")
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = local_bin / 'ffmpeg.zip'
        try:
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            print("✅ Downloaded ffmpeg zip")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find ffmpeg.exe in the zip
                for member in zip_ref.namelist():
                    if member.endswith('ffmpeg.exe'):
                        zip_ref.extract(member, local_bin)
                        extracted = local_bin / member
                        extracted.rename(local_ffmpeg)
                        print(f"✅ Extracted ffmpeg.exe to {local_ffmpeg}")
                        break
            zip_path.unlink()
            return str(local_ffmpeg)
        except Exception as e:
            print(f"❌ Failed to download/extract ffmpeg: {e}")
            return ''
    else:
        print("❌ ffmpeg not found. Please install ffmpeg using your package manager.")
        return ''

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check yt-dlp
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ yt-dlp {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ yt-dlp not found")
        print("   Install with: pip install yt-dlp")
        return False
    
    # Check Python packages
    required_packages = ['requests', 'mutagen', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False
    
    # Check ffmpeg
    ffmpeg_path = check_ffmpeg()
    if not ffmpeg_path:
        print("❌ ffmpeg is required. Please install it and re-run setup.")
        return False
    
    return True

def get_node_role() -> str:
    """Get the node role from user input."""
    print("\n🏗️  Node Configuration")
    print("What type of node is this device?")
    print("1. Main Node (Downloads from YouTube, coordinates the network)")
    print("2. Secondary Node (Receives music from main node)")
    print("3. Mobile Node (iPhone setup - Syncthing iOS app (Android coming soon sorry :) )")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        if choice == '1':
            return 'main'
        elif choice == '2':
            return 'secondary'
        elif choice == '3':
            return 'mobile'
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def get_main_node_config() -> Dict:
    """Get configuration for main node."""
    print("\n🎯 Main Node Configuration")
    print("This node will download music from YouTube and coordinate the network.")
    
    config = {}
    
    # Get playlist URLs
    print("\n📋 YouTube Playlists")
    print("Enter your YouTube playlist URLs (one per line, empty line to finish):")
    playlist_urls = []
    
    while True:
        url = input("Playlist URL: ").strip()
        if not url:
            break
        if 'youtube.com/playlist' in url:
            playlist_urls.append(url)
        else:
            print("⚠️  Please enter a valid YouTube playlist URL")
    
    if not playlist_urls:
        print("❌ At least one playlist URL is required")
        return None
    
    config['playlist_urls'] = playlist_urls
    
    # Syncthing configuration
    print("\n🔄 Syncthing Configuration")
    print("Syncthing will sync music across your devices.")
    
    api_url = input("Syncthing API URL (default: http://localhost:8384): ").strip()
    config['syncthing.api_url'] = api_url or 'http://localhost:8384'
    
    api_key = input("Syncthing API Key: ").strip()
    if not api_key:
        print("❌ Syncthing API key is required")
        return None
    config['syncthing.api_key'] = api_key
    
    folder_id = input("Syncthing Folder ID: ").strip()
    if not folder_id:
        print("❌ Syncthing folder ID is required")
        return None
    config['syncthing.folder_id'] = folder_id
    
    device_id = input("This device's Syncthing ID: ").strip()
    if not device_id:
        print("❌ Device ID is required")
        return None
    config['syncthing.device_id'] = device_id
    
    # Download settings
    print("\n⚙️  Download Settings")
    max_concurrent = input("Max concurrent downloads (default: 3): ").strip()
    config['max_concurrent_downloads'] = int(max_concurrent) if max_concurrent else 3
    
    check_interval = input("Check interval in seconds (default: 3600): ").strip()
    config['check_interval'] = int(check_interval) if check_interval else 3600
    
    config['ffmpeg_path'] = str(check_ffmpeg())
    
    return config

def get_secondary_node_config() -> Dict:
    """Get configuration for secondary node."""
    print("\n🖥️  Secondary Node Configuration")
    print("This node will receive music from the main node.")
    
    config = {}
    
    # Main node connection
    print("\n🔗 Main Node Connection")
    main_address = input("Main node IP address or hostname: ").strip()
    if not main_address:
        print("❌ Main node address is required")
        return None
    config['main_node_address'] = main_address
    
    main_device_id = input("Main node's Syncthing device ID: ").strip()
    if not main_device_id:
        print("❌ Main node device ID is required")
        return None
    config['main_node_device_id'] = main_device_id
    
    # Syncthing configuration
    print("\n🔄 Syncthing Configuration")
    api_url = input("Syncthing API URL (default: http://localhost:8384): ").strip()
    config['syncthing.api_url'] = api_url or 'http://localhost:8384'
    
    api_key = input("Syncthing API Key: ").strip()
    if not api_key:
        print("❌ Syncthing API key is required")
        return None
    config['syncthing.api_key'] = api_key
    
    folder_id = input("Syncthing Folder ID: ").strip()
    if not folder_id:
        print("❌ Syncthing folder ID is required")
        return None
    config['syncthing.folder_id'] = folder_id
    
    device_id = input("This device's Syncthing ID: ").strip()
    if not device_id:
        print("❌ Device ID is required")
        return None
    config['syncthing.device_id'] = device_id
    
    config['ffmpeg_path'] = str(check_ffmpeg())
    
    return config

def get_mobile_node_config() -> Dict:
    """Get configuration for mobile node."""
    print("\n📱 Mobile Node Configuration")
    print("This is for iPhone setup using Syncthing iOS app.")
    
    config = {}
    
    # Syncthing configuration
    print("\n🔄 Syncthing Configuration")
    print("You'll need to configure Syncthing iOS app manually.")
    print("1. Install Syncthing iOS app from App Store")
    print("2. Add the main node as a device")
    print("3. Share the Project5001 folder")
    
    api_url = input("Syncthing API URL (if available): ").strip()
    config['syncthing.api_url'] = api_url or 'http://localhost:8384'
    
    api_key = input("Syncthing API Key (if available): ").strip()
    config['syncthing.api_key'] = api_key
    
    folder_id = input("Syncthing Folder ID: ").strip()
    config['syncthing.folder_id'] = folder_id
    
    device_id = input("This device's Syncthing ID: ").strip()
    config['syncthing.device_id'] = device_id
    
    config['ffmpeg_path'] = str(check_ffmpeg())
    
    return config

def create_configuration(role: str, config_data: Dict) -> bool:
    """Create the node configuration."""
    try:
        from config import create_node_config
        
        # Create the configuration
        node_config = create_node_config(role, **config_data)
        
        print(f"✅ Configuration created for {role} node")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        return False

def test_configuration(role: str) -> bool:
    """Test the configuration."""
    print(f"\n🧪 Testing {role} node configuration...")
    
    try:
        from config import NodeConfig
        from database import Project5001Database
        
        # Test configuration loading
        config = NodeConfig(role)
        print("✅ Configuration loaded")
        
        # Test database
        db = Project5001Database(config)
        print("✅ Database initialized")
        
        # Test harvester (if main node)
        if role == 'main':
            from harvester_v2 import AdvancedHarvester
            harvester = AdvancedHarvester(config)
            print("✅ Harvester initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def create_startup_scripts(role: str):
    """Create startup scripts for the node."""
    print(f"\n📜 Creating startup scripts for {role} node...")
    
    # Create main startup script
    if role == 'main':
        script_content = '''#!/usr/bin/env python3
# Project 5001 - Main Node Startup Script
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from harvester_v2 import main

if __name__ == '__main__':
    main()
'''
        
        with open('start_main_node.py', 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod('start_main_node.py', 0o755)
        print("✅ Created start_main_node.py")
    
    # Create systemd service file
    service_content = f'''[Unit]
Description=Project 5001 {role.title()} Node
After=network.target
Wants=network.target

[Service]
Type=simple
User={getpass.getuser()}
Group={getpass.getuser()}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')}
ExecStart={sys.executable} harvester_v2.py {role} --daemon
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''
    
    with open(f'project5001-{role}-node.service', 'w') as f:
        f.write(service_content)
    
    print(f"✅ Created project5001-{role}-node.service")

def print_next_steps(role: str):
    """Print next steps for the user."""
    print(f"\n🎉 {role.title()} Node Setup Complete!")
    print("\n📋 Next Steps:")
    
    if role == 'main':
        print("1. Start the harvester: python harvester_v2.py main --daemon")
        print("2. Or use systemd: sudo systemctl enable project5001-main-node.service")
        print("3. Check logs: tail -f Project5001/Logs/main-node.log")
        print("4. Monitor status: python status.py")
        
    elif role == 'secondary':
        print("1. Ensure Syncthing is running and connected to main node")
        print("2. Check sync status in Syncthing web interface")
        print("3. Monitor logs: tail -f Project5001/Logs/secondary-node.log")
        
    elif role == 'mobile':
        print("1. Install Syncthing iOS app from App Store")
        print("2. Add main node as a device in Syncthing")
        print("3. Share the Project5001 folder")
        print("4. Install VLC or preferred music player")
        print("5. Point music player to synced Project5001/Harvest folder")
    
    print(f"\n📚 Documentation: See TECHNICAL_README.md for detailed instructions")
    print("🆘 Support: Check logs in Project5001/Logs/ for troubleshooting")

def main():
    """Main setup function."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed. Please install missing dependencies.")
        return False
    
    # Get node role
    role = get_node_role()
    
    # Get configuration based on role
    if role == 'main':
        config_data = get_main_node_config()
    elif role == 'secondary':
        config_data = get_secondary_node_config()
    elif role == 'mobile':
        config_data = get_mobile_node_config()
    else:
        print("❌ Invalid role")
        return False
    
    if not config_data:
        print("\n❌ Setup cancelled.")
        return False

    # --- Syncthing folder path check ---
    # Only check if Syncthing is enabled and folder_id is set
    syncthing_folder_id = config_data.get('syncthing.folder_id')
    # Acceptable folder names/IDs (case-insensitive)
    expected_folder = 'Project5001/Harvest'
    # Warn if folder_id does not contain 'harvest' or 'Project5001/Harvest'
    if syncthing_folder_id and 'harvest' not in syncthing_folder_id.lower() and 'project5001/harvest' not in syncthing_folder_id.lower():
        print(f"\n⚠️  WARNING: Your Syncthing folder ID is set to '{syncthing_folder_id}'.\nFor Project 5001 to work, you must sync the 'Project5001/Harvest' folder (not just the project root or another folder).\n")
        resp = input("Would you like to auto-correct this to 'Project5001/Harvest'? (Y/n): ").strip().lower()
        if resp in ('', 'y', 'yes'):
            config_data['syncthing.folder_id'] = 'Project5001/Harvest'
            print("✅ Syncthing folder ID set to 'Project5001/Harvest'.")
        else:
            print("⚠️  Proceeding with your current folder ID, but syncing may not work correctly.")
    # --- End Syncthing folder path check ---

    # Create configuration
    if not create_configuration(role, config_data):
        return False
    
    # Test configuration
    if not test_configuration(role):
        print("\n⚠️  Configuration test failed, but setup completed.")
        print("You may need to fix configuration issues manually.")
    
    # Create startup scripts
    create_startup_scripts(role)
    
    # Print next steps
    print_next_steps(role)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 