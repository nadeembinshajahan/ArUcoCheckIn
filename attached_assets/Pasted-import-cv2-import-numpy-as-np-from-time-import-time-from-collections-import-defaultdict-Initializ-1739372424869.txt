import cv2
import numpy as np
from time import time
from collections import defaultdict

# Initialize video capture
cap = cv2.VideoCapture("test4.MOV")
# cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

# Get the width and height of the frames
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (frame_width, frame_height))

# Setup ArUco detector with the correct modern syntax
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

# Initialize time trackers for each marker ID and section
marker_section_times = defaultdict(lambda: {1: 0, 2: 0, 3: 0})
marker_last_times = {}
marker_current_sections = {}

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame")
        break
    
    height, width = frame.shape[:2]
    
    # Draw vertical lines to divide frame into thirds
    third_width = width // 3
    cv2.line(frame, (third_width, 0), (third_width, height), (0, 255, 0), 2)
    cv2.line(frame, (2 * third_width, 0), (2 * third_width, height), (0, 255, 0), 2)
    
    # Detect ArUco markers
    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(frame)
    
    current_time = time()
    
    if markerIds is not None:

        cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
        

        for idx, corners in enumerate(markerCorners):
            marker_id = int(markerIds[idx])
            
            marker_center = np.mean(corners[0], axis=0)
            center_x = int(marker_center[0])
            
            # Determine which section the marker is in
            if center_x < third_width:
                new_section = 1
            elif center_x < 2 * third_width:
                new_section = 2
            else:
                new_section = 3
            
            # Initialize tracking for new markers
            if marker_id not in marker_last_times:
                marker_last_times[marker_id] = current_time
                marker_current_sections[marker_id] = new_section
                continue
            
            # Update time for the current section
            if marker_current_sections[marker_id] == new_section:
                marker_section_times[marker_id][new_section] += current_time - marker_last_times[marker_id]
            
            marker_current_sections[marker_id] = new_section
            marker_last_times[marker_id] = current_time
    
    out.write(frame)
    
    # Display the frame
    # cv2.imshow('Frame', frame)
    
    # # Break the loop if 'q' is pressed
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

print("\nFinal times for each ArUco marker:")
for marker_id, section_times in marker_section_times.items():
    print(f"\nMarker ID {marker_id}:")
    total_time = sum(section_times.values())
    for section, time_spent in section_times.items():
        percentage = (time_spent / total_time * 100) if total_time > 0 else 0
        print(f"Section {section}: {time_spent:.2f} seconds ({percentage:.1f}%)")

cap.release()
out.release()
cv2.destroyAllWindows()