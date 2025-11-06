from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import csv
import os
from typing import List, Dict
import threading
from detection_service import detection_service

app = FastAPI(title="Defect Detection API with Camera")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_FILE = "bottle_data.csv"

# Initialize detection service on startup
@app.on_event("startup")
async def startup_event():
    if detection_service.initialize():
        detection_service.start()
        # Start processing in background thread
        thread = threading.Thread(target=detection_service.run_loop, daemon=True)
        thread.start()
        print("✅ Detection service started successfully")
    else:
        print("❌ Failed to initialize detection service")

@app.on_event("shutdown")
async def shutdown_event():
    detection_service.stop()
    print("🛑 Detection service stopped")

def read_bottles_from_csv() -> List[Dict]:
    """Read all bottles from CSV file"""
    bottles = []
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    bottles.append(row)
        except Exception as e:
            print(f"Error reading CSV: {e}")
    return bottles

def calculate_stats(bottles: List[Dict]) -> Dict:
    """Calculate statistics from bottles data"""
    total = len(bottles)
    defective = sum(1 for b in bottles if b.get('Status') == 'Defective')
    non_defective = sum(1 for b in bottles if b.get('Status') == 'Non-Defective')
    defect_rate = (defective / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "defective": defective,
        "nonDefective": non_defective,
        "defectRate": defect_rate
    }

def generate_video_stream():
    """Generate video stream from detection service"""
    while True:
        frame = detection_service.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/")
async def root():
    return {"message": "Defect Detection API with Integrated Camera", "status": "running"}

@app.get("/api/video-feed")
async def video_feed():
    """Stream video feed with detections"""
    return StreamingResponse(
        generate_video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/api/bottles")
async def get_bottles():
    """Get all bottles and statistics"""
    bottles = read_bottles_from_csv()
    stats = calculate_stats(bottles)
    current = detection_service.get_current_status()
    
    return {
        "bottles": bottles,
        "stats": stats,
        "current": current
    }

@app.get("/api/bottles/{bottle_id}")
async def get_bottle(bottle_id: int):
    """Get a specific bottle by ID"""
    bottles = read_bottles_from_csv()
    for bottle in bottles:
        if int(bottle.get('Bottle Number', 0)) == bottle_id:
            return bottle
    return {"error": "Bottle not found"}

@app.get("/api/stats")
async def get_stats():
    """Get only statistics"""
    bottles = read_bottles_from_csv()
    return calculate_stats(bottles)

@app.get("/api/current")
async def get_current():
    """Get the current bottle being inspected"""
    return detection_service.get_current_status()

@app.get("/api/camera-status")
async def camera_status():
    """Check if camera is working"""
    return {
        "running": detection_service.running,
        "initialized": detection_service.cap is not None and detection_service.cap.isOpened()
    }

@app.get("/alert.wav")
async def get_alert_sound():
    """Serve the alert sound file"""
    alert_file = "alert.wav"
    if os.path.exists(alert_file):
        return FileResponse(alert_file, media_type="audio/wav")
    return {"error": "Alert sound file not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
