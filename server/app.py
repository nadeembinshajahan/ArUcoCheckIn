import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Models
class ArtworkObservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), nullable=False)
    artwork_id = db.Column(db.String(50), nullable=False)
    aruco_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    section_1_time = db.Column(db.Float, default=0)
    section_2_time = db.Column(db.Float, default=0)
    section_3_time = db.Column(db.Float, default=0)
    total_time = db.Column(db.Float, default=0)

class ObservationEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), nullable=False)
    artwork_id = db.Column(db.String(50), nullable=False)
    aruco_id = db.Column(db.Integer, nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # 'start' or 'update'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/observation/start', methods=['POST'])
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

@app.route('/observation/update', methods=['POST'])
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

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
