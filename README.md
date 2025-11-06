# 🍾 Bottle Defect Detection System

An AI-powered real-time defect detection system for bottle quality control using YOLOv8 and React. Detects missing caps, labels, and damaged plastic bottles with a modern web interface.

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![React](https://img.shields.io/badge/React-18+-61DAFB)

---

## ✨ Features

- 🎥 **Real-time Camera Feed** - Live bottle inspection
- 🤖 **AI Detection** - YOLOv8-based defect detection
- 🔊 **Audio Alerts** - Sound notification for defective bottles
- 📊 **Modern UI** - React TypeScript web interface
- 💾 **Data Logging** - CSV export of all inspections
- 📸 **Screenshot Capture** - Auto-save images of detected bottles

---

## 🚀 Quick Start

### Step 1: Download Model Weights

The trained YOLOv8 model is **required** to run the system.

**Download the model file:**
👉 [Download best.pt from Google Drive](https://drive.google.com/file/d/1tsV7AMizhKCgzlVkLGEkOrFpr6lFGzjD/view?usp=sharing)

**Instructions:**
1. Click the link above
2. Click "Download" (⬇️ icon in top right)
3. Save `best.pt` to the **project root folder**
   ```
   Defect-Detection-system-main/
   ├── best.pt  ← Place the downloaded file here
   ├── START.bat
   ├── api_server_integrated.py
   └── ...
   ```

> ⚠️ **Important:** The model file is ~80MB. Make sure you have enough space.

---

## 📦 Installation

### Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Webcam** - USB or built-in camera

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Packages installed:**
- `ultralytics` - YOLOv8 framework
- `opencv-python` - Camera and image processing
- `fastapi` - Backend API server
- `uvicorn` - ASGI server

### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

**Packages installed:**
- React, TypeScript, Vite
- TailwindCSS for styling
- Lucide React for icons

---

## 🎮 Running the System

### Method 1: One-Click Start (Recommended)

**Windows:**
```bash
# Just double-click this file:
START.bat
```

This will:
1. Start the backend + camera
2. Start the frontend dev server
3. Wait for your input
   - Press **ENTER** to open browser
   - Press **ESC** to close everything

### Method 2: Manual Start

**Terminal 1 - Backend:**
```bash
python api_server_integrated.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Open Browser:**
Navigate to `http://localhost:3000`

---

## 🖥️ System Interface

### Web Dashboard

```
┌────────────────────────────────────┐
│ 📦 Defect Detection System         │
│    Real-time Quality Control       │
└────────────────────────────────────┘

┌──────────┬─────────────────────────┐
│          │  CURRENT STATUS         │
│  Camera  │  ┌──────────────────┐   │
│  Feed    │  │  NON-DEFECTIVE   │   │
│  (Left   │  └──────────────────┘   │
│  Half)   │                         │
│          │  COMPONENT CHECKS       │
│  Live    │  ✓ Cap: Detected        │
│  Stream  │  ✓ Label: Detected      │
│          │  ✓ Plastic: Good        │
└──────────┴─────────────────────────┘
```

### Detection Logic

The system checks for:
- ✅ **Cap** - Present or Missing
- ✅ **Label** - Present or Missing  
- ✅ **Plastic** - Good or Damaged

**Status:**
- **Non-Defective** - All components present and good
- **Defective** - Any component missing or damaged

---

## 🔧 Configuration

### Detection Settings

Edit `detection_service.py`:

```python
# Detection interval (seconds before new bottle)
TIME_THRESHOLD_IN_FRAME = 3.0

# Camera region of interest (left half)
ROI_X_START = 0.0   # Left edge
ROI_X_END = 0.5     # Middle
ROI_Y_START = 0.0   # Top
ROI_Y_END = 1.0     # Bottom
```

### Audio Alert

- **Sound File:** `alert.wav` (in root folder)
- **Trigger:** Defective bottle detected
- **Behavior:** Plays immediately, repeats every 5 seconds
- **Stops:** When bottle becomes non-defective

---

## 📁 Project Structure

```
Defect-Detection-system-main/
├── best.pt                      # YOLOv8 model (download from Drive)
├── alert.wav                    # Alert sound file
├── api_server_integrated.py     # FastAPI backend server
├── detection_service.py         # Detection logic & camera
├── bottle_data.csv              # Inspection logs
├── requirements.txt             # Python dependencies
├── START.bat                    # Main launcher
├── start_system.ps1             # PowerShell script
├── Times New Roman.ttf          # UI font
├── screenshots/                 # Auto-saved bottle images
└── frontend/                    # React web interface
    ├── package.json
    ├── src/
    │   ├── App.tsx
    │   ├── types.ts
    │   └── components/
    │       └── LiveView.tsx     # Main UI component
    └── ...
```

---

## 🎯 How It Works

1. **Camera captures** bottle in detection zone (left half of frame)
2. **YOLOv8 model** detects cap, label, and plastic condition
3. **Backend processes** detection and determines status
4. **Frontend displays** live camera feed and results
5. **Audio alert** plays if bottle is defective (loops every 5 seconds)
6. **Data logged** to CSV after 3 seconds
7. **Screenshot saved** when bottle leaves frame

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/current` | GET | Current bottle status |
| `/api/camera-status` | GET | Camera connection status |
| `/api/video-feed` | GET | MJPEG video stream |
| `/alert.wav` | GET | Alert sound file |

---

## 🛑 Stopping the System

### If using START.bat:
Press **ESC** in the launcher window

### If running manually:
Close both terminal windows (Ctrl+C)

---

## 🐛 Troubleshooting

### Camera not detected
- Check if webcam is connected
- Try changing camera index in `detection_service.py`: `cv2.VideoCapture(0)` → `cv2.VideoCapture(1)`

### Model not loading
- Ensure `best.pt` is in the root folder
- Check file size (~80MB)
- Re-download from Google Drive if corrupted

### Audio not playing
- Ensure `alert.wav` exists in root folder
- Check browser audio permissions
- Click on page first (browser autoplay policy)

### Frontend not loading
- Check if port 3000 is available
- Run `npm install` in frontend folder
- Clear browser cache

### Detection too fast/slow
- Adjust `TIME_THRESHOLD_IN_FRAME` in `detection_service.py`
- Default is 3 seconds

---

## 📸 Data Output

### CSV Log (`bottle_data.csv`)
```csv
Bottle Number,Cap,Label,Plastic,Status,Day,Date,Time
1,Detected,Detected,Good,Non-Defective,Wednesday,06/11/24,13:30:45
2,Missing,Detected,Good,Defective,Wednesday,06/11/24,13:30:52
```

### Screenshots
- Saved in `screenshots/` folder
- Named: `bottle_1.png`, `bottle_2.png`, etc.
- Captured when bottle leaves detection zone

---

## 🔑 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **ESC** | Close all windows (in START.bat) |
| **ENTER** | Open web browser (in START.bat) |

---

## 🎨 Tech Stack

**Backend:**
- Python 3.8+
- YOLOv8 (Ultralytics)
- FastAPI
- OpenCV
- Uvicorn

**Frontend:**
- React 18
- TypeScript
- Vite
- TailwindCSS
- Lucide Icons

---

## 📝 Notes

- Detection zone is the **left half** of camera feed
- System records a bottle after **3 seconds** in frame
- Audio alert **loops every 5 seconds** while defective
- Camera feed shows **only the detection area** (cropped)
- Model file must be downloaded separately from Google Drive

---

## 📄 License

This project is for educational and commercial use.

---

## 🤝 Support

For issues or questions, check the troubleshooting section or review the code comments.

---

**Made with ❤️ for Quality Control**
