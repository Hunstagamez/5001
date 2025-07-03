#!/usr/bin/env python3
"""
Project 5001 - FFmpeg Installer
Cross-platform FFmpeg installation utility.
"""

import os
import sys
import platform
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Optional

class FFmpegInstaller:
    """Cross-platform FFmpeg installer."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        
    def is_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is already available."""
        return shutil.which('ffmpeg') is not None
    
    def install_ffmpeg(self) -> bool:
        """Install FFmpeg for the current platform."""
        if self.is_ffmpeg_available():
            logging.info("FFmpeg is already available")
            return True
        
        logging.info(f"Installing FFmpeg for {self.system}")
        
        try:
            if self.system == 'linux':
                return self._install_linux()
            elif self.system == 'darwin':  # macOS
                return self._install_macos()
            elif self.system == 'windows':
                return self._install_windows()
            else:
                logging.error(f"Unsupported platform: {self.system}")
                return False
        except Exception as e:
            logging.error(f"FFmpeg installation failed: {e}")
            return False
    
    def _install_linux(self) -> bool:
        """Install FFmpeg on Linux using package managers."""
        # Try different package managers
        package_managers = [
            (['apt', 'update'], ['apt', 'install', '-y', 'ffmpeg']),
            (['yum', 'install', '-y', 'epel-release'], ['yum', 'install', '-y', 'ffmpeg']),
            (['dnf', 'install', '-y', 'ffmpeg']),
            (['pacman', '-S', '--noconfirm', 'ffmpeg']),
            (['zypper', 'install', '-y', 'ffmpeg'])
        ]
        
        for commands in package_managers:
            try:
                # For apt, run update first
                if len(commands) == 2:
                    subprocess.run(commands[0], check=True, capture_output=True)
                    result = subprocess.run(commands[1], check=True, capture_output=True)
                else:
                    result = subprocess.run(commands[0], check=True, capture_output=True)
                
                if result.returncode == 0 and self.is_ffmpeg_available():
                    logging.info("FFmpeg installed successfully via package manager")
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        # If package managers fail, try snap
        try:
            subprocess.run(['snap', 'install', 'ffmpeg'], check=True, capture_output=True)
            if self.is_ffmpeg_available():
                logging.info("FFmpeg installed successfully via snap")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        logging.error("Could not install FFmpeg on Linux. Please install manually.")
        return False
    
    def _install_macos(self) -> bool:
        """Install FFmpeg on macOS using Homebrew."""
        # Check if Homebrew is available
        if not shutil.which('brew'):
            logging.error("Homebrew not found. Please install Homebrew first: https://brew.sh")
            return False
        
        try:
            # Update Homebrew
            subprocess.run(['brew', 'update'], check=True, capture_output=True)
            
            # Install FFmpeg
            result = subprocess.run(['brew', 'install', 'ffmpeg'], check=True, capture_output=True)
            
            if result.returncode == 0 and self.is_ffmpeg_available():
                logging.info("FFmpeg installed successfully via Homebrew")
                return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Homebrew installation failed: {e}")
        
        return False
    
    def _install_windows(self) -> bool:
        """Install FFmpeg on Windows."""
        logging.info("Windows FFmpeg installation requires manual setup")
        logging.info("Please download FFmpeg from: https://ffmpeg.org/download.html#build-windows")
        logging.info("Extract the archive and add the bin folder to your PATH environment variable")
        
        # Try to install via winget if available
        if shutil.which('winget'):
            try:
                result = subprocess.run(['winget', 'install', 'Gyan.FFmpeg'], 
                                      check=True, capture_output=True, text=True)
                if result.returncode == 0:
                    logging.info("FFmpeg installed via winget. You may need to restart your terminal.")
                    return True
            except subprocess.CalledProcessError:
                pass
        
        # Try chocolatey
        if shutil.which('choco'):
            try:
                result = subprocess.run(['choco', 'install', 'ffmpeg', '-y'], 
                                      check=True, capture_output=True, text=True)
                if result.returncode == 0 and self.is_ffmpeg_available():
                    logging.info("FFmpeg installed successfully via Chocolatey")
                    return True
            except subprocess.CalledProcessError:
                pass
        
        # Try scoop
        if shutil.which('scoop'):
            try:
                result = subprocess.run(['scoop', 'install', 'ffmpeg'], 
                                      check=True, capture_output=True, text=True)
                if result.returncode == 0 and self.is_ffmpeg_available():
                    logging.info("FFmpeg installed successfully via Scoop")
                    return True
            except subprocess.CalledProcessError:
                pass
        
        logging.warning("Automatic installation failed. Please install FFmpeg manually.")
        return False
    
    def get_ffmpeg_path(self) -> Optional[str]:
        """Get the path to FFmpeg executable."""
        return shutil.which('ffmpeg')
    
    def verify_installation(self) -> bool:
        """Verify that FFmpeg is properly installed and working."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and 'ffmpeg version' in result.stdout:
                logging.info("FFmpeg installation verified")
                return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logging.error("FFmpeg installation verification failed")
        return False

def main():
    """Main entry point for testing."""
    installer = FFmpegInstaller()
    
    print("🎬 FFmpeg Installer for Project 5001")
    print("="*40)
    
    if installer.is_ffmpeg_available():
        print("✅ FFmpeg is already available")
        path = installer.get_ffmpeg_path()
        print(f"   Path: {path}")
        if installer.verify_installation():
            print("✅ FFmpeg verification passed")
        else:
            print("❌ FFmpeg verification failed")
    else:
        print("⚠️  FFmpeg not found. Installing...")
        if installer.install_ffmpeg():
            print("✅ FFmpeg installation completed")
            if installer.verify_installation():
                print("✅ FFmpeg verification passed")
            else:
                print("❌ FFmpeg verification failed")
        else:
            print("❌ FFmpeg installation failed")
            print("\nManual Installation:")
            print("1. Download FFmpeg from: https://ffmpeg.org/download.html")
            print("2. Extract and add to your system PATH")
            print("3. Restart your terminal/command prompt")

if __name__ == '__main__':
    main() 