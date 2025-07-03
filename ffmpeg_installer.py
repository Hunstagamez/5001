#!/usr/bin/env python3
"""
Project 5001 - FFmpeg Auto-Installer
Automatically installs FFmpeg system-wide on first run.
"""

import os
import sys
import platform
import subprocess
import shutil
import tempfile
import zipfile
import tarfile
from pathlib import Path
from urllib.request import urlretrieve
import ssl

class FFmpegInstaller:
    """Cross-platform FFmpeg installer."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.is_64bits = sys.maxsize > 2**32
        
    def is_ffmpeg_installed(self) -> bool:
        """Check if ffmpeg is already installed and available in PATH."""
        return shutil.which('ffmpeg') is not None
    
    def get_ffmpeg_path(self) -> str:
        """Get the path to ffmpeg if installed."""
        return shutil.which('ffmpeg') or ''
    
    def install_ffmpeg_windows(self) -> bool:
        """Install FFmpeg on Windows."""
        print("🔄 Installing FFmpeg on Windows...")
        
        try:
            # Try using winget first (Windows 10 1709+)
            if self._try_winget_install():
                return True
            
            # Try using chocolatey if available
            if self._try_chocolatey_install():
                return True
            
            # Manual download and install
            return self._manual_windows_install()
            
        except Exception as e:
            print(f"❌ Windows installation failed: {e}")
            return False
    
    def _try_winget_install(self) -> bool:
        """Try installing via winget."""
        try:
            print("   Trying winget...")
            result = subprocess.run(['winget', 'install', 'FFmpeg'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ FFmpeg installed via winget")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False
    
    def _try_chocolatey_install(self) -> bool:
        """Try installing via chocolatey."""
        try:
            print("   Trying chocolatey...")
            result = subprocess.run(['choco', 'install', 'ffmpeg', '-y'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ FFmpeg installed via chocolatey")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False
    
    def _manual_windows_install(self) -> bool:
        """Manual download and install for Windows."""
        print("   Downloading FFmpeg manually...")
        
        # Download from official builds
        base_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest"
        arch = "win64" if self.is_64bits else "win32"
        filename = f"ffmpeg-master-latest-{arch}-gpl.zip"
        url = f"{base_url}/{filename}"
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = Path(temp_dir) / filename
                
                # Download
                print(f"   Downloading from {url}...")
                urlretrieve(url, zip_path)
                
                # Extract
                print("   Extracting...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find ffmpeg.exe
                ffmpeg_exe = None
                for root, dirs, files in os.walk(temp_dir):
                    if 'ffmpeg.exe' in files:
                        ffmpeg_exe = Path(root) / 'ffmpeg.exe'
                        break
                
                if not ffmpeg_exe:
                    print("❌ Could not find ffmpeg.exe in downloaded archive")
                    return False
                
                # Install to system PATH
                install_dir = Path("C:/ffmpeg")
                install_dir.mkdir(exist_ok=True)
                
                # Copy files
                bin_dir = install_dir / "bin"
                bin_dir.mkdir(exist_ok=True)
                
                for exe in ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']:
                    src = ffmpeg_exe.parent / exe
                    if src.exists():
                        shutil.copy2(src, bin_dir / exe)
                
                # Add to PATH
                self._add_to_windows_path(str(bin_dir))
                
                print(f"✅ FFmpeg installed to {install_dir}")
                return True
                
        except Exception as e:
            print(f"❌ Manual installation failed: {e}")
            return False
    
    def _add_to_windows_path(self, path: str):
        """Add directory to Windows PATH."""
        try:
            import winreg
            
            # Get current PATH
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 
                               0, winreg.KEY_READ | winreg.KEY_WRITE)
            
            current_path, _ = winreg.QueryValueEx(key, 'Path')
            
            if path not in current_path:
                new_path = current_path + ';' + path
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                winreg.CloseKey(key)
                
                print(f"   Added {path} to system PATH")
                print("   ⚠️  You may need to restart your terminal for PATH changes to take effect")
        except Exception as e:
            print(f"   ⚠️  Could not update PATH automatically: {e}")
            print(f"   Please manually add {path} to your system PATH")
    
    def install_ffmpeg_linux(self) -> bool:
        """Install FFmpeg on Linux."""
        print("🔄 Installing FFmpeg on Linux...")
        
        try:
            # Try different package managers
            package_managers = [
                ('apt', ['apt', 'update', '&&', 'apt', 'install', '-y', 'ffmpeg']),
                ('yum', ['yum', 'install', '-y', 'ffmpeg']),
                ('dnf', ['dnf', 'install', '-y', 'ffmpeg']),
                ('pacman', ['pacman', '-S', '--noconfirm', 'ffmpeg']),
                ('zypper', ['zypper', 'install', '-y', 'ffmpeg'])
            ]
            
            for name, cmd in package_managers:
                if self._try_package_manager(name, cmd):
                    return True
            
            print("❌ No supported package manager found")
            return False
            
        except Exception as e:
            print(f"❌ Linux installation failed: {e}")
            return False
    
    def _try_package_manager(self, name: str, cmd: list) -> bool:
        """Try installing via a specific package manager."""
        try:
            print(f"   Trying {name}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"✅ FFmpeg installed via {name}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False
    
    def install_ffmpeg_macos(self) -> bool:
        """Install FFmpeg on macOS."""
        print("🔄 Installing FFmpeg on macOS...")
        
        try:
            # Try Homebrew first
            if self._try_homebrew_install():
                return True
            
            # Try MacPorts
            if self._try_macports_install():
                return True
            
            print("❌ No supported package manager found")
            return False
            
        except Exception as e:
            print(f"❌ macOS installation failed: {e}")
            return False
    
    def _try_homebrew_install(self) -> bool:
        """Try installing via Homebrew."""
        try:
            print("   Trying Homebrew...")
            result = subprocess.run(['brew', 'install', 'ffmpeg'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ FFmpeg installed via Homebrew")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False
    
    def _try_macports_install(self) -> bool:
        """Try installing via MacPorts."""
        try:
            print("   Trying MacPorts...")
            result = subprocess.run(['sudo', 'port', 'install', 'ffmpeg'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ FFmpeg installed via MacPorts")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return False
    
    def install_ffmpeg(self) -> bool:
        """Install FFmpeg for the current platform."""
        if self.is_ffmpeg_installed():
            print("✅ FFmpeg is already installed")
            return True
        
        print(f"🔍 Detected platform: {self.system} ({self.machine})")
        
        if self.system == 'windows':
            return self.install_ffmpeg_windows()
        elif self.system == 'linux':
            return self.install_ffmpeg_linux()
        elif self.system == 'darwin':
            return self.install_ffmpeg_macos()
        else:
            print(f"❌ Unsupported platform: {self.system}")
            return False
    
    def cleanup_local_binaries(self):
        """Remove local ffmpeg binaries if they exist."""
        local_files = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
        removed = []
        
        for file in local_files:
            if Path(file).exists():
                try:
                    Path(file).unlink()
                    removed.append(file)
                except Exception as e:
                    print(f"⚠️  Could not remove {file}: {e}")
        
        if removed:
            print(f"🧹 Removed local binaries: {', '.join(removed)}")

def main():
    """Main entry point."""
    print("🎵 Project 5001 - FFmpeg Auto-Installer")
    print("=" * 50)
    
    installer = FFmpegInstaller()
    
    if installer.is_ffmpeg_installed():
        print("✅ FFmpeg is already installed and available")
        print(f"   Path: {installer.get_ffmpeg_path()}")
        return True
    
    print("❌ FFmpeg not found. Installing automatically...")
    
    success = installer.install_ffmpeg()
    
    if success:
        print("\n🎉 FFmpeg installation completed!")
        print("   You may need to restart your terminal for PATH changes to take effect")
        
        # Clean up local binaries if they exist
        installer.cleanup_local_binaries()
        
        return True
    else:
        print("\n❌ Automatic installation failed")
        print("   Please install FFmpeg manually:")
        print("   - Windows: Download from https://ffmpeg.org/download.html")
        print("   - Linux: Use your package manager (apt, yum, etc.)")
        print("   - macOS: Use Homebrew (brew install ffmpeg)")
        return False

if __name__ == "__main__":
    main() 