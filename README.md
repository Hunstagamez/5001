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

### 1. **Clone and Setup**
```bash
git clone https://github.com/Hunstagamez/5001.git
cd 5001
python initialiser.py --setup
```

### 2. **Configure YouTube Cookies**
```bash
# Copy the template and add your YouTube cookies
cp cookies.example.txt cookies.txt
# Edit cookies.txt with your actual YouTube cookies (see instructions in file)
```

### 3. **Start the System**
```bash
# Quick start (checks health and starts if ready)
python initialiser.py --quick

# Or use the full CLI menu
python cli.py
```

### 4. **Manage Your System**
```bash
# Check status
python initialiser.py --status

# Run maintenance
python initialiser.py --maintenance

# Stop services
python initialiser.py --stop
```

---

## 🎯 Current Features

### ✅ **Working Now**
- **Smart YouTube Playlist Harvesting** - Downloads music from your playlists
- **Intelligent Rate Limiting** - Detects and avoids YouTube blocks
- **Device Rotation** - Distributes downloads across multiple devices
- **Metadata Tagging** - Auto-tags MP3s with artist, title, and source info
- **Database Tracking** - Tracks all downloads and metadata
- **Smart Playlist Generation** - Creates organized playlists automatically:
  - Main archive (all tracks)
  - Recent additions (last 30 days)
  - Monthly playlists (by month)
  - Artist playlists (by artist)
  - Favorites (recent highlights)
- **Syncthing Integration** - Syncs music across your devices
- **Unified CLI Menu** - Easy management interface
- **System Initializer** - One-command setup and startup
- **Health Monitoring** - System status and diagnostics

### 🔄 **Syncthing Setup**
- **Main Node**: Downloads from YouTube, coordinates the network
- **Secondary Nodes**: Receive music via Syncthing
- **Mobile Nodes**: iPhone setup with VLC for playback
- **Automatic Sync**: New tracks sync first, backfill older content

---

## 🛠️ The Stack

- 🛠️ **yt-dlp** - YouTube downloading and metadata extraction
- 🎧 **mutagen** - Audio file tagging and metadata
- 🧬 **Syncthing** - Distributed file synchronization
- 🎬 **FFmpeg** - Audio conversion and processing
- 🐍 **Python 3.8+** - Core application logic
- 📊 **SQLite** - Local database for tracking
- 🎵 **M3U Playlists** - Universal playlist format

---

## 📱 Node Types

### **Main Node** (Home Machine)
- Downloads music from YouTube playlists
- Coordinates the distributed network
- Manages device rotation for rate limiting
- Triggers Syncthing sync after downloads

### **Secondary Node** (Travel Laptop)
- Receives music from main node via Syncthing
- Full library sync
- Can be promoted to download duty if main node fails

### **Mobile Node** (iPhone)
- Uses Syncthing iOS app
- Full iPhone library sync
- Offline playback with VLC or preferred app

---

## 🎵 Audio Quality

- **Target**: 256kbps MP3
- **Fallback**: 192k, 128k, 96k if needed
- **Storage**: <80GB for 5000+ tracks
- **Format**: MP3 with full metadata tagging

---

## 🔧 Management

### **CLI Menu System**
```bash
python cli.py
```
- 🎵 Harvester Control (start/stop/status)
- 📋 Playlist Management (generate all types)
- 📊 System Status (database, files, Syncthing)
- 📁 File Operations (browse, search, cleanup)
- ⚙️ Configuration (view, validate, reload)
- 📝 Logs & Debugging (view, search, cleanup)
- 🔄 Syncthing Operations (rescan, test connection)
- ❓ Help & Documentation

### **System Initializer**
```bash
python initialiser.py --help
```
- `--setup` - Run initial system setup
- `--quick` - Quick start (check health and start if ready)
- `--start` - Start all services
- `--stop` - Stop all services
- `--restart` - Restart all services
- `--status` - Show system status
- `--health` - Check system health
- `--maintenance` - Run maintenance tasks

---

## 📊 Monitoring

### **Check Status**
```bash
python status.py
python status.py --json  # For programmatic use
```

### **View Logs**
```bash
# Main node
tail -f Project5001/Logs/main-node.log

# Secondary node  
tail -f Project5001/Logs/secondary-node.log
```

---

## 🍪 YouTube Cookies Required!

**YouTube now requires authentication for most music downloads.**

1. **Get your cookies:**
   - Go to YouTube and log in
   - Open browser DevTools (F12)
   - Go to Application/Storage → Cookies → https://youtube.com
   - Copy the values for: SID, HSID, SSID, APISID, SAPISID, __Secure-1PSID, __Secure-3PSID, etc.

2. **Add to cookies.txt:**
   ```bash
   cp cookies.example.txt cookies.txt
   # Edit cookies.txt with your actual values
   ```

---

## ⚠️ This Repo Is For Me

You're welcome to read it, fork it, or adapt it.  
But this isn't a product, and it's not a one-size-fits-all.
It's me making sure I get what I want.

---

## 🕳️ Lore

> Project 5001 isn't named after a file.  
> It's named after the **first song YouTube wouldn't let me save**.

---

**Take back control of your music.** 🎧

---

## ⚠️ DISCLAIMER

> This project is intended for personal use only.  
> It does not distribute or host any copyrighted content.  
> All tools used (e.g. yt-dlp) are publicly available and legally maintained.  
> The developer does not condone piracy or public redistribution of copyrighted material.

---

> **Important Architecture Note:**
> 
> **Project 5001's device mesh (the "hive") and Syncthing's file syncing are separate systems.**
> - The device mesh controls which devices can download, coordinate, and rotate for rate limiting.
> - Syncthing handles actual file transfer and folder synchronization between devices.
> 
> **To fully participate in the distributed system, a device must be:**
> 1. Added to the Project 5001 mesh (for download/coordination logic).
> 2. Added to Syncthing (for file syncing).
> 
> **You must add new devices to both Project 5001 and Syncthing for full functionality.**
>
> **Important:** When configuring Syncthing, make sure to sync the `Project5001/Harvest` folder (not just the project root or another folder). This is where all music is downloaded and stored. Syncing the wrong folder will prevent your devices from receiving new music.
>
> - The iPhone should be set up as a receive-only node in Syncthing, syncing only the `Project5001/Harvest` folder. Use VLC or another music player that can access the Files app for playback.
>
> - Folder ID, Device ID, and API URL should be taken from your main node (laptop/desktop), not the phone.

---
