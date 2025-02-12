import requests
import time
import random
from datetime import datetime, timedelta

SERVER_URL = "http://localhost:5000"
TEST_CAMERAS = [
    {"camera_id": "pi_001", "artwork_ids": ["artwork_001", "artwork_002", "artwork_003"]},
    {"camera_id": "pi_002", "artwork_ids": ["artwork_004", "artwork_005", "artwork_006"]},
    {"camera_id": "pi_003", "artwork_ids": ["artwork_007", "artwork_008", "artwork_009"]}
]

def register_cameras():
    """Register test cameras with the server"""
    for camera in TEST_CAMERAS:
        response = requests.post(
            f"{SERVER_URL}/api/camera/register",
            json={
                "camera_id": camera["camera_id"],
                "location": f"Gallery Section {camera['camera_id'][-1]}",
                "artwork_ids": camera["artwork_ids"]
            }
        )
        if response.status_code == 200:
            print(f"Registered camera {camera['camera_id']}")
        else:
            print(f"Failed to register camera {camera['camera_id']}")

def simulate_observations():
    """Simulate artwork observations from multiple cameras"""
    while True:
        try:
            # For each camera, simulate some observations
            for camera in TEST_CAMERAS:
                # Simulate 1-3 visitors per camera
                for _ in range(random.randint(1, 3)):
                    aruco_id = random.randint(1000, 9999)
                    artwork_id = random.choice(camera["artwork_ids"])
                    
                    # Generate random section times
                    section_times = {
                        1: random.uniform(0, 120),  # 0-2 minutes
                        2: random.uniform(0, 180),  # 0-3 minutes
                        3: random.uniform(0, 150)   # 0-2.5 minutes
                    }
                    
                    # Calculate timestamps
                    start_time = datetime.utcnow() - timedelta(minutes=5)
                    end_time = datetime.utcnow()
                    
                    data = {
                        "camera_id": camera["camera_id"],
                        "artwork_id": artwork_id,
                        "aruco_id": aruco_id,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "section_times": section_times
                    }
                    
                    response = requests.post(f"{SERVER_URL}/api/observation/update", json=data)
                    if response.status_code == 200:
                        print(f"Sent observation for camera {camera['camera_id']}, artwork {artwork_id}")
                    else:
                        print(f"Failed to send observation: {response.text}")
            
            # Wait before next batch of observations
            time.sleep(10)  # Send new observations every 10 seconds
            
        except Exception as e:
            print(f"Error sending observations: {str(e)}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    print("Starting test server integration...")
    register_cameras()
    simulate_observations()
