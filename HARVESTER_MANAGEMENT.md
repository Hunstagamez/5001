# 🎵 Project 5001 - Harvester Management

## Overview

The harvester management system ensures only one harvester instance can run at a time, provides real-time status monitoring, and offers dynamic menu options based on the current harvester state.

## 🚀 Key Features

### Single Instance Control
- **PID File Management**: Uses `Project5001/harvester.pid` to track running instances
- **Process Validation**: Verifies processes are actually running, not just PID file exists
- **Automatic Cleanup**: Removes stale PID files when processes die unexpectedly
- **Prevents Multiple Instances**: Blocks starting new harvesters when one is already running

### Real-time Status Monitoring
- **Live Status**: Check if harvester is running, get PID, start time, and mode
- **Status File**: Stores detailed status in `Project5001/harvester_status.json`
- **Process Health**: Validates process is actually alive, not just PID file exists

### Dynamic Menu System
- **Smart Options**: Menu changes based on harvester status
- **When Stopped**: Shows "Start Harvester" and "Run Single Cycle" options
- **When Running**: Shows "Stop Harvester" and "View Real-time Logs" options
- **Context Aware**: Only shows relevant actions for current state

### Real-time Log Viewing
- **Separate Terminal**: View logs in real-time in a new terminal window
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Auto-launch**: `launch_log_viewer.py` opens log viewer in new terminal
- **Manual Option**: `view_harvester_logs.py` for manual execution

## 📋 Usage

### Starting the Harvester

```bash
# Via CLI (recommended)
python cli.py
# Navigate to: Harvester Control -> Start Harvester (Daemon)

# Via initialiser
python initialiser.py --start

# Direct (not recommended - bypasses instance control)
python harvester_v2.py main --daemon
```

### Stopping the Harvester

```bash
# Via CLI
python cli.py
# Navigate to: Harvester Control -> Stop Harvester

# Via initialiser
python initialiser.py --stop

# The harvester will also stop when you press Ctrl+C
```

### Checking Status

```bash
# Via CLI
python cli.py
# Navigate to: Harvester Control -> Harvester Status

# Via test script
python test_harvester_manager.py

# Check manually
ls Project5001/harvester.pid  # If exists, harvester is running
```

### Viewing Real-time Logs

```bash
# Auto-launch in new terminal (recommended)
python launch_log_viewer.py

# Manual execution
python view_harvester_logs.py

# Via CLI (shows recent logs)
python cli.py
# Navigate to: Harvester Control -> View Real-time Logs
```

## 🔧 Technical Details

### Files Created

- `Project5001/harvester.pid` - Process ID file (created when daemon starts)
- `Project5001/harvester_status.json` - Status information
- `Project5001/Logs/harvester.log` - Harvester log file

### Manager Components

- **HarvesterManager**: Core management class
- **PID File Handling**: Process tracking and validation
- **Status Management**: JSON-based status storage
- **Process Control**: Start/stop with proper cleanup

### Menu Logic

```python
if not harvester_running:
    # Show start options
    - Start Harvester (Daemon)
    - Run Single Harvest Cycle
    - Harvester Status
    - Test Configuration
    - Manage YouTube Playlists
else:
    # Show stop and monitoring options
    - Stop Harvester
    - Harvester Status
    - View Real-time Logs
    - Test Configuration
    - Manage YouTube Playlists
```

## 🛠️ Troubleshooting

### Harvester Won't Start

1. **Check if already running**:
   ```bash
   python test_harvester_manager.py
   ```

2. **Clean up stale PID file**:
   ```bash
   rm Project5001/harvester.pid
   ```

3. **Check logs**:
   ```bash
   tail -f Project5001/Logs/harvester.log
   ```

### Harvester Won't Stop

1. **Force stop via CLI**:
   ```bash
   python cli.py -> Harvester Control -> Stop Harvester
   ```

2. **Manual process kill**:
   ```bash
   # Windows
   taskkill /F /IM python.exe
   
   # Linux/macOS
   pkill -f harvester_v2.py
   ```

3. **Clean up PID file**:
   ```bash
   rm Project5001/harvester.pid
   ```

### Log Viewer Issues

1. **Manual execution**:
   ```bash
   python view_harvester_logs.py
   ```

2. **Check log file exists**:
   ```bash
   ls Project5001/Logs/harvester.log
   ```

3. **Start harvester first**:
   ```bash
   python cli.py -> Harvester Control -> Start Harvester
   ```

## 🔄 Migration from Old System

The new system is backward compatible. If you have existing harvesters running:

1. **Stop old harvester**:
   ```bash
   # Old method
   pkill -f harvester_v2.py
   ```

2. **Start with new system**:
   ```bash
   python cli.py -> Harvester Control -> Start Harvester
   ```

3. **Verify new management**:
   ```bash
   python test_harvester_manager.py
   ```

## 📊 Status Information

The status file contains:

```json
{
  "pid": 12345,
  "start_time": "2024-01-01T12:00:00",
  "status": "running",
  "daemon_mode": true,
  "last_activity": "2024-01-01T12:05:00"
}
```

## 🎯 Best Practices

1. **Always use CLI**: Use `python cli.py` for management
2. **Check status first**: Verify harvester state before actions
3. **Use log viewer**: Monitor real-time activity during harvests
4. **Clean shutdown**: Use stop command, not Ctrl+C when possible
5. **Regular monitoring**: Check status periodically

## 🆘 Support

- **Logs**: Check `Project5001/Logs/` for detailed error messages
- **Status**: Use `python test_harvester_manager.py` for diagnostics
- **CLI Help**: Use `python cli.py` -> Help & Documentation
- **Issues**: Check PID file and process status if problems occur 