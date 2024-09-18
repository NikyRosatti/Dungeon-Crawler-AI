from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    completed_dungeons = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class MazeBd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grid = db.Column(db.JSON, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # FK a User
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Fecha de creación

    # Relación con el modelo User
    user = db.relationship('User', backref='mazes', lazy=True)
    
    def __repr__(self):
        return f'<MazeBd {self.grid}>'