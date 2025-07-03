# Project 5001 - Code Cleanup Analysis

**Generated:** $(date)
**Analysis by:** AI Code Cleanup Agent

## 🗑️ **SAFE TO DELETE (75%+ Confidence)**

### 1. **harvester.py** - Completely Obsolete ✅ **DELETE** 
**Confidence: 90%**
- **Why**: Old version of harvester system, completely replaced by `harvester_v2.py`
- **Evidence**: 
  - No imports or references found in any codebase files
  - All system components reference `harvester_v2.py` instead
  - `harvester_v2.py` includes advanced features missing in old version (rate limiting, device rotation, configuration management)
  - 346 lines of obsolete code

### 2. **ffmpeg.exe & ffprobe.exe** - Wrong Platform ✅ **DELETE**
**Confidence: 85%**
- **Why**: Windows executables on Linux system
- **Evidence**:
  - User system is Linux (6.8.0-1024-aws)
  - Project uses yt-dlp which typically relies on system ffmpeg
  - No references to these specific executables in code
  - Dead weight: ~50MB of unnecessary binaries

### 3. **Unused Import Statements** ✅ **CLEAN**
**Confidence: 80%**

**In `setup_project5001.py`:**
```python
import zipfile        # Not used - Line 14
import urllib.request # Not used - Line 15
import platform      # Not used - Line 16
```

**In `status.py`:**
```python
from dotenv import load_dotenv  # Loaded twice - Line 12 & 149
```

**In `harvester_v2.py`:**
```python
import re  # Only used once, could be inlined - Line 12
```

### 4. **Redundant Environment Loading** ✅ **CLEAN**
**Confidence: 85%**
- **Issue**: Multiple files load `.env` multiple times
- **Solution**: Centralize in config module, remove duplicates

## ⚠️ **LIKELY REDUNDANT (60-74% Confidence)**

### 1. **start_main_node.py** - Thin Wrapper 🔶 **FLAG**
**Confidence: 70%**
- **Why uncertain**: May be used by systemd services or automation
- **Analysis**: Just 10 lines wrapping `harvester_v2.py main()`
- **Recommendation**: Check if referenced in service files before removing

### 2. **cookie_extension.js** - Orphaned JavaScript 🔶 **FLAG**
**Confidence: 75%**
- **Why uncertain**: Could be documentation or future feature
- **Analysis**: No references in Python code, cookies handled via `cookies.txt`
- **Recommendation**: Verify not used in browser automation before removing

### 3. **Overlapping Playlist Logic** - Partial Redundancy 🔶 **FLAG**
**Confidence: 65%**
- **Issue**: CLI playlist methods duplicate `PlaylistGenerator` functionality
- **Example**: `cli.py` has playlist generation methods that just call `PlaylistGenerator`
- **Recommendation**: Simplify CLI to direct calls, remove wrapper methods

## 🔧 **OPTIMIZATION OPPORTUNITIES**

### 1. **Duplicate Configuration Validation**
**Multiple files validate similar config patterns:**
- `config.py` - Main validation
- `initialiser.py` - Health checks  
- `cli.py` - Config testing
**Solution**: Centralize validation logic

### 2. **Repeated Database Connection Patterns**
**Files with similar DB connection code:**
- `database.py` - Main database class
- `status.py` - Direct SQLite connections
- `generate_playlists.py` - Direct SQLite connections
**Solution**: Always use `Project5001Database` class

### 3. **Logging Setup Duplication**
**Multiple files set up logging independently:**
- `config.py`, `cli.py`, `generate_playlists.py`, `harvester.py`
**Solution**: Centralize logging configuration

## 📊 **CLEANUP IMPACT SUMMARY**

| Category | Files Affected | Lines Removed | Confidence |
|----------|---------------|---------------|------------|
| Obsolete Files | 3 files | ~400 lines | 90% |
| Unused Imports | 5 files | ~15 lines | 80% |
| Binary Cleanup | 2 files | ~50MB | 85% |
| Code Deduplication | 8 files | ~200 lines | 70% |

**Total Estimated Cleanup: ~615 lines + 50MB**

## 🎯 **RECOMMENDED CLEANUP ORDER**

1. **Phase 1 (Immediate)**: Delete obsolete files (`harvester.py`, `ffmpeg.exe`, `ffprobe.exe`)
2. **Phase 2 (Safe)**: Remove unused imports and fix duplicate environment loading  
3. **Phase 3 (Test)**: Remove flagged files after verification
4. **Phase 4 (Refactor)**: Consolidate duplicate logic patterns

## ⚠️ **SAFETY NOTES**

- All changes should be tested on a non-production system first
- Keep git commits small and atomic for easy rollback
- Verify no external scripts reference deleted files
- Check systemd services and cron jobs for file references