from app import db
from datetime import datetime
import json

class ObservationEvent(db.Model):
    __tablename__ = 'observation_events'

    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), nullable=False)
    artwork_id = db.Column(db.String(50), nullable=False)
    aruco_id = db.Column(db.Integer, nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # 'start' or 'update'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class CheckIn(db.Model):
    __tablename__ = 'check_in'

    id = db.Column(db.Integer, primary_key=True)
    aruco_id = db.Column(db.String(50), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='checked_in')  # 'checked_in' or 'checked_out'

    @property
    def can_check_in(self):
        """Check if the ArUco code can check in again"""
        if not self.check_out_time:
            return False
        time_diff = datetime.utcnow() - self.check_out_time
        return time_diff.total_seconds() >= 10  # 10-second cooldown

    @classmethod
    def get_latest_by_aruco(cls, aruco_id):
        return cls.query.filter_by(aruco_id=aruco_id).order_by(cls.check_in_time.desc()).first()

class ArtworkObservation(db.Model):
    __tablename__ = 'artwork_observations'

    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), nullable=False)
    artwork_id = db.Column(db.String(50), nullable=False)
    aruco_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    section_1_time = db.Column(db.Float, default=0.0)
    section_2_time = db.Column(db.Float, default=0.0)
    section_3_time = db.Column(db.Float, default=0.0)
    total_time = db.Column(db.Float, default=0.0)

    @property
    def section_times(self):
        return {
            1: self.section_1_time,
            2: self.section_2_time,
            3: self.section_3_time
        }

class Camera(db.Model):
    __tablename__ = 'cameras'

    camera_id = db.Column(db.String(50), primary_key=True)
    location = db.Column(db.String(100))
    artwork_ids = db.Column(db.String(500))  # JSON string of artwork IDs being monitored
    last_active = db.Column(db.DateTime)

    @property
    def monitored_artworks(self):
        return json.loads(self.artwork_ids)

    @monitored_artworks.setter
    def monitored_artworks(self, artwork_list):
        self.artwork_ids = json.dumps(artwork_list)

class Artwork(db.Model):
    __tablename__ = 'artworks'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))  # Location in gallery