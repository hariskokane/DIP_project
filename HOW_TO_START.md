# How to Start the System

## 🚀 Quick Start

### Option 1: Double-Click START.bat (Recommended)
1. Double-click `START.bat`
2. Wait for both windows to open
3. Press **ENTER** to open web browser
4. Press **ESC** anytime to close everything

### Option 2: Use PowerShell Script Directly
1. Right-click `start_system.ps1`
2. Select "Run with PowerShell"
3. Press **ENTER** to open browser
4. Press **ESC** to close all

### Option 3: Manual Start
```bash
# Terminal 1
python api_server_integrated.py

# Terminal 2
cd frontend
npm run dev
```

---

## ⌨️ Keyboard Controls

| Key | Action |
|-----|--------|
| **ESC** | Close all windows and exit |
| **ENTER** | Open web browser to http://localhost:3000 |

---

## 📺 What Happens

1. **Backend + Camera** window opens (Python)
2. **Frontend** window opens (Node.js/Vite)
3. System is ready in ~10 seconds
4. Press ENTER to open browser
5. Press ESC anytime to close everything

---

## 🛑 Stopping the System

### Easy Way:
Press **ESC** in the launcher window

### Manual Way:
Close both terminal windows (Backend + Frontend)

---

## 📝 Files

- `START.bat` - Main launcher (double-click this)
- `start_system.ps1` - PowerShell script (handles ESC key)
- `start_all.bat` - Old launcher (still works)
- `start_integrated.bat` - Alternative launcher

---

## ✨ Features

- ✅ One-click start
- ✅ ESC to close everything
- ✅ Auto browser opening
- ✅ Clean shutdown
- ✅ No orphan processes

---

Enjoy your streamlined startup! 🎉
