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
        box_size = min(width, height) // 1.5  # Make box bigger - using 2/3 of min dimension
        center_x = width // 2
        center_y = height // 2

        # Detect ArUco markers
        corners, ids, _ = self.detector.detectMarkers(frame)

        # Check if marker is in center box
        aruco_detected = False
        detected_id = None
        if ids is not None and len(ids) > 0:
            for i, corner in enumerate(corners):
                marker_center = np.mean(corner[0], axis=0)
                if (abs(marker_center[0] - center_x) < box_size//2 and
                    abs(marker_center[1] - center_y) < box_size//2):
                    aruco_detected = True
                    detected_id = str(ids[i][0])  # Convert ID to string
                    break

        # Draw box with color based on detection
        color = (0, 255, 0) if aruco_detected else (0, 0, 255)  # Green if detected, red if not
        cv2.rectangle(frame,
                     (center_x - box_size//2, center_y - box_size//2),
                     (center_x + box_size//2, center_y + box_size//2),
                     color, 2)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), detected_id

    def check_aruco_in_center(self, frame):
        height, width = frame.shape[:2]
        box_size = min(width, height) // 1.5  # Match the box size from process_frame
        center_x = width // 2
        center_y = height // 2

        # Detect ArUco markers
        corners, ids, _ = self.detector.detectMarkers(frame)

        if ids is not None and len(ids) > 0:
            for i, corner in enumerate(corners):
                marker_center = np.mean(corner[0], axis=0)
                if (abs(marker_center[0] - center_x) < box_size//2 and
                    abs(marker_center[1] - center_y) < box_size//2):
                    return str(ids[i][0])  # Return actual ArUco ID as string
        return None