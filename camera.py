import cv2
import numpy as np
import logging
import os
from threading import Lock

class Camera:
    def __init__(self, video_source=0):
        """
        Initialize camera with video source.
        Args:
            video_source: Can be:
                - Integer for webcam index (e.g., 0 for default webcam)
                - String for video file path
                Examples:
                - camera = Camera(0)  # Use default webcam
                - camera = Camera(1)  # Use second webcam
                - camera = Camera("videos/sample.mp4")  # Use video file
        """
        self.video = None
        self.test_pattern = None
        self.video_source = video_source
        self.lock = Lock()  # Add thread synchronization

        try:
            if isinstance(video_source, str) and os.path.isfile(video_source):
                self.video = cv2.VideoCapture(video_source)
                logging.info(f"Opened video file: {video_source}")
            else:
                self.video = cv2.VideoCapture(int(video_source))
                logging.info(f"Opened camera device: {video_source}")

            if not self.video.isOpened():
                raise ValueError("Failed to open video source")

        except Exception as e:
            logging.warning(f"Failed to open video source: {str(e)}. Using test pattern instead.")
            self.video = None
            # Create a test pattern (black background with text)
            self.test_pattern = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(self.test_pattern, 
                       "Camera/Video Not Available", 
                       (160, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       1, 
                       (255, 255, 255), 
                       2)

    def __del__(self):
        self.release()

    def release(self):
        """Safely release video resources"""
        if self.video is not None:
            self.video.release()
            self.video = None

    def get_frame(self, raw=False):
        """
        Get the next frame from the video source.
        Args:
            raw: If True, returns the raw frame instead of JPEG bytes
        Returns:
            Frame data (as raw numpy array or JPEG bytes) or None if no frame is available

        For video files:
        - Automatically loops back to the start when reaching the end
        - Falls back to test pattern if video file becomes unavailable

        For webcams:
        - Continuously captures frames
        - Falls back to test pattern if camera becomes unavailable
        """
        frame = None
        with self.lock:  # Ensure thread-safe access to video device
            try:
                if self.video is not None:
                    success, frame = self.video.read()
                    if not success:
                        # For video files, loop back to start
                        if isinstance(self.video_source, str):
                            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            success, frame = self.video.read()
                            if not success:
                                frame = self.test_pattern.copy() if self.test_pattern is not None else None
                        else:
                            frame = self.test_pattern.copy() if self.test_pattern is not None else None
                else:
                    frame = self.test_pattern.copy() if self.test_pattern is not None else None

            except Exception as e:
                logging.error(f"Error reading frame: {str(e)}")
                frame = self.test_pattern.copy() if self.test_pattern is not None else None

        if frame is None:
            return None

        if raw:
            return frame

        try:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes() if ret else None
        except Exception as e:
            logging.error(f"Error encoding frame: {str(e)}")
            return None