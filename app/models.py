from datetime import datetime

from app import db

# Intermediate table to link users and completed mazes
user_completed_dungeons = db.Table(
    "user_completed_maze",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("maze_id", db.Integer, db.ForeignKey("maze_bd.id"), primary_key=True),
    db.Column("completed_at", db.DateTime, default=datetime.utcnow),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    completed_dungeons = db.Column(db.Integer, nullable=False, default=0)
    avatar = db.Column(db.String(200), nullable=True)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    points = db.Column(db.Integer, nullable=False, default=0)
    completed_dungeons = db.relationship(
        "MazeBd",
        secondary=user_completed_dungeons,
        lazy="subquery",
        backref=db.backref("completers", lazy=True),
    )

    def __repr__(self):
        return f"<User {self.username}>"


class MazeBd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grid = db.Column(db.JSON, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # FK to User
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )  # Creation date
    maze_size = db.Column(db.Integer, nullable=False)

    # Relationship with the User model
    user = db.relationship("User", backref="mazes", lazy=True)

    def __repr__(self):
        return f"<MazeBd {self.grid}>"
