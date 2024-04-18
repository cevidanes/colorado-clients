from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from utilities.extensions import db



class CPUser(UserMixin, db.Model):
    __tablename__ = 'cp_users'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    token = db.Column(db.String(255))
    pr_position_id = db.Column(db.String(255))
    
    def set_password(self, password):
        """Create hashed password."""
        self.token = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        print(password)
        return check_password_hash(self.token, password)

class CPPosition(db.Model):
    __tablename__ = 'cp_positions'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    name = db.Column(db.String(255), nullable=False)
    enabled = db.Column(db.String(255), nullable=False)

class CPUserPosition(db.Model):
    __tablename__ = 'cp_user_position'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('cp_users.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('cp_positions.id'), nullable=False)
