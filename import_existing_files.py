#!/usr/bin/env python3
"""
Project 5001 - Import Existing Files
Manually import existing MP3 files from the Harvest folder into the database.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import NodeConfig
    from database import Project5001Database
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the Project 5001 directory")
    sys.exit(1)

class ExistingFileImporter:
    def __init__(self):
        self.config = NodeConfig('main')
        self.db = Project5001Database(self.config)
        self.harvest_dir = Path(self.config.get('harvest_dir'))
        
    def extract_info_from_filename(self, filename: str) -> Tuple[str, str, str]:
        """Extract artist and title from filename."""
        # Remove extension
        name = Path(filename).stem
        
        # Try to parse patterns like "00001 - Artist - Title" or "Artist - Title"
        patterns = [
            r'^\d+\s*-\s*(.+?)\s*-\s*(.+)$',  # "00001 - Artist - Title"
            r'^(.+?)\s*-\s*(.+)$',            # "Artist - Title"
            r'^(.+?)\s*:\s*(.+)$',            # "Artist: Title"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, name)
            if match:
                artist = match.group(1).strip()
                title = match.group(2).strip()
                # Generate a simple video ID from filename
                video_id = f"imported_{hash(filename) % 1000000:06d}"
                return video_id, artist, title
        
        # Fallback: use filename as title, "Unknown Artist" as artist
        video_id = f"imported_{hash(filename) % 1000000:06d}"
        return video_id, "Unknown Artist", name
    
    def get_existing_files(self) -> List[Path]:
        """Get all MP3 files in the harvest directory."""
        if not self.harvest_dir.exists():
            print(f"❌ Harvest directory not found: {self.harvest_dir}")
            return []
        
        files = list(self.harvest_dir.glob('*.mp3'))
        return files
    
    def get_database_files(self) -> List[str]:
        """Get all filenames currently in the database."""
        videos = self.db.get_all_videos()
        return [video['filename'] for video in videos]
    
    def import_file(self, filepath: Path) -> bool:
        """Import a single file into the database."""
        filename = filepath.name
        
        # Check if already in database
        if filename in self.get_database_files():
            print(f"⚠️  {filename} already in database, skipping")
            return False
        
        # Extract info from filename
        video_id, artist, title = self.extract_info_from_filename(filename)
        
        # Get file size
        file_size = filepath.stat().st_size
        
        # Add to database
        success = self.db.add_video(
            video_id=video_id,
            title=title,
            artist=artist,
            filename=filename,
            playlist_url="manual_import",
            file_size=file_size,
            duration=None,
            quality="unknown"
        )
        
        if success:
            print(f"✅ Imported: {filename} ({artist} - {title})")
            return True
        else:
            print(f"❌ Failed to import: {filename}")
            return False
    
    def import_all_files(self) -> int:
        """Import all existing files not in the database."""
        print("🔍 Scanning for existing files...")
        
        files = self.get_existing_files()
        if not files:
            print("ℹ️  No MP3 files found in harvest directory")
            return 0
        
        print(f"Found {len(files)} MP3 files")
        
        # Get files already in database
        db_files = set(self.get_database_files())
        
        # Filter out files already in database
        new_files = [f for f in files if f.name not in db_files]
        
        if not new_files:
            print("ℹ️  All files are already in the database")
            return 0
        
        print(f"Found {len(new_files)} files to import:")
        for file in new_files:
            print(f"  📄 {file.name}")
        
        print(f"\n🔄 Importing {len(new_files)} files...")
        
        imported_count = 0
        for file in new_files:
            if self.import_file(file):
                imported_count += 1
        
        print(f"\n✅ Successfully imported {imported_count}/{len(new_files)} files")
        return imported_count
    
    def show_status(self):
        """Show current status of files vs database."""
        print("📊 File Import Status:")
        
        files = self.get_existing_files()
        db_files = set(self.get_database_files())
        
        print(f"Files in harvest directory: {len(files)}")
        print(f"Files in database: {len(db_files)}")
        
        # Find orphaned files (in directory but not in database)
        orphaned = [f for f in files if f.name not in db_files]
        print(f"Files to import: {len(orphaned)}")
        
        if orphaned:
            print("\nFiles not in database:")
            for file in orphaned:
                print(f"  📄 {file.name}")
        
        # Find database-only files (in database but not in directory)
        db_only = [f for f in db_files if not (self.harvest_dir / f).exists()]
        if db_only:
            print(f"\nFiles in database but missing from directory: {len(db_only)}")
            for filename in db_only:
                print(f"  ❓ {filename}")

def main():
    importer = ExistingFileImporter()
    
    print("🎧 Project 5001 - Import Existing Files")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Show status")
        print("2. Import all files")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            importer.show_status()
        elif choice == '2':
            imported = importer.import_all_files()
            if imported > 0:
                print(f"\n🎉 Successfully imported {imported} files!")
                print("You can now run the initializer again to see the updated track count.")
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == '__main__':
    main() 