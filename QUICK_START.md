# 🎧 Project 5001 - Quick Start Guide

## 🚀 **One-Command Setup**

### 1. **Clone and Setup**
```bash
git clone https://github.com/Hunstagamez/5001.git
cd 5001
python initialiser.py --setup
```

### 2. **Configure YouTube Cookies**
```bash
# Copy the template
cp cookies.example.txt cookies.txt

# Edit cookies.txt with your YouTube cookies
# See cookies.example.txt for detailed instructions
```

### 3. **Start the System**
```bash
# Quick start (checks health and starts if ready)
python initialiser.py --quick

# Or start manually
python initialiser.py --start
```

## 🎛️ **Management Interface**

### **Full CLI Management**
```bash
python cli.py
```
Provides interactive menus for:
- 🎵 Harvester Control (start/stop/status)
- 📋 Playlist Management (generate all playlists)
- 📊 System Status (database, files, Syncthing)
- 📁 File Operations (browse, search, cleanup)
- ⚙️ Configuration (view, validate, reload)
- 📝 Logs & Debugging (view, search, cleanup)
- 🔄 Syncthing Operations (rescan, test connection)
- ❓ Help & Documentation

### **Quick Commands**
```bash
# Check system status
python initialiser.py --status

# Health check
python initialiser.py --health

# Maintenance tasks
python initialiser.py --maintenance

# Stop services
python initialiser.py --stop

# Restart services
python initialiser.py --restart
```

## 📱 Node Types

### **Main Node** (Home Machine Recommended)
- Downloads music from YouTube playlists
- Coordinates the distributed network
- Manages device rotation for rate limiting
- Triggers Syncthing sync after downloads

### **Secondary Node** (E.g. Travel Laptop)
- Receives music from main node via Syncthing
- Full library sync
- Can be promoted to download duty should something happen to main node

### **Mobile Node** (iPhone)
- Uses Syncthing iOS app
- Full iPhone library sync
- Offline playback with VLC or preferred app

## 🔧 Core Features

### **Smart Rate Limiting Detection**
- Automatically detects YouTube rate limiting
- Rotates between devices to avoid blocks
- Intelligent cooldown periods
- Aggressive download strategy

### **Distributed RAID-esque System**
- Multiple devices hold complete copies
- No single point of failure
- Automatic failover and recovery
- P2P mesh networking via Syncthing
- Plug-N-Play node expansion functionality

### **Intelligent Playlist Generation**
- **Main Archive**: Complete collection (all tracks)
- **Recent Additions**: Last 30 days of new music
- **Monthly Playlists**: Organized by month (last 6 months)
- **Artist Playlists**: Grouped by artist (3+ tracks minimum)
- **Favorites**: Recent additions (top 100)

### **Priority Sync**
- New tracks sync first
- Backfill older content
- Full library on iPhone
- No bandwidth throttling

## 📊 Monitoring

### **Check Status**
```bash
# Full status report
python initialiser.py --status

# JSON output for scripting
python status.py --json
```

### **View Logs**
```bash
# View recent logs
python cli.py -> Logs -> View Recent Logs

# Or manually
tail -f Project5001/Logs/main-node.log
```

### **Health Check**
```bash
python initialiser.py --health
```

## 🎵 Audio Quality

- **Target**: 256kbps MP3
- **Fallback**: 192k, 128k, 96k if needed
- **Storage**: <80GB for 5000+ tracks
- **Format**: MP3 with full metadata tagging

## 🔄 Syncthing Setup

> **Important:** You must sync the `Project5001/Harvest` folder (NOT the root) between your devices. This is where all music is downloaded and stored.

### **Get API Key**
1. Open Syncthing Web UI (http://localhost:8384)
2. Actions → Settings → API
3. Copy the API key

### **Get Folder ID**
1. In Syncthing Web UI
2. Select your `Project5001/Harvest` folder
3. Copy folder ID from URL

### **Device IDs**
- Each device has a unique Syncthing ID
- Found in Syncthing Web UI → My Devices
- Required for device rotation

## 📱 iPhone Setup

### **1. Install Syncthing iOS**
- Download from App Store
- Create account and add main node as device

### **2. Share Project5001/Harvest Folder**
- In main node's Syncthing
- Share the `Project5001/Harvest` folder with your iPhone
- Accept on iPhone
- **Set the iPhone as a receive-only node** (do not enable send permissions)

### **3. Install Music Player**
- VLC (recommended)
- Or any app that can access Files app
- Point to synced `Project5001/Harvest` folder

> **Common Pitfalls:**
> - Make sure you are syncing the `Project5001/Harvest` folder, NOT the project root
> - Folder ID, Device ID, and API URL should be taken from your main node (laptop/desktop), not the phone
> - The iPhone should be set as a receive-only node in Syncthing

## 🍪 YouTube Cookies Required!

**YouTube now requires authentication for most music downloads.**

1. **Copy the template:**
   ```bash
   cp cookies.example.txt cookies.txt
   ```

2. **Get your YouTube cookies:**
   - Go to YouTube and log in
   - Open browser DevTools (F12)
   - Go to Application/Storage tab
   - Find 'Cookies' → 'https://youtube.com'
   - Copy the values for required cookies (see `cookies.example.txt` for details)

3. **The harvester will automatically use `cookies.txt` for all downloads.**

If you do not provide cookies, most downloads will fail or require sign-in.

## 🚨 Troubleshooting

### **Common Issues**

**yt-dlp not found:**
```bash
pip install yt-dlp
```

**ffmpeg not found:**
- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
  - Or use: `winget install ffmpeg`
  - Or use: `scoop install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

**Syncthing API errors:**
```bash
# Check if Syncthing is running
curl http://localhost:8384/rest/system/status
```

**Rate limiting:**
- System automatically rotates devices
- Check rotation status: `python status.py`
- Manual rotation available in logs

**iPhone sync issues:**
- Ensure Syncthing iOS has background app refresh enabled
- Check storage space (50GB+ Recommended)
- Verify folder sharing permissions

### **Reset Configuration**
```bash
# Remove config and start over
rm -rf config/
rm -rf Project5001/
python initialiser.py --setup
```

## 🎯 Next Steps

1. **Start with Main Node**: Set up your home laptop first
2. **Add Secondary Node**: Configure your travel laptop
3. **Setup iPhone**: Install Syncthing iOS and music player
4. **Monitor & Optimize**: Use status tools to monitor performance
5. **Scale Up**: Add more devices to the rotation pool

## 📚 Full Documentation

- **CLI Management**: `python cli.py --help`
- **System Initializer**: `python initialiser.py --help`
- **Configuration**: `config.py` and generated JSON files
- **Database Schema**: `database.py`
- **Rate Limiting**: `rate_limiter.py`
- **Advanced Harvester**: `harvester_v2.py`

## 🆘 Support

- **Logs**: Check `Project5001/Logs/` for detailed error messages
- **Status**: `python initialiser.py --status`
- **Health Check**: `python initialiser.py --health`
- **Maintenance**: `python initialiser.py --maintenance` 