from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Registered user account."""
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False, index=True)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    scans = db.relationship('ScanHistory', backref='user', lazy='dynamic',
                            cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class ScanHistory(db.Model):
    """Record of every scan performed (URL or Email)."""
    __tablename__ = 'scan_history'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # null = guest
    scan_type    = db.Column(db.String(10), nullable=False)   # 'url' | 'email'
    input_value  = db.Column(db.Text, nullable=False)         # the URL or email body
    label        = db.Column(db.String(20), nullable=False)   # 'Malicious'/'Safe'/'Phishing'/'Legitimate'
    risk_level   = db.Column(db.String(10), nullable=False)   # 'HIGH'/'MEDIUM'/'LOW'
    confidence   = db.Column(db.Float, nullable=False)        # 0–100 %
    scanned_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self) -> dict:
        return {
            'id':          self.id,
            'scan_type':   self.scan_type,
            'input_value': self.input_value,
            'label':       self.label,
            'risk_level':  self.risk_level,
            'confidence':  self.confidence,
            'scanned_at':  self.scanned_at.strftime('%Y-%m-%d %H:%M:%S') if self.scanned_at else None,
            'username':    self.user.username if self.user else 'Guest',
        }

    def __repr__(self):
        return f'<ScanHistory {self.scan_type} {self.label}>'
