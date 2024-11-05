import json

from flask import jsonify, session, url_for

from app.models import MazeBd, db

# Auxiliary Functions


def invalid_points_response():
    """Returns a JSON response if the start or exit point is missing."""
    return (
        jsonify(
            {"valid": False, "error": "Start or exit point not found"}
        ),
        400,
    )


def save_maze_and_respond(map_grid, size):
    """Saves the maze to the database and responds with the redirect URL."""
    json_str = json.dumps(map_grid)  # Convert the array to a list for JSON
    new_maze = MazeBd(grid=json_str, user_id=session.get("user_id"), maze_size=size)
    db.session.add(new_maze)
    db.session.commit()

    maze_id = new_maze.id

    return jsonify(
        {"valid": True, "redirect_url": url_for("game.map", maze_id=maze_id)}
    )
