# 🍪 Project 5001 - Cookie Automation Guide

## Overview

Project 5001 now includes automated tools to extract YouTube cookies from your browsers, eliminating the need for manual cookie extraction. This guide covers all the available methods.

## 🚀 Quick Start

### Method 1: CLI Menu (Easiest)
```bash
python cli.py
# Then select: 8. 🍪 Cookie Management
# Then select: 1. 🔍 Extract Cookies Automatically
```

### Method 2: Direct Script
```bash
python cookie_automator.py
```

### Method 3: Browser Extension
1. Go to YouTube and log in
2. Open browser DevTools (F12)
3. Copy and paste the contents of `cookie_extension.js`
4. Press Enter to run
5. Click the red download button

## 🔧 How It Works

### Automatic Extraction (`cookie_automator.py`)

The automation tool:

1. **Scans for browsers** - Detects Chrome, Edge, Firefox on Windows/macOS/Linux
2. **Extracts cookies** - Reads YouTube cookies from browser databases
3. **Formats correctly** - Converts to Netscape format for yt-dlp
4. **Tests automatically** - Downloads a test video to verify cookies work
5. **Creates cookies.txt** - Saves the working cookies file

### Browser Extension (`cookie_extension.js`)

The browser extension:

1. **Runs in browser** - No need to close browsers
2. **Extracts live cookies** - Gets current session cookies
3. **Creates download link** - Generates cookies.txt file
4. **Works immediately** - No file locking issues

## 📋 Requirements

### For Automatic Extraction:
- Python 3.8+
- Browsers must be **closed** (to avoid file locking)
- Logged into YouTube in at least one browser

### For Browser Extension:
- Any modern browser (Chrome, Firefox, Edge, Safari)
- Must be logged into YouTube
- JavaScript enabled

## 🛠️ Troubleshooting

### "File being used by another process"
**Solution:** Close all browser windows and try again
```bash
# Close browsers, then run:
python cookie_automator.py
```

### "No YouTube cookies found"
**Solutions:**
1. Make sure you're logged into YouTube
2. Try the browser extension method instead
3. Check if you're using a different browser profile

### "Cookie test failed"
**Solutions:**
1. Cookies might be expired - extract fresh ones
2. YouTube might have changed their API
3. Try logging out and back into YouTube

## 🔄 Integration with Project 5001

### CLI Integration
The cookie management is fully integrated into the Project 5001 CLI:

```bash
python cli.py
# Menu options:
# 8. 🍪 Cookie Management
#    ├── 1. 🔍 Extract Cookies Automatically
#    ├── 2. 🧪 Test Current Cookies
#    ├── 3. 📋 Show Cookie Instructions
#    └── 4. 📁 View Current Cookies
```

### Automatic Testing
After extraction, the system automatically:
- Tests cookies with a sample download
- Reports success/failure
- Provides troubleshooting tips

## 📁 File Structure

```
Project5001/
├── cookie_automator.py      # Main automation script
├── cookie_extension.js      # Browser extension script
├── cookies.txt             # Generated cookies file
├── cookies.example.txt     # Template file
└── COOKIE_AUTOMATION.md    # This guide
```

## 🔒 Security Notes

- **Never commit cookies.txt** - It contains your authentication
- **Keep cookies private** - Don't share with others
- **Regular updates** - Cookies expire, refresh periodically
- **Browser security** - Only extract from your own browsers

## 🎯 Best Practices

1. **Use automatic extraction** when browsers are closed
2. **Use browser extension** when browsers are open
3. **Test cookies regularly** - they expire over time
4. **Keep browsers updated** - for best compatibility
5. **Log into YouTube** before extracting cookies

## 🚨 Common Issues

### Windows Issues
- **File locking**: Close browsers completely
- **Permission errors**: Run as administrator if needed
- **Path issues**: Use forward slashes in paths

### macOS Issues
- **Safari cookies**: Not supported, use Chrome/Firefox
- **Permission prompts**: Allow access to browser data
- **Keychain access**: May need to unlock keychain

### Linux Issues
- **Browser not found**: Install browsers in standard locations
- **Permission denied**: Check file permissions
- **SQLite errors**: Install sqlite3 development packages

## 📞 Support

If you encounter issues:

1. Check this guide first
2. Try the browser extension method
3. Use manual extraction as fallback
4. Check Project 5001 logs for errors
5. Report issues on the project repository

---

**Remember**: Cookie automation makes Project 5001 much easier to use, but cookies still expire and need refreshing periodically. The system will tell you when cookies need updating! 