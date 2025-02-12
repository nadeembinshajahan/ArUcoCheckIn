# ArUco Code Check-in System

A web-based ArUco marker detection and check-in system built with Flask and OpenCV. This application processes video input to detect ArUco markers and maintains a history of check-ins.

## Features

- Real-time ArUco marker detection
- Video feed processing with center detection zone
- Check-in history tracking
- SQLite database for persistent storage
- Visual feedback for marker detection
- Responsive web interface

## Requirements

- Python 3.8+
- OpenCV with ArUco support
- Flask
- SQLite

## Installation

1. Clone the repository
2. Install the required packages:
```bash
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

1. The main interface shows:
   - Video feed with ArUco detection
   - Center detection zone (red when no marker, green when marker detected)
   - Check-in button
   - History panel

2. To check in:
   - Position an ArUco marker in the center zone
   - Wait for the zone to turn green
   - Click the "Check In" button
   - The check-in will be recorded in the history panel

## ArUco Markers

This system uses 6x6 ArUco markers (DICT_6X6_50). You can generate these markers using OpenCV or various online tools.

## Development

The project structure:
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
```

## Database

The application uses SQLite for data storage. The database file (`aruco_checkin.db`) is automatically created in the instance folder when the application first runs.

## Troubleshooting

1. Video feed not showing:
   - Check if the video source exists
   - Verify OpenCV installation
   - Check console for error messages

2. Database issues:
   - Delete the database file and restart to reset
   - Check file permissions in the instance directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
