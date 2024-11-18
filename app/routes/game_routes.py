import json

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    session,
)
from flask_socketio import emit

from app import socketio
from app.controllers.auth_controllers import login_required
from app.controllers.game_controllers import (
    invalid_points_response,
    save_maze_and_respond,
)
from app.models import User, MazeBd
from app.services.map_services import (
    are_points_valid,
    change_door,
    create_grid,
    find_points,
    is_winneable,
    load_maze_from_db,
    move_player,
)
from app.services.train_services import (
    running_tests,
    run_training_test,
    setup_environment,
    train_model,
)

bp = Blueprint("game", __name__)
maze_info = {
    "mapa_original": [],
    "start": None,
    "map_size": 0,
}


@bp.route("/map")
@login_required
def map():
    maze_id = int(request.args.get("maze_id", 0))
    maze = MazeBd.query.filter_by(id=maze_id).first()

    # Diccionario con información del laberinto
    maze_info["mapa_original"] = json.loads(
        maze.grid
    )  # Asigna el grid a mapa_original,
    maze_info["start"] = maze_info["mapa_original"].index(2)
    maze_info["map_size"] = maze.maze_size  # Calcula el tamaño del mapa

    avatar = User.query.get(session["user_id"]).avatar
    return render_template(
        "map.html",
        mapa_original=change_door(maze_info["mapa_original"]),
        avatar=avatar,
        maze_id=maze_id,
    )


@bp.route("/map_creator")
@login_required
def map_creator():
    return render_template("map_creator.html")


@bp.route("/validate_map", methods=["POST"])
@login_required
def validate_map():
    data = request.get_json()
    map_grid = data.get("map")
    size = data.get("size")

    # Convertir el array en una matriz
    grid = create_grid(map_grid, size)

    # Identificar el punto de inicio (2) y de salida (3)
    start_point, exit_point = find_points(grid)

    if not are_points_valid(start_point, exit_point):
        return invalid_points_response()

    # Validar si el laberinto es resoluble
    if is_winneable(grid):
        return save_maze_and_respond(map_grid, size)
    else:
        return jsonify({"valid": False})


@socketio.on("start_training")
def handle_training(data):
    maze_id = data.get("maze_id")
    if maze_id is not None:
        emit("training_status", {"status": "started"})
        train(maze_id)
        emit("training_status", {"status": "finished"})
    else:
        emit("training_status", {"status": "error", "message": "Maze ID is missing"})


@socketio.on("testTraining")
def handle_test(data):
    maze_id = data.get("maze_id")
    if maze_id is not None:
        emit("training_status", {"status": "started"})
        train(maze_id)
        emit("training_status", {"status": "finished"})
    else:
        emit("training_status", {"status": "error", "message": "Maze ID is missing"})


@socketio.on("connect")
def handle_connect():
    if not maze_info["mapa_original"]:  # Verificar si mapa_original está inicializado
        emit("map", "No hay un mapa cargado.")
    else:
        emit("map", maze_info["mapa_original"])


@socketio.on("move")
def handle_move(direction):
    move_player(direction, maze_info["mapa_original"], maze_info["map_size"])

    if -2 in maze_info["mapa_original"]:
        emit("finish_map", "You Win!")

    emit("map", maze_info["mapa_original"])


@socketio.on("restart_pos")
def restart_position(position):
    maze_info["mapa_original"][maze_info["mapa_original"].index(-1)] = 3
    maze_info["mapa_original"][maze_info["start"]] = -1
    emit("map", maze_info["mapa_original"])


@socketio.on("start_simulation")
def train(maze_id):
    for progress_emit in train_model(maze_id):
        emit("progress", progress_emit)


@socketio.on("testTraining")
def test(data):
    global running_tests

    maze_id = int(data.get("maze_id"))
    running_tests[maze_id] = True

    # Cargar el laberinto desde la base de datos
    maze, grid, size = load_maze_from_db(maze_id)

    # Vectorizar entornos y cargar el modelo
    env, model = setup_environment(grid, maze_id)

    # Ejecutar la prueba de entrenamiento y emitir los resultados
    run_training_test(env, model, maze_id, maze, size)


@socketio.on("stopTraining")
def stop_test(data):
    maze_id = data.get("maze_id")
    maze_id = int(maze_id)

    global running_tests
    if maze_id in running_tests:
        running_tests[maze_id] = False  # Señalar que se debe detener el test
        print(f"Request to stop the test {maze_id}")
    else:
        socketio.emit(
            "training_status",
            {
                "status": "error",
                "message": "There is no test running for this maze_id",
            },
        )
