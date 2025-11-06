import cv2
import numpy as np
from datetime import datetime, timedelta
from ultralytics import YOLO
from PIL import ImageFont, ImageDraw, Image
import csv
import os
import threading
import time
from typing import Dict, Optional

class DetectionService:
    def __init__(self):
        # Model and Classes
        self.MODEL_PATH = "best.pt"
        self.classNames = ['bottle', 'cap', 'cap missing', 'damaged plastic', 'label', 'label missing']
        
        # Paths
        self.CSV_FILE = "bottle_data.csv"
        self.SCREENSHOTS_DIR = "screenshots"
        if not os.path.exists(self.SCREENSHOTS_DIR):
            os.makedirs(self.SCREENSHOTS_DIR)
        
        # Tracking and Logic
        self.DISTANCE_THRESHOLD = 100
        self.TIME_THRESHOLD_IN_FRAME = 3.0  # 3 seconds before new bottle
        
        # ROI (Region of Interest) - Left portion of frame for detection
        # Values are percentages (0.0 to 1.0)
        self.ROI_X_START = 0.0   # Start at left edge (0%)
        self.ROI_X_END = 0.5     # End at middle (50%)
        self.ROI_Y_START = 0.0   # Start at top (0%)
        self.ROI_Y_END = 1.0     # End at bottom (100%)
        
        # Globals
        self.bottle_counter = 0
        self.previous_bottle_number = -1
        self.last_saved_time = datetime.now() - timedelta(seconds=10)
        self.bottle_in_frame = False
        self.bottle_last_seen_time = datetime.now()
        self.previous_bottle = None
        
        # Audio alert tracking
        self.last_defect_alert_time = None
        self.defect_detected_time = None
        self.alert_played = False
        
        # Camera
        self.cap = None
        self.model = None
        self.current_frame = None
        self.current_bottle_status = None
        self.lock = threading.Lock()
        self.running = False
        
    def initialize(self):
        """Initialize camera and model"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            self.model = YOLO(self.MODEL_PATH)
            self.current_bottle_status = self.get_default_bottle_status()
            return True
        except Exception as e:
            print(f"Error initializing: {e}")
            return False
    
    def bbox_center(self, bbox):
        x1, y1, x2, y2 = bbox
        return (x1 + x2) // 2, (y1 + y2) // 2
    
    def bbox_distance(self, bbox1, bbox2):
        x1, y1 = self.bbox_center(bbox1)
        x2, y2 = self.bbox_center(bbox2)
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    
    def get_default_bottle_status(self):
        self.bottle_counter += 1
        return {
            "Bottle Number": self.bottle_counter,
            "Cap": "Not Detected",
            "Label": "Not Detected",
            "Plastic": "Good",
            "Status": "--",
            "Day": datetime.now().strftime("%A"),
            "Date": datetime.now().strftime("%d/%m/%y"),
            "Time": datetime.now().strftime("%H:%M:%S"),
        }
    
    def save_to_csv(self, bottle_status):
        file_exists = os.path.isfile(self.CSV_FILE)
        try:
            with open(self.CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=bottle_status.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(bottle_status)
        except IOError as e:
            print(f"Error saving to CSV: {e}")
    
    def save_screenshot(self, img, bottle_number):
        screenshot_path = os.path.join(self.SCREENSHOTS_DIR, f"bottle_{bottle_number}.png")
        try:
            cv2.imwrite(screenshot_path, img)
        except cv2.error as e:
            print(f"Error saving screenshot: {e}")
    
    def draw_detection_box(self, img, x1, y1, x2, y2, label, color):
        """Draw bounding box on image"""
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Draw label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(img, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return img
    
    def process_frame(self):
        """Process a single frame and return annotated image"""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        success, img_original = self.cap.read()
        if not success:
            return None
        
        img = img_original.copy()
        h, w = img.shape[:2]
        
        # Calculate ROI coordinates
        roi_x1 = int(w * self.ROI_X_START)
        roi_y1 = int(h * self.ROI_Y_START)
        roi_x2 = int(w * self.ROI_X_END)
        roi_y2 = int(h * self.ROI_Y_END)
        
        # Draw ROI rectangle on display image (without text)
        cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 255), 2)
        
        # Extract ROI for detection
        roi_img = img_original[roi_y1:roi_y2, roi_x1:roi_x2]
        
        # Update time fields
        with self.lock:
            self.current_bottle_status["Day"] = datetime.now().strftime("%A")
            self.current_bottle_status["Date"] = datetime.now().strftime("%d/%m/%y")
            self.current_bottle_status["Time"] = datetime.now().strftime("%H:%M:%S")
        
        # Run detection ONLY on ROI
        results = self.model(roi_img, verbose=False)
        
        bottle_detected = False
        temp_cap = "Not Detected"
        temp_label = "Not Detected"
        temp_plastic = "Good"
        
        # Colors
        COLOR_BOTTLE = (255, 0, 0)
        COLOR_PRESENT = (0, 255, 0)
        COLOR_DEFECTIVE = (0, 0, 255)
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Get coordinates relative to ROI
                x1_roi, y1_roi, x2_roi, y2_roi = map(int, box.xyxy[0])
                
                # Convert to full image coordinates
                x1 = x1_roi + roi_x1
                y1 = y1_roi + roi_y1
                x2 = x2_roi + roi_x1
                y2 = y2_roi + roi_y1
                
                label = self.classNames[int(box.cls[0])]
                
                if label == 'bottle':
                    bottle_detected = True
                    
                    if not self.bottle_in_frame:
                        self.bottle_in_frame = True
                        self.bottle_last_seen_time = datetime.now()
                    elif (datetime.now() - self.bottle_last_seen_time).total_seconds() >= self.TIME_THRESHOLD_IN_FRAME:
                        if self.previous_bottle is None or self.bbox_distance(self.previous_bottle, [x1, y1, x2, y2]) > self.DISTANCE_THRESHOLD:
                            if self.previous_bottle_number != -1:
                                self.save_screenshot(img_original, self.previous_bottle_number)
                            
                            with self.lock:
                                self.current_bottle_status = self.get_default_bottle_status()
                            self.previous_bottle = [x1, y1, x2, y2]
                    
                    img = self.draw_detection_box(img, x1, y1, x2, y2, "Bottle", COLOR_BOTTLE)
                
                elif label == 'cap':
                    temp_cap = "Detected"
                    img = self.draw_detection_box(img, x1, y1, x2, y2, "Cap", COLOR_PRESENT)
                elif label == 'cap missing':
                    temp_cap = "Missing"
                    img = self.draw_detection_box(img, x1, y1, x2, y2, "Cap Missing", COLOR_DEFECTIVE)
                elif label == 'label':
                    temp_label = "Detected"
                    img = self.draw_detection_box(img, x1, y1, x2, y2, "Label", COLOR_PRESENT)
                elif label == 'label missing':
                    temp_label = "Missing"
                    img = self.draw_detection_box(img, x1, y1, x2, y2, "Label Missing", COLOR_DEFECTIVE)
                elif label == 'damaged plastic':
                    temp_plastic = "Damaged"
                    img = self.draw_detection_box(img, x1, y1, x2, y2, "Damaged Plastic", COLOR_DEFECTIVE)
        
        if bottle_detected:
            with self.lock:
                self.current_bottle_status["Cap"] = temp_cap
                self.current_bottle_status["Label"] = temp_label
                self.current_bottle_status["Plastic"] = temp_plastic
                
                # Mark as Defective if ANY component is missing or damaged
                if temp_cap != "Detected" or temp_label != "Detected" or temp_plastic != "Good":
                    self.current_bottle_status["Status"] = "Defective"
                    
                    # Track defect detection time for audio alert
                    if not self.alert_played:
                        if self.defect_detected_time is None:
                            self.defect_detected_time = datetime.now()
                        elif (datetime.now() - self.defect_detected_time).total_seconds() >= 3.0:
                            # Play alert after 3 seconds
                            self.alert_played = True
                            self.last_defect_alert_time = datetime.now()
                else:
                    self.current_bottle_status["Status"] = "Non-Defective"
                    # Reset alert tracking when non-defective
                    self.defect_detected_time = None
                    self.alert_played = False
            
            current_time = datetime.now()
            if self.current_bottle_status["Bottle Number"] != self.previous_bottle_number and (current_time - self.last_saved_time).seconds >= 2:
                self.save_to_csv(self.current_bottle_status)
                self.previous_bottle_number = self.current_bottle_status["Bottle Number"]
                self.last_saved_time = current_time
        else:
            # Reset if no bottle detected
            if self.bottle_in_frame:
                self.bottle_in_frame = False
        
        # Store current frame
        with self.lock:
            self.current_frame = img
        
        return img
    
    def get_current_status(self) -> Dict:
        """Get current bottle status"""
        with self.lock:
            status = self.current_bottle_status.copy() if self.current_bottle_status else None
            # Add audio alert flag
            if status:
                status['play_alert'] = self.alert_played and self.last_defect_alert_time and \
                                      (datetime.now() - self.last_defect_alert_time).total_seconds() < 1.0
            return status
    
    def get_frame(self):
        """Get current frame as JPEG bytes - Returns only ROI portion"""
        with self.lock:
            if self.current_frame is not None:
                h, w = self.current_frame.shape[:2]
                
                # Calculate ROI coordinates
                roi_x1 = int(w * self.ROI_X_START)
                roi_y1 = int(h * self.ROI_Y_START)
                roi_x2 = int(w * self.ROI_X_END)
                roi_y2 = int(h * self.ROI_Y_END)
                
                # Extract only the ROI portion with detections drawn on it
                roi_frame = self.current_frame[roi_y1:roi_y2, roi_x1:roi_x2]
                
                ret, buffer = cv2.imencode('.jpg', roi_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                return buffer.tobytes()
        return None
    
    def start(self):
        """Start detection service"""
        self.running = True
        
    def stop(self):
        """Stop detection service"""
        self.running = False
        if self.cap is not None:
            self.cap.release()
    
    def run_loop(self):
        """Main processing loop"""
        while self.running:
            self.process_frame()
            time.sleep(0.03)  # ~30 FPS

# Global instance
detection_service = DetectionService()
