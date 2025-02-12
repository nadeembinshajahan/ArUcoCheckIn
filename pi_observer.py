import cv2
import time
import logging
import os
from artwork_tracker import ArtworkTracker

# Configuration
CAMERA_ID = os.environ.get('CAMERA_ID', 'pi_001')  # Unique ID for this Pi
ARTWORK_ID = os.environ.get('ARTWORK_ID', 'artwork_001')  # ID of artwork being observed
SERVER_URL = os.environ.get('SERVER_URL', 'http://your-aws-server.com')
REPORT_INTERVAL = 30  # Send updates every 30 seconds

def main():
    # Initialize camera
    cap = cv2.VideoCapture(0)  # Use Pi camera
    if not cap.isOpened():
        logging.error("Failed to open camera")
        return

    # Initialize tracker
    tracker = ArtworkTracker(
        camera_id=CAMERA_ID,
        artwork_id=ARTWORK_ID,
        server_url=SERVER_URL
    )

    last_report_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to read frame")
                continue

            # Process frame
            tracker.process_frame(frame)

            # Report data periodically
            current_time = time.time()
            if current_time - last_report_time >= REPORT_INTERVAL:
                tracker.report_section_times()
                last_report_time = current_time

            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        cap.release()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()
