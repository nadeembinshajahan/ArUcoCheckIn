import os
import logging
import time
from flask import Flask, render_template, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy.orm import DeclarativeBase
import json

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

    # Configure PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Initialize database with app
    db.init_app(app)

    from models import CheckIn, Camera as DBCamera, ArtworkObservation, ObservationEvent # Added import for ObservationEvent
    from camera import Camera as VideoCamera
    from aruco_processor import ArucoProcessor

    # Get video source from environment variable, default to camera index 0
    video_source = os.environ.get('VIDEO_SOURCE', 'attached_assets/check.MOV')
    camera = VideoCamera(video_source)
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

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

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


    @app.route('/api/camera/register', methods=['POST'])
    def register_camera():
        """Register a new camera/RPI in the system"""
        try:
            data = request.json
            camera = DBCamera(
                camera_id=data['camera_id'],
                location=data.get('location', 'Unknown'),
                artwork_ids=json.dumps(data['artwork_ids'])
            )
            camera.last_active = datetime.utcnow()
            db.session.merge(camera)  # Update if exists, insert if new
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            logging.error(f"Error registering camera: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/observation/start', methods=['POST']) # Added route for observation start
    def start_observation():
        try:
            data = request.json
            event = ObservationEvent(
                camera_id=data['camera_id'],
                artwork_id=data['artwork_id'],
                aruco_id=data['aruco_id'],
                event_type='start',
                timestamp=datetime.fromisoformat(data['timestamp'])
            )
            db.session.add(event)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/observation/update', methods=['POST']) # Modified route for observation update
    def update_observation():
        try:
            data = request.json
            observation = ArtworkObservation(
                camera_id=data['camera_id'],
                artwork_id=data['artwork_id'],
                aruco_id=data['aruco_id'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                section_1_time=data['section_times'][1],
                section_2_time=data['section_times'][2],
                section_3_time=data['section_times'][3],
                total_time=data['total_time']
            )
            db.session.add(observation)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/analytics')
    def get_analytics():
        try:
            # Get active cameras (active in last 5 minutes)
            active_time = datetime.utcnow() - timedelta(minutes=5)
            active_cameras = DBCamera.query.filter(DBCamera.last_active >= active_time).count()

            # Get total unique visitors today
            today = datetime.utcnow().date()
            total_visitors = db.session.query(db.func.count(db.distinct(ArtworkObservation.aruco_id)))\
                .filter(db.func.date(ArtworkObservation.timestamp) == today).scalar()

            # Get average time spent per artwork (in minutes)
            avg_time = db.session.query(db.func.avg(ArtworkObservation.total_time))\
                .filter(db.func.date(ArtworkObservation.timestamp) == today)\
                .scalar() or 0

            # Get most popular artwork
            popular_artwork = db.session.query(
                ArtworkObservation.artwork_id,
                db.func.count(ArtworkObservation.id).label('visit_count')
            ).group_by(ArtworkObservation.artwork_id)\
            .order_by(db.text('visit_count DESC')).first()

            # Get section time distribution
            section_times = db.session.query(
                db.func.avg(ArtworkObservation.section_1_time).label('section_1'),
                db.func.avg(ArtworkObservation.section_2_time).label('section_2'),
                db.func.avg(ArtworkObservation.section_3_time).label('section_3')
            ).filter(db.func.date(ArtworkObservation.timestamp) == today).first()

            # Get recent observations
            recent = ArtworkObservation.query\
                .order_by(ArtworkObservation.timestamp.desc())\
                .limit(10)\
                .all()

            analytics = {
                'total_visitors': total_visitors or 0,
                'active_cameras': active_cameras or 0,
                'avg_time': round(float(avg_time) / 60, 1),  # Convert to minutes
                'popular_artwork': popular_artwork[0] if popular_artwork else "N/A",
                'section_times': {
                    'section_1': round(float(section_times[0] or 0) / 60, 1),
                    'section_2': round(float(section_times[1] or 0) / 60, 1),
                    'section_3': round(float(section_times[2] or 0) / 60, 1)
                },
                'recent_observations': [{
                    'aruco_id': str(obs.aruco_id),
                    'artwork_id': obs.artwork_id,
                    'time_spent': f"{float(obs.total_time)/60:.1f} min",
                    'sections': ', '.join(str(i) for i, t in obs.section_times.items() if t > 0),
                    'timestamp': obs.timestamp.strftime('%Y-%m-%d %H:%M')
                } for obs in recent] if recent else []
            }
            return jsonify(analytics)
        except Exception as e:
            logging.error(f"Error fetching analytics: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Create database tables
    with app.app_context():
        db.create_all()
        logging.info("Database tables created successfully")

    return app

# Create the application instance
app = create_app()