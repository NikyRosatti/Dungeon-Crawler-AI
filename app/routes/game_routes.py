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
    "original_map": [],
    "start": None,
    "map_size": 0,
}


@bp.route("/map")
@login_required
def map():
    maze_id = int(request.args.get("maze_id", 0))
    maze = MazeBd.query.filter_by(id=maze_id).first()

    # Dictionary with maze information
    maze_info["original_map"] = json.loads(
        maze.grid
    )  # Assign the grid to original_map,
    maze_info["start"] = maze_info["original_map"].index(2)
    maze_info["map_size"] = maze.maze_size  # Calculate the map size

    avatar = User.query.get(session["user_id"]).avatar
    return render_template(
        "map.html",
        original_map=change_door(maze_info["original_map"]),
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

    # Convert the array into a matrix
    grid = create_grid(map_grid, size)

    # Identify the start (2) and exit (3) points
    start_point, exit_point = find_points(grid)

    if not are_points_valid(start_point, exit_point):
        return invalid_points_response()

    # Validate if the maze is solvable
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
    if not maze_info["original_map"]:  # Check if original_map is initialized
        emit("map", "No map loaded.")
    else:
        emit("map", maze_info["original_map"])


@socketio.on("move")
def handle_move(direction):
    move_player(direction, maze_info["original_map"], maze_info["map_size"])

    if -2 in maze_info["original_map"]:
        emit("finish_map", "You Win!")

    emit("map", maze_info["original_map"])


@socketio.on("restart_pos")
def restart_position(position):
    maze_info["original_map"][maze_info["original_map"].index(-2)] = 3
    maze_info["original_map"][maze_info["start"]] = -1
    emit("map", maze_info["original_map"])


@socketio.on("start_simulation")
def train(maze_id):
    for progress_emit in train_model(maze_id):
        emit("progress", progress_emit)


@socketio.on("testTraining")
def test(data):
    global running_tests

    maze_id = int(data.get("maze_id"))
    running_tests[maze_id] = True

    # Load the maze from the database
    maze, grid, size = load_maze_from_db(maze_id)

    # Vectorize environments and load the model
    env, model = setup_environment(grid, maze_id)

    # Run the training test and emit results
    for update in run_training_test(env, model, maze_id, maze, size):
        socketio.emit("training_update", update["status"])
        socketio.emit("map", update["map"])


@socketio.on("stopTraining")
def stop_test(data):
    maze_id = data.get("maze_id")
    maze_id = int(maze_id)

    global running_tests
    if maze_id in running_tests:
        running_tests[maze_id] = False  # Mark that the test should be stopped
        print(f"Request to stop the test {maze_id}")
    else:
        socketio.emit(
            "training_status",
            {
                "status": "error",
                "message": "There is no test running for this maze_id",
            },
        )
