from app import db
from datetime import datetime

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
        return time_diff.total_seconds() >= 10

    @classmethod
    def get_latest_by_aruco(cls, aruco_id):
        return cls.query.filter_by(aruco_id=aruco_id).order_by(cls.check_in_time.desc()).first()