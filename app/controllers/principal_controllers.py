import json

from flask import render_template, request
from flask_babel import gettext as _

from app.models import MazeBd, User, db


def build_maze_query(filter_by):
    query = MazeBd.query.join(User, MazeBd.user_id == User.id)

    # Mapear filtros a funciones de orden
    filter_map = {
        "created_at_desc": MazeBd.created_at.desc(),
        "created_at_asc": MazeBd.created_at.asc(),
        "username_asc": db.func.lower(User.username).asc(),
        "username_desc": db.func.lower(User.username).desc(),
        # Asumiendo que el grid se guarda como string/JSON
        "grid_size_desc": db.func.length(MazeBd.grid).desc(),
        "grid_size_asc": db.func.length(MazeBd.grid).asc(),
    }

    # Aplicar el filtro si es válido
    order_by = filter_map.get(filter_by, MazeBd.created_at.desc())
    query = query.order_by(order_by)

    return query


def serialize_mazes(mazes):
    return [
        {
            "id": maze.id,
            "grid": json.loads(maze.grid),  # Convertir la cadena JSON a lista/matriz
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
    selected_language = request.form["language"]

    user.language = selected_language
    db.session.commit()

    return render_template(
        "settings.html",
        success=_("Language updated successfully."),
        user_language=selected_language,
    )
