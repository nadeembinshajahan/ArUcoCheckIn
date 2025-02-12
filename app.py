import os
import logging
import time
from flask import Flask, render_template, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize database
db = SQLAlchemy()

# Initialize Flask app
def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_key_123")

    # Configure PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Initialize database with app
    db.init_app(app)

    from models import CheckIn
    from camera import Camera
    from aruco_processor import ArucoProcessor

    # Get video source from environment variable, default to camera index 0
    video_source = os.environ.get('VIDEO_SOURCE', 'attached_assets/check.MOV')
    camera = Camera(video_source)
    processor = ArucoProcessor()

    @app.route('/')
    def index():
        return render_template('index.html')

    def gen_frames():
        while True:
            frame = camera.get_frame()
            if frame is not None:
                processed_frame, aruco_detected = processor.process_frame(frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + processed_frame + b'\r\n')

    @app.route('/video_feed')
    def video_feed():
        def generate():
            while True:
                try:
                    frame = camera.get_frame()
                    if frame is not None:
                        processed_frame, aruco_detected = processor.process_frame(frame)
                        if processed_frame is not None:
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + processed_frame + b'\r\n')
                except Exception as e:
                    logging.error(f"Error in video feed: {str(e)}")
                    # Small delay to prevent rapid reconnection attempts
                    time.sleep(0.1)

        return Response(generate(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/check_aruco')
    def check_aruco():
        try:
            frame = camera.get_frame(raw=True)
            if frame is not None:
                detected_id = processor.check_aruco_in_center(frame)
                return jsonify({'detected': detected_id is not None, 'aruco_id': detected_id})
        except Exception as e:
            logging.error(f"Error checking ArUco: {str(e)}")
        return jsonify({'detected': False, 'aruco_id': None})

    @app.route('/checkin/<aruco_id>')
    def checkin(aruco_id):
        new_checkin = CheckIn(aruco_id=aruco_id)
        db.session.add(new_checkin)
        db.session.commit()
        return jsonify({'success': True, 'timestamp': new_checkin.timestamp.isoformat()})

    @app.route('/get_history')
    def get_history():
        checkins = CheckIn.query.order_by(CheckIn.timestamp.desc()).limit(10).all()
        history = [{
            'aruco_id': c.aruco_id,
            'timestamp': c.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for c in checkins]
        return jsonify(history)

    with app.app_context():
        db.create_all()

    return app

# Create the application instance
app = create_app()