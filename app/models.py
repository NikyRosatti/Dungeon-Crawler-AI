"""
Model definitions for User and MazeBd in the application.

This module contains the models that define the database structure for the User and MazeBd classes.
It also defines the many-to-many relationship between users and completed mazes.
"""

from datetime import datetime
from app import db

# Intermediate table to relate users and completed mazes
user_completed_dungeons = db.Table(
    "user_completed_maze",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("maze_id", db.Integer, db.ForeignKey("maze_bd.id"), primary_key=True),
    db.Column("completed_at", db.DateTime, default=datetime.utcnow),
)


class User(db.Model):
    """
    User class representing the user in the system.

    This class contains the attributes related to the user, including username, email, password,
    language, and completed dungeons. It also defines the relationship with completed mazes.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    language = db.Column(db.String(2), nullable=True)
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
        """
        Return a string representation of the User object.

        This method returns a string representing the User instance, displaying the username.
        """
        return f"<User {self.username}>"

    def get_completed_dungeons(self):
        """
        Returns the count of completed dungeons for the user.

        This method returns the number of mazes the user has completed.
        """
        return len(self.completed_dungeons)


class MazeBd(db.Model):
    """
    MazeBd class representing a maze in the database.

    This class defines the attributes of a maze, including its grid, the user who created it,
    and the size of the maze. It also defines the relationship with the User who created the maze.
    """

    id = db.Column(db.Integer, primary_key=True)
    grid = db.Column(db.JSON, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # FK to User
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Creation date
    maze_size = db.Column(db.Integer, nullable=False)

    # Relationship with the User model
    user = db.relationship("User", backref="mazes", lazy=True)

    def __repr__(self):
        """
        Return a string representation of the MazeBd object.

        This method returns a string representing the MazeBd instance, displaying its grid.
        """
        return f"<MazeBd {self.grid}>"

