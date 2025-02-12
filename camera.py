import cv2
import numpy as np
import logging

class Camera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.test_pattern = None

        if not self.video.isOpened():
            logging.warning("Failed to open camera. Using test pattern instead.")
            self.video = None
            # Create a test pattern (black background with text)
            self.test_pattern = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(self.test_pattern, 
                       "Camera Not Available", 
                       (160, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       1, 
                       (255, 255, 255), 
                       2)

    def __del__(self):
        if self.video is not None:
            self.video.release()

    def get_frame(self, raw=False):
        if self.video is not None:
            success, frame = self.video.read()
            if not success:
                frame = self.test_pattern.copy() if self.test_pattern is not None else None
        else:
            frame = self.test_pattern.copy() if self.test_pattern is not None else None

        if frame is None:
            return None

        if raw:
            return frame

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()