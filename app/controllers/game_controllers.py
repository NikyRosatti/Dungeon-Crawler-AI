"""
This module contains auxiliary functions to handle the maze logic.
It includes functions to validate the start and exit points, as well as to save
the maze to the database and respond with the appropriate redirection URL.
"""

import json

from flask import jsonify, session, url_for
from app.models import MazeBd, db


def invalid_points_response():
    """
    Returns a JSON response with an error message if the start or exit point is missing
    in the maze. It returns an HTTP status code 400.
    """
    return (
        jsonify(
            {"valid": False, "error": "Start or exit point not found"}
        ),
        400,
    )


def save_maze_and_respond(map_grid, size):
    """
    Saves the provided maze to the database and responds with a JSON object containing
    the redirection URL to the newly saved maze map page.
    The maze is saved with the current user's information and the provided size.

    Args:
        map_grid (list): The maze representation as a list.
        size (tuple): The maze size (rows, columns).

    Returns:
        jsonify: A JSON object with the key "valid" set to True and the redirection URL.
    """
    json_str = json.dumps(map_grid)  # Convert the array to a list for JSON
    new_maze = MazeBd(grid=json_str, user_id=session.get(
        "user_id"), maze_size=size)
    db.session.add(new_maze)
    db.session.commit()

    maze_id = new_maze.id

    return jsonify(
        {"valid": True, "redirect_url": url_for("game.map", maze_id=maze_id)}
    )
