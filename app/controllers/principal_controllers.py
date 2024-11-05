import json

from app.models import MazeBd, User, db


def build_maze_query(filter_by):
    query = MazeBd.query.join(User, MazeBd.user_id == User.id)

    # Map filters to ordering functions
    filter_map = {
        "created_at_desc": MazeBd.created_at.desc(),
        "created_at_asc": MazeBd.created_at.asc(),
        "username_asc": db.func.lower(User.username).asc(),
        "username_desc": db.func.lower(User.username).desc(),
        # Assuming the grid is stored as a string/JSON
        "grid_size_desc": db.func.length(MazeBd.grid).desc(),
        "grid_size_asc": db.func.length(MazeBd.grid).asc(),
    }

    # Apply the filter if it is valid
    order_by = filter_map.get(filter_by, MazeBd.created_at.desc())
    query = query.order_by(order_by)

    return query


def serialize_mazes(mazes):
    return [
        {
            "id": maze.id,
            "grid": json.loads(maze.grid),  # Convert the JSON string to list/matrix
            "created_at": (
                maze.created_at.strftime("%Y-%m-%d")
                if hasattr(maze.created_at, "strftime")
                else maze.created_at
            ),
            "username": User.query.get(maze.user_id).username,
        }
        for maze in mazes
    ]
