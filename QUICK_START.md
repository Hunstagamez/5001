# 🎧 Project 5001 - Quick Start Guide

### 1. **Clone and Setup**
```bash
git clone <your-repo>
cd 5001
python setup_project5001.py
```

### 2. **Follow the Interactive Setup**
The setup script will guide you through:
- Choosing your node type (Main/Secondary/Mobile)
- Configuring YouTube playlists
- Setting up Syncthing integration
- Testing the configuration

### 3. **Start Your Node**
```bash
# Main node (downloads from YouTube)
python harvester_v2.py main --daemon

# Or use systemd
sudo systemctl enable project5001-main-node.service
sudo systemctl start project5001-main-node.service
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
- Can be promoted to download duty should something happen to main node.

### **Mobile Node** (iPhone)
- Uses Syncthing iOS app
- Full IPhone library sync
- Offline playback with VLC or preferred app

## 🔧 Core Features

### **Smart Rate Limiting Detection**
- Automatically detects YouTube rate limiting
- Rotates between devices to avoid blocks
- Intelligent cooldown periods
- Aggressive download strategy (fuck YouTube)

### **Distributed RAID-esque System**
- Multiple devices hold complete copies
- No single point of failure
- Automatic failover and recovery
- P2P mesh networking via Syncthing
- Plug-N-Play node expansion functionality

### **Priority Sync**
- New tracks sync first
- Backfill older content
- Full library on iPhone
- No bandwidth throttling

## 📊 Monitoring

### **Check Status**
```bash
python status.py
```

### **View Logs**
```bash
# Main node
tail -f Project5001/Logs/main-node.log

# Secondary node  
tail -f Project5001/Logs/secondary-node.log
```

### **Database Stats**
```bash
python status.py --json
```

## 🎵 Audio Quality

- **Target**: 256kbps MP3
- **Fallback**: 192k, 128k, 96k if needed
- **Storage**: <80GB for 5000+ tracks
- **Format**: MP3 with full metadata tagging

## 🔄 Syncthing Setup

> **Important:** You must sync the `Project5001/Harvest` folder (NOT the root) between your devices. This is where all music is downloaded and stored. Syncing the wrong folder will prevent your hive from coordinating your catalogue.

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
> - Make sure you are syncing the `Project5001/Harvest` folder, NOT the project root.
> - Folder ID, Device ID, and API URL should be taken from your main node (laptop/desktop), not the phone.
> - The iPhone should be set as a receive-only node in Syncthing.

## 🍪 YouTube Cookies Required!

**YouTube now requires authentication for most music downloads.**

1. **Export your YouTube cookies:**
   - Install the [Get cookies.txt] browser extension on your select browser.
   - Go to youtube.com and sign in.
   - Click the extension and export cookies for youtube.com.
   - Save the file as `cookies.txt` in your Project 5001 directory.

2. **The harvester will automatically use `cookies.txt` for all downloads.**

If you do not provide cookies, most downloads will fail or require sign-in.

## 🚨 Troubleshooting

### **Common Issues**

**yt-dlp not found:**
```bash
pip install yt-dlp
```

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
- Check storage space (50GB+ Recommended, though it de)
- Verify folder sharing permissions

### **Reset Configuration**
```bash
# Remove config and start over
rm -rf config/
rm -rf Project5001/
python setup_project5001.py
```

## 🎯 Next Steps

1. **Start with Main Node**: Set up your home laptop first
2. **Add Secondary Node**: Configure your current laptop
3. **Setup iPhone**: Install Syncthing iOS and music player
4. **Monitor & Optimize**: Use status tools to monitor performance
5. **Scale Up**: Add more devices to the rotation pool

## 📚 Full Documentation

- **Technical Details**: `TECHNICAL_README.md`
- **Configuration**: `config.py` and generated JSON files
- **Database Schema**: `database.py`
- **Rate Limiting**: `rate_limiter.py`
- **Advanced Harvester**: `harvester_v2.py`

## 🆘 Support

- **Logs**: Check `Project5001/Logs/` for detailed error messages
- **Status**: Use `python status.py` for system health
- **Configuration**: Review generated JSON files in `config/`
- **Database**: SQLite database in `Project5001/harvest.db`

---

**May your harvest be bountiful.** 