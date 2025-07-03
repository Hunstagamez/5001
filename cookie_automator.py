#!/usr/bin/env python3
"""
Project 5001 - Cookie Automation Tool
Automatically extracts YouTube cookies from browsers for Project 5001.
"""

import os
import sys
import json
import sqlite3
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional
import time

def print_banner():
    """Print Project 5001 cookie automation banner."""
    print("🍪" + "="*50)
    print("   PROJECT 5001 - COOKIE AUTOMATION TOOL")
    print("   Automatically extract YouTube cookies")
    print("="*50 + "🍪")
    print()

def get_browser_paths() -> Dict[str, str]:
    """Get common browser paths for different operating systems."""
    system = platform.system()
    
    if system == "Windows":
        return {
            "chrome": [
                os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Network\\Cookies"),
                os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\Network\\Cookies"),
                os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2\\Network\\Cookies"),
            ],
            "edge": [
                os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Network\\Cookies"),
                os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 1\\Network\\Cookies"),
            ],
            "firefox": [
                os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"),
            ]
        }
    elif system == "Darwin":  # macOS
        return {
            "chrome": [
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Profile 1/Cookies"),
            ],
            "safari": [
                os.path.expanduser("~/Library/Cookies/Cookies.binarycookies"),
            ],
            "firefox": [
                os.path.expanduser("~/Library/Application Support/Firefox/Profiles"),
            ]
        }
    else:  # Linux
        return {
            "chrome": [
                os.path.expanduser("~/.config/google-chrome/Default/Cookies"),
                os.path.expanduser("~/.config/google-chrome/Profile 1/Cookies"),
            ],
            "firefox": [
                os.path.expanduser("~/.mozilla/firefox"),
            ]
        }

def extract_chrome_cookies(cookies_path: str) -> List[Dict]:
    """Extract YouTube cookies from Chrome/Edge database."""
    try:
        # Create a temporary copy of the cookies file (Chrome locks the original)
        temp_cookies = Path("temp_cookies.db")
        if temp_cookies.exists():
            temp_cookies.unlink()
        
        # Copy the cookies file
        import shutil
        shutil.copy2(cookies_path, temp_cookies)
        
        # Connect to the cookies database
        conn = sqlite3.connect(temp_cookies)
        cursor = conn.cursor()
        
        # Get YouTube cookies
        cursor.execute("""
            SELECT name, value, expires_utc, path, secure, httponly
            FROM cookies 
            WHERE host_key LIKE '%youtube.com'
        """)
        
        cookies = []
        for row in cursor.fetchall():
            name, value, expires_utc, path, secure, httponly = row
            
            # Convert Chrome timestamp to Unix timestamp
            # Chrome uses microseconds since 1601-01-01
            if expires_utc:
                # Convert to seconds since epoch
                expires_utc = (expires_utc - 11644473600000000) // 1000000
            
            cookies.append({
                'name': name,
                'value': value,
                'expires': expires_utc,
                'path': path,
                'secure': secure,
                'httponly': httponly
            })
        
        conn.close()
        temp_cookies.unlink()  # Clean up
        
        return cookies
        
    except Exception as e:
        print(f"❌ Failed to extract Chrome cookies: {e}")
        return []

def extract_firefox_cookies(profiles_path: str) -> List[Dict]:
    """Extract YouTube cookies from Firefox database."""
    try:
        # Find the default profile
        profiles_dir = Path(profiles_path)
        if not profiles_dir.exists():
            return []
        
        # Look for profiles.ini
        profiles_ini = profiles_dir / "profiles.ini"
        if not profiles_ini.exists():
            return []
        
        # Find the default profile
        default_profile = None
        with open(profiles_ini, 'r') as f:
            for line in f:
                if line.startswith("Path="):
                    default_profile = line.split("=", 1)[1].strip()
                    break
        
        if not default_profile:
            return []
        
        # Get the cookies database path
        cookies_path = profiles_dir / default_profile / "cookies.sqlite"
        if not cookies_path.exists():
            return []
        
        # Connect to the cookies database
        conn = sqlite3.connect(cookies_path)
        cursor = conn.cursor()
        
        # Get YouTube cookies
        cursor.execute("""
            SELECT name, value, expiry, path, isSecure, isHttpOnly
            FROM moz_cookies 
            WHERE host LIKE '%youtube.com'
        """)
        
        cookies = []
        for row in cursor.fetchall():
            name, value, expiry, path, is_secure, is_httponly = row
            cookies.append({
                'name': name,
                'value': value,
                'expires': expiry,
                'path': path,
                'secure': is_secure,
                'httponly': is_httponly
            })
        
        conn.close()
        return cookies
        
    except Exception as e:
        print(f"❌ Failed to extract Firefox cookies: {e}")
        return []

