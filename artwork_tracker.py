import cv2
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Tuple, Optional
import json
import requests
import os
from dataclasses import dataclass
from time import time

@dataclass
class ArtworkObservation:
    artwork_id: str  # Location/artwork identifier
    aruco_id: int
    start_time: float
    end_time: float
    section_times: Dict[int, float]  # Section -> time spent

class ArtworkTracker:
    def __init__(self, camera_id: str, artwork_id: str, server_url: str):
        """
        Initialize artwork observation tracker
        Args:
            camera_id: Unique identifier for this camera/pi
            artwork_id: Identifier for the artwork being observed
            server_url: URL of the central server
        """
        self.camera_id = camera_id
        self.artwork_id = artwork_id
        self.server_url = server_url
        
        # Initialize ArUco detector
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        
        # Tracking state
        self.marker_section_times: Dict[int, Dict[int, float]] = {}  # marker_id -> section -> time
        self.marker_last_times: Dict[int, float] = {}  # marker_id -> last_seen_time
        self.marker_current_sections: Dict[int, int] = {}  # marker_id -> current_section
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def process_frame(self, frame: np.ndarray) -> None:
        """Process a single frame and update observation times"""
        try:
            height, width = frame.shape[:2]
            third_width = width // 3
            
            # Detect ArUco markers
            corners, ids, _ = self.detector.detectMarkers(frame)
            current_time = time()
            
            if ids is not None:
                for idx, corners in enumerate(corners):
                    marker_id = int(ids[idx])
                    
                    # Calculate marker position
                    marker_center = np.mean(corners[0], axis=0)
                    center_x = int(marker_center[0])
                    
                    # Determine section (1, 2, or 3)
                    if center_x < third_width:
                        new_section = 1
                    elif center_x < 2 * third_width:
                        new_section = 2
                    else:
                        new_section = 3
                    
                    # Initialize tracking for new markers
                    if marker_id not in self.marker_last_times:
                        self.marker_last_times[marker_id] = current_time
                        self.marker_current_sections[marker_id] = new_section
                        self.marker_section_times[marker_id] = {1: 0, 2: 0, 3: 0}
                        self._report_observation_start(marker_id)
                        continue
                    
                    # Update time for current section
                    if self.marker_current_sections[marker_id] == new_section:
                        elapsed = current_time - self.marker_last_times[marker_id]
                        self.marker_section_times[marker_id][new_section] += elapsed
                    
                    self.marker_current_sections[marker_id] = new_section
                    self.marker_last_times[marker_id] = current_time

        except Exception as e:
            logging.error(f"Error processing frame: {str(e)}")

    def _report_observation_start(self, marker_id: int) -> None:
        """Report the start of a new observation"""
        try:
            data = {
                'camera_id': self.camera_id,
                'artwork_id': self.artwork_id,
                'aruco_id': marker_id,
                'event': 'observation_start',
                'timestamp': datetime.utcnow().isoformat()
            }
            requests.post(f"{self.server_url}/observation/start", json=data)
        except Exception as e:
            logging.error(f"Failed to report observation start: {str(e)}")

    def report_section_times(self) -> None:
        """Report accumulated section times to the server"""
        current_time = time()
        try:
            for marker_id, section_times in self.marker_section_times.items():
                # Only report if we have actual time spent
                if sum(section_times.values()) > 0:
                    observation = ArtworkObservation(
                        artwork_id=self.artwork_id,
                        aruco_id=marker_id,
                        start_time=self.marker_last_times[marker_id],
                        end_time=current_time,
                        section_times=section_times.copy()
                    )
                    
                    data = {
                        'camera_id': self.camera_id,
                        'artwork_id': self.artwork_id,
                        'aruco_id': marker_id,
                        'section_times': section_times,
                        'total_time': sum(section_times.values()),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    requests.post(f"{self.server_url}/observation/update", json=data)
                    
                    # Reset times after reporting
                    self.marker_section_times[marker_id] = {1: 0, 2: 0, 3: 0}
                    
        except Exception as e:
            logging.error(f"Failed to report section times: {str(e)}")
