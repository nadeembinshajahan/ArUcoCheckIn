import cv2
import numpy as np

class ArucoProcessor:
    def __init__(self):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

    def process_frame(self, frame):
        # Convert bytes to numpy array
        if isinstance(frame, bytes):
            np_arr = np.frombuffer(frame, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Draw center box
        height, width = frame.shape[:2]
        box_size = min(width, height) // 3
        center_x = width // 2
        center_y = height // 2

        # Draw green box in center
        cv2.rectangle(frame,
                     (center_x - box_size//2, center_y - box_size//2),
                     (center_x + box_size//2, center_y + box_size//2),
                     (0, 255, 0), 2)

        # Detect ArUco markers
        corners, ids, _ = self.detector.detectMarkers(frame)

        aruco_detected = False
        if len(corners) > 0:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            aruco_detected = True

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), aruco_detected

    def check_aruco_in_center(self, frame):
        height, width = frame.shape[:2]
        box_size = min(width, height) // 3
        center_x = width // 2
        center_y = height // 2

        # Detect ArUco markers
        corners, ids, _ = self.detector.detectMarkers(frame)

        if len(corners) > 0:
            for corner in corners:
                # Calculate marker center
                marker_center = np.mean(corner[0], axis=0)

                # Check if marker is in center box
                if (abs(marker_center[0] - center_x) < box_size//2 and
                    abs(marker_center[1] - center_y) < box_size//2):
                    return True

        return False