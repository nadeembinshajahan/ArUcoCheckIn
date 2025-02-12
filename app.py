import os
import logging
import time
from flask import Flask, render_template, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize database
db = SQLAlchemy()

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
        return Response(gen_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/check_aruco')
    def check_aruco():
        try:
            frame = camera.get_frame(raw=True)
            if frame is not None:
                detected_id = processor.check_aruco_in_center(frame)
                if detected_id:
                    logging.debug(f"Detected ArUco ID: {detected_id}")
                    # Check if there's an active check-in for this ArUco
                    last_checkin = CheckIn.query.filter_by(
                        aruco_id=detected_id,
                        is_checked_out=False
                    ).first()

                    if last_checkin:
                        # If checked in more than 10 seconds ago, allow check-out
                        if datetime.utcnow() - last_checkin.check_in_time > timedelta(seconds=10):
                            return jsonify({
                                'detected': True,
                                'aruco_id': detected_id,
                                'status': 'can_checkout',
                                'checkin_id': last_checkin.id
                            })
                        return jsonify({
                            'detected': True,
                            'aruco_id': detected_id,
                            'status': 'already_checked_in'
                        })
                    return jsonify({
                        'detected': True,
                        'aruco_id': detected_id,
                        'status': 'can_checkin'
                    })
                logging.debug("No ArUco detected in center")
            return jsonify({'detected': False, 'aruco_id': None, 'status': None})
        except Exception as e:
            logging.error(f"Error checking ArUco: {str(e)}")
            return jsonify({'detected': False, 'aruco_id': None, 'status': None})

    @app.route('/checkin/<aruco_id>')
    def checkin(aruco_id):
        try:
            # Check if already checked in
            existing_checkin = CheckIn.query.filter_by(
                aruco_id=aruco_id,
                is_checked_out=False
            ).first()

            if existing_checkin:
                return jsonify({
                    'success': False,
                    'message': 'Already checked in'
                })

            new_checkin = CheckIn(aruco_id=aruco_id)
            db.session.add(new_checkin)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Checked in successfully',
                'timestamp': new_checkin.check_in_time.isoformat()
            })
        except Exception as e:
            logging.error(f"Error in checkin: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error during check-in: {str(e)}'
            })

    @app.route('/checkout/<int:checkin_id>')
    def checkout(checkin_id):
        try:
            checkin = CheckIn.query.get(checkin_id)
            if checkin and not checkin.is_checked_out:
                checkin.check_out_time = datetime.utcnow()
                checkin.is_checked_out = True
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': 'Checked out successfully'
                })
            return jsonify({
                'success': False,
                'message': 'Invalid check-in or already checked out'
            })
        except Exception as e:
            logging.error(f"Error in checkout: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error during check-out: {str(e)}'
            })

    @app.route('/get_history')
    def get_history():
        try:
            checkins = CheckIn.query.order_by(CheckIn.check_in_time.desc()).limit(10).all()
            history = [checkin.to_dict() for checkin in checkins]
            return jsonify(history)
        except Exception as e:
            logging.error(f"Error getting history: {str(e)}")
            return jsonify([])

    with app.app_context():
        db.create_all()

    return app

# Create the application instance
app = create_app()