import os
import logging
from flask import Flask, request, jsonify, render_template
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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/analytics')
def get_analytics():
    try:
        # For now, return mock data
        # This will be replaced with actual database queries
        analytics = {
            'total_visitors': 1234,
            'active_now': 42,
            'avg_time': 5.2,
            'popular_section': 'Section 2',
            'recent_observations': [
                {
                    'aruco_id': '1234',
                    'artwork_id': 'Artwork A',
                    'time_spent': '3.5 min',
                    'sections': '1, 2, 3',
                    'timestamp': '2024-02-12 14:30'
                },
                {
                    'aruco_id': '5678',
                    'artwork_id': 'Artwork B',
                    'time_spent': '2.1 min',
                    'sections': '2, 3',
                    'timestamp': '2024-02-12 14:25'
                }
            ]
        }
        return jsonify(analytics)
    except Exception as e:
        logging.error(f"Error fetching analytics: {str(e)}")
        return jsonify({'error': 'Failed to fetch analytics data'}), 500

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)