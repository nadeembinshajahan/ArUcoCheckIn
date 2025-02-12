import os
import logging
from flask import Flask, render_template, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_key_123")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checkins.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

from models import CheckIn
from camera import Camera
from aruco_processor import ArucoProcessor

camera = Camera()
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
    frame = camera.get_frame(raw=True)
    if frame is not None:
        is_detected = processor.check_aruco_in_center(frame)
        return jsonify({'detected': is_detected})
    return jsonify({'detected': False})

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
