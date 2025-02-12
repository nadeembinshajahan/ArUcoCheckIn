pip install flask flask-sqlalchemy opencv-python-headless numpy psycopg2-binary requests
```

## Configuration

The application can be configured using environment variables:

- `DATABASE_URL`: PostgreSQL database connection string
- `VIDEO_SOURCE`: Path to video file or camera index (default: 'attached_assets/check.MOV')
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (default: 'dev_key_123')

## Setup Instructions

1. Install Dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the database:
```bash
# The database URL should be in the environment variable DATABASE_URL
```

3. Start the Flask server:
```bash
python main.py
```

4. Access the application:
```
http://localhost:5000
```

## Usage Guide

### Camera Configuration

1. Navigate to `/camera_config` in your browser
2. Enter the camera URL/source
3. Use the drawing tools to define artwork regions:
   - Click on the video feed to create vertical region boundaries
   - Red lines indicate frame edges
   - Green lines indicate user-defined boundaries
   - Each region between lines represents an artwork area
4. Name your regions using the table below the video feed
5. Save your configuration

### Analytics Dashboard

1. Navigate to `/dashboard` to view:
   - Total visitor count
   - Active cameras
   - Average observation time
   - Most viewed artwork
   - Time spent per section
   - Visitor flow throughout the day
   - Recent observations table

### ArUco Tracking

The system uses 6x6 ArUco markers (DICT_6X6_50) for visitor tracking:
- Each visitor receives a unique ArUco marker
- Markers are detected in real-time by cameras
- Section times are calculated based on marker position
- Data is sent to the central server for analytics

## Project Structure
```
.
├── app.py              # Main Flask application
├── artwork_tracker.py  # ArUco tracking and observation logic
├── models.py          # Database models
├── static/            
│   ├── css/          # Stylesheets
│   └── js/           # JavaScript files
│       ├── dashboard.js    # Dashboard visualization
│       └── camera_config.js # Camera configuration interface
└── templates/         # HTML templates
    ├── dashboard.html     # Analytics dashboard
    └── camera_config.html # Camera setup interface
```

## API Documentation

### Observation Endpoints

- `POST /observation/start`
  - Start tracking a new visitor
  - Body: `{camera_id, artwork_id, aruco_id, timestamp}`

- `POST /observation/update`
  - Update section times for a visitor
  - Body: `{camera_id, artwork_id, aruco_id, section_times, total_time, timestamp}`

### Camera Management

- `POST /api/camera/register`
  - Register a new camera in the system
  - Body: `{camera_id, location, artwork_ids}`

- `POST /api/connect_camera`
  - Connect to a camera feed
  - Body: `{camera_url}`

- `POST /api/save_regions`
  - Save artwork regions for a camera
  - Body: `{camera_url, regions}`

## Development

For development purposes:
- Debug mode is enabled
- Flask runs on port 5000
- Logging is set to DEBUG level
- Database tables are automatically created on startup

## Testing

Run the integration tests:
```bash
python test_server_integration.py
```

Run the tracking tests:
```bash
python test_tracking.py