from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    completed_dungeons = db.Column(db.Integer, nullable=False, default=0)
    avatar = db.Column(db.String(200), nullable=True)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class MazeBd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grid = db.Column(db.JSON, nullable = False)
    entradaX = db.Column( db.Integer, nullable=False)
    entradaY = db.Column(db.Integer, nullable=False)
    salidaX = db.Column(db.Integer, nullable=False)
    salidaY = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<MazeBd {self.grid}>'