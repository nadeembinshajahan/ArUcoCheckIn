from app import db
from datetime import datetime

class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aruco_id = db.Column(db.String(50), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    is_checked_out = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'aruco_id': self.aruco_id,
            'check_in_time': self.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
            'check_out_time': self.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if self.check_out_time else None,
            'is_checked_out': self.is_checked_out
        }