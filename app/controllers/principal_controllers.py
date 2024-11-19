"""
This module contains functions for logic related to the visualization,
filtering, and serialization of mazes, as well as for updating the user's
language settings.
"""

import json

from flask import render_template, request
from flask_babel import gettext as _
from app.models import MazeBd, User, db


def build_maze_query(filter_by):
    """
    Builds a query to retrieve mazes filtered and sorted according to the
    `filter_by` parameter. The query can be sorted by creation date, username, or grid size.

    Args:
        filter_by (str): The filter by which to sort the mazes. It can be one of the following:
                          'created_at_desc', 'created_at_asc', 'username_asc', 'username_desc', 
                          'grid_size_desc', 'grid_size_asc'.

    Returns:
        query: The filtered and sorted query.
    """
    query = MazeBd.query.join(User, MazeBd.user_id == User.id)

    # Map filters to sorting functions
    filter_map = {
        "created_at_desc": MazeBd.created_at.desc(),
        "created_at_asc": MazeBd.created_at.asc(),
        "username_asc": db.func.lower(User.username).asc(),
        "username_desc": db.func.lower(User.username).desc(),
        # Assuming the grid is stored as a string/JSON
        "grid_size_desc": db.func.length(MazeBd.grid).desc(),
        "grid_size_asc": db.func.length(MazeBd.grid).asc(),
    }

    # Apply the filter if valid
    order_by = filter_map.get(filter_by, MazeBd.created_at.desc())
    query = query.order_by(order_by)

    return query


def serialize_mazes(mazes):
    """
    Serializes the mazes obtained from the database into a list of dictionaries,
    so they can be used in the frontend.

    Args:
        mazes (list): A list of MazeBd objects retrieved from the database.

    Returns:
        list: A list of dictionaries representing the mazes.
    """
    return [
        {
            "id": maze.id,
            # Convert the JSON string to a list/matrix
            "grid": json.loads(maze.grid),
            "created_at": (
                maze.created_at.strftime("%Y-%m-%d")
                if hasattr(maze.created_at, "strftime")
                else maze.created_at
            ),
            "username": User.query.get(maze.user_id).username,
        }
        for maze in mazes
    ]


def update_language(user):
    """
    Updates the user's language in the database and redirects to the settings page
    with a success message.

    Args:
        user (User): The user whose language is to be updated.

    Returns:
        render_template: The rendered settings template with the success message.
    """
    selected_language = request.form["language"]

    user.language = selected_language
    db.session.commit()

    return render_template(
        "settings.html",
        success=_("Language updated successfully."),
        user_language=selected_language,
    )