def write_cookies_file(cookies: List[Dict], output_path: str = "cookies.txt"):
    """Write cookies to Netscape format file."""
    try:
        with open(output_path, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# This file is generated by Project 5001 Cookie Automation Tool\n")
            f.write("# Do not edit manually\n\n")
            
            for cookie in cookies:
                # Netscape format: domain, domain_specified, path, secure, expiry, name, value
                domain = ".youtube.com"
                domain_specified = "TRUE"
                path = cookie.get('path', '/')
                secure = "TRUE" if cookie.get('secure') else "FALSE"
                expiry = cookie.get('expires', 0)
                name = cookie['name']
                value = cookie['value']
                
                f.write(f"{domain}\t{domain_specified}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
        
        print(f"✅ Cookies written to {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to write cookies file: {e}")
        return False

def test_cookies(cookies_file: str = "cookies.txt") -> bool:
    """Test if the extracted cookies work with yt-dlp."""
    try:
        # Test with a simple YouTube video
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--cookies', cookies_file,
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '96k',
            '--output', 'test_cookies.mp3',
            '--no-warnings',
            test_url
        ]
        
        print("🧪 Testing extracted cookies...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Check if download was successful
        if result.returncode == 0 and Path("test_cookies.mp3").exists():
            print("✅ Cookie test successful!")
            Path("test_cookies.mp3").unlink()  # Clean up test file
            return True
        else:
            print("❌ Cookie test failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Cookie test error: {e}")
        return False

def main():
    """Main function."""
    print_banner()
    
    # Get browser paths
    browser_paths = get_browser_paths()
    
    print("🔍 Looking for browser cookie databases...")
    
    all_cookies = []
    
    # Try Chrome/Edge
    for browser, paths in [("Chrome", browser_paths.get("chrome", [])), 
                          ("Edge", browser_paths.get("edge", []))]:
        for path in paths:
            if Path(path).exists():
                print(f"📂 Found {browser} cookies at: {path}")
                cookies = extract_chrome_cookies(path)
                if cookies:
                    print(f"✅ Extracted {len(cookies)} YouTube cookies from {browser}")
                    all_cookies.extend(cookies)
                break
    
    # Try Firefox
    firefox_paths = browser_paths.get("firefox", [])
    for path in firefox_paths:
        if Path(path).exists():
            print(f"📂 Found Firefox cookies at: {path}")
            cookies = extract_firefox_cookies(path)
            if cookies:
                print(f"✅ Extracted {len(cookies)} YouTube cookies from Firefox")
                all_cookies.extend(cookies)
            break
    
    if not all_cookies:
        print("❌ No YouTube cookies found in any browser")
        print("\n💡 Manual cookie extraction:")
        print("1. Go to YouTube and log in")
        print("2. Open browser DevTools (F12)")
        print("3. Go to Application/Storage → Cookies → youtube.com")
        print("4. Copy the required cookies manually")
        return False
    
    # Remove duplicates
    unique_cookies = {}
    for cookie in all_cookies:
        key = cookie['name']
        if key not in unique_cookies or cookie.get('expires', 0) > unique_cookies[key].get('expires', 0):
            unique_cookies[key] = cookie
    
    cookies_list = list(unique_cookies.values())
    print(f"📊 Total unique YouTube cookies: {len(cookies_list)}")
    
    # Write cookies file
    if write_cookies_file(cookies_list):
        # Test the cookies
        if test_cookies():
            print("\n🎉 Cookie automation successful!")
            print("Your Project 5001 system should now be able to download YouTube videos.")
            return True
        else:
            print("\n⚠️  Cookies extracted but test failed.")
            print("The cookies might be expired or invalid.")
            return False
    else:
        print("\n❌ Failed to write cookies file")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 