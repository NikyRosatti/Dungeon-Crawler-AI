from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    completed_dungeons = db.Column(db.Integer, nullable=False, default=0)
    avatar = db.Column(db.String(200), nullable=True)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"


class MazeBd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grid = db.Column(db.JSON, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # FK a User
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )  # Fecha de creación
    maze_size = db.Column(db.Integer, nullable=False)

    # Relación con el modelo User
    user = db.relationship("User", backref="mazes", lazy=True)

    def __repr__(self):
        return f"<MazeBd {self.grid}>"
