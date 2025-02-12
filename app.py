import os
import logging
import time
from flask import Flask, render_template, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Initialize Flask app
def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_key_123")

    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aruco_checkin.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database with app
    db.init_app(app)

    from models import CheckIn
    from camera import Camera
    from aruco_processor import ArucoProcessor

    # Get video source from environment variable, default to camera index 0
    video_source = os.environ.get('VIDEO_SOURCE', 'attached_assets/check.MOV')
    camera = Camera(video_source)
    processor = ArucoProcessor()

    def gen_frames():
        while True:
            frame = camera.get_frame()
            if frame is not None:
                processed_frame, _ = processor.process_frame(frame)
                if processed_frame is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + processed_frame + b'\r\n')
            time.sleep(0.1)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen_frames(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/check_aruco')
    def check_aruco():
        try:
            frame = camera.get_frame(raw=True)
            if frame is not None:
                detected_id = processor.check_aruco_in_center(frame)
                if detected_id:
                    latest_checkin = CheckIn.get_latest_by_aruco(detected_id)
                    if latest_checkin:
                        if latest_checkin.status == 'checked_in':
                            return jsonify({
                                'detected': True,
                                'aruco_id': detected_id,
                                'status': 'can_checkout'
                            })
                        elif latest_checkin.can_check_in:
                            return jsonify({
                                'detected': True,
                                'aruco_id': detected_id,
                                'status': 'can_checkin'
                            })
                        else:
                            return jsonify({
                                'detected': True,
                                'aruco_id': detected_id,
                                'status': 'cooldown'
                            })
                    else:
                        return jsonify({
                            'detected': True,
                            'aruco_id': detected_id,
                            'status': 'can_checkin'
                        })
        except Exception as e:
            logging.error(f"Error checking ArUco: {str(e)}")
        return jsonify({'detected': False, 'aruco_id': None, 'status': None})

    @app.route('/checkin/<aruco_id>')
    def checkin(aruco_id):
        try:
            latest_checkin = CheckIn.get_latest_by_aruco(aruco_id)
            if latest_checkin and latest_checkin.status == 'checked_in':
                return jsonify({'success': False, 'error': 'Already checked in'})

            if latest_checkin and not latest_checkin.can_check_in:
                return jsonify({'success': False, 'error': 'Please wait before checking in again'})

            new_checkin = CheckIn(aruco_id=aruco_id)
            db.session.add(new_checkin)
            db.session.commit()
            return jsonify({'success': True, 'timestamp': new_checkin.check_in_time.isoformat()})
        except Exception as e:
            logging.error(f"Error in checkin: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/checkout/<aruco_id>')
    def checkout(aruco_id):
        try:
            checkin = CheckIn.get_latest_by_aruco(aruco_id)
            if not checkin or checkin.status != 'checked_in':
                return jsonify({'success': False, 'error': 'No active check-in found'})

            checkin.status = 'checked_out'
            checkin.check_out_time = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'timestamp': checkin.check_out_time.isoformat()})
        except Exception as e:
            logging.error(f"Error in checkout: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/get_history')
    def get_history():
        try:
            checkins = CheckIn.query.order_by(CheckIn.check_in_time.desc()).limit(10).all()
            history = [{
                'aruco_id': c.aruco_id,
                'timestamp': c.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': c.status,
                'checkout_time': c.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if c.check_out_time else None
            } for c in checkins]
            return jsonify(history)
        except Exception as e:
            logging.error(f"Error getting history: {str(e)}")
            return jsonify([])

    # Create database tables
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        logging.info("Database tables created successfully")

    return app

# Create the application instance
app = create_app()