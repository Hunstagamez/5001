# 🎧 Project 5001
A self-hosted, fault-tolerant music archival system built to overcome YouTube's 5,000 playlist limit. Offline-first. Spite-built. Closed-system.
> *Youtube limited me to 5000 songs, so I am taking matters into my own hands.*

---

**Project 5001 (or, just 5001)** is made to free me.  
It started the moment I realised YouTube wouldn't save more than 5,000 tracks in a playlist.  
No subscription, no algorithm, no ads, no desk jockeys picking what songs I get to keep.  
This project is my way of taking back control from bloat, from drift, from artificial caps.

It's not a streaming service.  
It's not a database.  
It's a vault. My vault of taste, curated and indestructible.

Built around a single principle:

> _My playlist is mine, not Google's._

---

## ✦ Philosophy

- **Offline-first.** If the Google explodes tomorrow, the music stays.
- **Sync everything. Own everything. Back everything.**
- **No compression. No DMCA victims. No missing tracks.**
- Built by me. Powered by my music. Shared with you.

---

## 🚀 Quick Start

### **One-Command Setup**
```bash
git clone https://github.com/Hunstagamez/5001.git
cd 5001
python initialiser.py --setup
```

### **Start the System**
```bash
# Quick start (checks health and starts if ready)
python initialiser.py --quick

# Or start manually
python initialiser.py --start
```

### **Manage Your System**
```bash
# Full management interface
python cli.py

# Check status
python initialiser.py --status
```

---

## 🧱 The Stack

- 🛠️ `yt-dlp` for harvesting  
- 🎧 `mutagen` for tagging  
- 🧬 `Syncthing` for device mesh  
- 🎛️ `FFmpeg` for audio conversion
- 🐍 `Python 3.8+` for orchestration
- 📊 `SQLite` for metadata storage

---

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

---

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
- Main archive playlist (all tracks)
- Recent additions (last 30 days)
- Monthly playlists (last 6 months)
- Artist-specific playlists
- Favorites playlist (recent additions)

### **Priority Sync**
- New tracks sync first
- Backfill older content
- Full library on iPhone
- No bandwidth throttling

---

## 🎵 Audio Quality

- **Target**: 256kbps MP3
- **Fallback**: 192k, 128k, 96k if needed
- **Storage**: <80GB for 5000+ tracks
- **Format**: MP3 with full metadata tagging

---

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

---

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

---

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

---

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

---

## 📚 Documentation

- **Quick Start**: `QUICK_START.md`
- **CLI Management**: `python cli.py --help`
- **System Initializer**: `python initialiser.py --help`
- **Configuration**: `config.py` and generated JSON files
- **Database Schema**: `database.py`
- **Rate Limiting**: `rate_limiter.py`
- **Advanced Harvester**: `harvester_v2.py`

---

## 🆘 Support

- **Logs**: Check `Project5001/Logs/` for detailed error messages
- **Status**: `python initialiser.py --status`
- **Health Check**: `python initialiser.py --health`
- **Maintenance**: `python initialiser.py --maintenance`

---

## ⚠️ DISCLAIMER

> This project is intended for personal use only.  
> It does not distribute or host any copyrighted content.  
> All tools used (e.g. yt-dlp) are publicly available and legally maintained.  
> The developer does not condone piracy or public redistribution of copyrighted material.

---

## 🕳️ Lore

> Project 5001 isn't named after a file.  
> It's named after the **first song YouTube wouldn't let me save**.

---

**Take back control of your music.** 🎧

---
