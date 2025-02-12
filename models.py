from app import db
from datetime import datetime

class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aruco_id = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
