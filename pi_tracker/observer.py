import os
import time
import json
import logging
import requests
import cv2
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('observer.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ServerInfo:
    server_url: str
    api_key: Optional[str] = None
    status: str = "inactive"

class ArtObserver:
    def __init__(self, camera_id: str, artwork_id: str, lambda_url: str):
        """Initialize the art observation system"""
        self.camera_id = camera_id
        self.artwork_id = artwork_id
        self.lambda_url = lambda_url
        self.server_info = None
        self.is_running = False
        
        # Initialize ArUco detector
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        
        # State tracking
        self.active_observations = {}  # marker_id -> start_time
        self.section_times = {}  # marker_id -> {section: time}
        
    def check_server_status(self) -> bool:
        """Query AWS Lambda to get EC2 server status"""
        try:
            response = requests.get(
                self.lambda_url,
                params={'camera_id': self.camera_id},
                timeout=5
            )
            if response.ok:
                data = response.json()
                self.server_info = ServerInfo(
                    server_url=data.get('server_url'),
                    api_key=data.get('api_key'),
                    status=data.get('status', 'inactive')
                )
                return self.server_info.status == 'active'
            return False
        except Exception as e:
            logging.error(f"Failed to check server status: {str(e)}")
            return False
            
    def start(self, video_source=0):
        """Start the observation system"""
        self.is_running = True
        cap = cv2.VideoCapture(video_source)
        
        last_server_check = 0
        server_check_interval = 10  # seconds
        
        try:
            while self.is_running:
                current_time = time.time()
                
                # Check server status every 10 seconds
                if current_time - last_server_check >= server_check_interval:
                    if self.check_server_status():
                        logging.info(f"Server active at {self.server_info.server_url}")
                    last_server_check = current_time
                
                # Process frame if we have an active server
                ret, frame = cap.read()
                if not ret:
                    logging.error("Failed to read frame")
                    continue
                    
                self.process_frame(frame)
                
                # Small delay to prevent CPU overload
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logging.info("Stopping observation system")
        finally:
            cap.release()
            self.is_running = False
            
    def process_frame(self, frame: np.ndarray):
        """Process a single frame for ArUco markers"""
        try:
            if not self.server_info or self.server_info.status != 'active':
                return
                
            height, width = frame.shape[:2]
            third_width = width // 3
            
            corners, ids, _ = self.detector.detectMarkers(frame)
            
            if ids is not None:
                for idx, marker_corners in enumerate(corners):
                    marker_id = int(ids[idx])
                    
                    # Calculate marker position
                    center = np.mean(marker_corners[0], axis=0)
                    center_x = int(center[0])
                    
                    # Determine section (1, 2, or 3)
                    section = 1 if center_x < third_width else 2 if center_x < 2 * third_width else 3
                    
                    self.update_observation(marker_id, section)
                    
        except Exception as e:
            logging.error(f"Error processing frame: {str(e)}")
            
    def update_observation(self, marker_id: int, current_section: int):
        """Update observation times and send to server"""
        current_time = time.time()
        
        # Initialize tracking for new markers
        if marker_id not in self.active_observations:
            self.active_observations[marker_id] = current_time
            self.section_times[marker_id] = {1: 0, 2: 0, 3: 0}
            self.report_observation_start(marker_id)
            return
            
        # Update section times
        elapsed = current_time - self.active_observations[marker_id]
        self.section_times[marker_id][current_section] += elapsed
        self.active_observations[marker_id] = current_time
        
        # Report updated times
        self.report_observation_update(marker_id)
        
    def report_observation_start(self, marker_id: int):
        """Report new observation to server"""
        if not self.server_info or not self.server_info.server_url:
            return
            
        try:
            data = {
                'camera_id': self.camera_id,
                'artwork_id': self.artwork_id,
                'aruco_id': marker_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f"{self.server_info.server_url}/api/observation/start",
                json=data,
                headers={'X-API-Key': self.server_info.api_key} if self.server_info.api_key else None,
                timeout=5
            )
            
            if not response.ok:
                logging.error(f"Failed to report observation start: {response.text}")
                
        except Exception as e:
            logging.error(f"Error reporting observation start: {str(e)}")
            
    def report_observation_update(self, marker_id: int):
        """Report updated section times to server"""
        if not self.server_info or not self.server_info.server_url:
            return
            
        try:
            data = {
                'camera_id': self.camera_id,
                'artwork_id': self.artwork_id,
                'aruco_id': marker_id,
                'section_times': self.section_times[marker_id],
                'total_time': sum(self.section_times[marker_id].values()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f"{self.server_info.server_url}/api/observation/update",
                json=data,
                headers={'X-API-Key': self.server_info.api_key} if self.server_info.api_key else None,
                timeout=5
            )
            
            if not response.ok:
                logging.error(f"Failed to report observation update: {response.text}")
                
        except Exception as e:
            logging.error(f"Error reporting observation update: {str(e)}")
