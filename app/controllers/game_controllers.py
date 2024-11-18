import json

from flask import jsonify, session, url_for

from app.models import MazeBd, db

# Funciones Auxiliares


def invalid_points_response():
    """Devuelve una respuesta JSON en caso de que falte el punto de inicio o salida."""
    return (
        jsonify(
            {"valid": False, "error": "No se encontró el punto de inicio o salida"}
        ),
        400,
    )


def save_maze_and_respond(map_grid, size):
    """Guarda el laberinto en la base de datos y responde con la URL de redirección."""
    json_str = json.dumps(map_grid)  # Convertir el array a lista para JSON
    new_maze = MazeBd(grid=json_str, user_id=session.get("user_id"), maze_size=size)
    db.session.add(new_maze)
    db.session.commit()

    maze_id = new_maze.id

    return jsonify(
        {"valid": True, "redirect_url": url_for("game.map", maze_id=maze_id)}
    )
