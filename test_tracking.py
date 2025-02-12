import cv2
import numpy as np
import logging
from artwork_tracker import ArtworkTracker

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Initialize tracker with test configuration
    tracker = ArtworkTracker(
        camera_id="test_camera",
        artwork_id="test_artwork",
        server_url="http://localhost:5000"  # Not used in test mode
    )
    
    # Open test video file
    cap = cv2.VideoCapture("attached_assets/check.MOV")
    if not cap.isOpened():
        logging.error("Failed to open video file")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.info("End of video file")
                break

            # Process frame
            height, width = frame.shape[:2]
            third_width = width // 3

            # Draw section lines
            cv2.line(frame, (third_width, 0), (third_width, height), (0, 255, 0), 2)
            cv2.line(frame, (2 * third_width, 0), (2 * third_width, height), (0, 255, 0), 2)

            # Process frame with tracker
            tracker.process_frame(frame)

            # Display section times
            y_offset = 30
            for marker_id, times in tracker.marker_section_times.items():
                text = f"ArUco {marker_id} - S1: {times[1]:.1f}s, S2: {times[2]:.1f}s, S3: {times[3]:.1f}s"
                cv2.putText(frame, text, (10, y_offset), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30

            # Display the frame
            cv2.imshow('Artwork Tracking Test', frame)

            # Break on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        logging.error(f"Error during tracking: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
