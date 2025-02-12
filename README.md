pip install flask flask-sqlalchemy opencv-python-headless numpy
```

## Configuration

The application can be configured using environment variables:

- `VIDEO_SOURCE`: Path to video file or camera index (default: 'attached_assets/check.MOV')
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (default: 'dev_key_123')

## Running the Application

1. Start the Flask server:
```bash
python main.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Main Interface Features:
   - Live video feed showing ArUco marker detection
   - Center detection zone (red when empty, green when marker detected)
   - Dynamic check-in/checkout button
   - Real-time history panel

2. Check-in Process:
   - Position an ArUco marker in the center zone
   - Wait for the zone to turn green (marker detected)
   - Click the "Check In" button when enabled
   - The system records the check-in time

3. Checkout Process:
   - If a checked-in marker is detected again, a "Check Out" button appears
   - Click to record the checkout time
   - After checkout, there's a 10-second cooldown before the same code can check in again

4. History Panel:
   - Shows the most recent check-ins and checkouts
   - Displays ArUco code IDs, check-in times, and checkout times
   - Updates in real-time as actions occur

## ArUco Markers

This system uses 6x6 ArUco markers (DICT_6X6_50). You can generate these markers using:
- OpenCV's aruco.Dictionary_create() function
- Online ArUco marker generators
- Pre-generated marker sets (available in OpenCV)

## Project Structure
```
.
├── app.py              # Main Flask application
├── camera.py           # Camera/video handling
├── aruco_processor.py  # ArUco detection logic
├── models.py           # Database models
├── static/            
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript files
└── templates/          # HTML templates