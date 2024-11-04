import os
from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    session,
    jsonify,
    flash,
)
from app.models import User, MazeBd, db
from sqlalchemy import or_
from flask_babel import gettext as _
from flask_socketio import emit
from app import socketio
import bcrypt
from functools import wraps
from app.services.map_service import move_player, change_door
from app.environment.maze import Maze
import json
from stable_baselines3 import PPO
from app.environment.utils import (
    is_winneable,
    find_points,
    action_to_string,
    obs_to_string,
)
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import time
import re

bp = Blueprint("routes", __name__)
maze_info = {
    "mapa_original": [],
    "start": None,
    "map_size": 0,
}

AVATARS = [
    "/static/img/avatars/ValenAvatar.png",
    "/static/img/avatars/NikyAvatar.png",
    "/static/img/avatars/EstebanAvatar.png",
    "/static/img/avatars/GonzaAvatar.png",
    "/static/img/avatars/FlorAvatar.png",
    "/static/img/avatars/JoaquinTAvatar.png",
    "/static/img/avatars/JoaquinBAvatar.png",
    "/static/img/avatars/BrusattiAvatar.png",
    "/static/img/avatars/SimonAvatar.png",
    "/static/img/avatars/AgusAvatar.png",
]


# Decorador de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("routes.login"))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method != "POST":
        return render_template("login.html")
    username = request.form["username"].strip()  # para evitar cadenas vacias con espacios
    password = request.form["password"].strip().encode("utf-8")

    user = User.query.filter(
        or_(User.username == username, User.email == username)
    ).first()

    if not user:
        return render_template("login.html", error=_("User does not exist.")), 400

    if not bcrypt.checkpw(password, user.password.encode("utf-8")):
        return render_template("login.html", error=_("Incorrect credentials.")), 400

    session["user_id"] = user.id
    return redirect(url_for("routes.dashboard"))

@bp.route("/logout")
@login_required
def logout():
    session.pop("user_id", None)
    session.clear()
    session.clear()
    return redirect(url_for("routes.login"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method != "POST":
        return render_template("register.html", avatars=AVATARS)

    EMAIL_REGEX = r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$"
    
    username = request.form["username"]
    password = request.form["password"].encode("utf-8")
    email = request.form["email"]
    avatar = request.form["avatar"]

    if not avatar:
        return render_template(
            "register.html", error=_("You must select an avatar"), avatars=AVATARS
        )

    existing_user = User.query.filter(
        or_(User.username == username, User.email == email)
    ).first()

    if existing_user:
      return render_template("register.html", error=_("Username already exists"), avatars=AVATARS), 400

    if len(username) < 3:
        return render_template("register.html", error=_("Username must have at least 3 characters"), avatars=AVATARS), 400

    if not username.isalnum():
        return render_template(
            "register.html", error=_("Username can only contain letters and numbers"), avatars=AVATARS
        ), 400

    if not re.match(EMAIL_REGEX, email):
        return render_template(
            "register.html", error=_("Please enter a valid email address"), avatars=AVATARS
        ), 400

    if len(password) < 8:
        return render_template("register.html", error=_("Password must have at least 8 characters"), avatars=AVATARS), 400

    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    new_user = User(
        username=username, password=hashed_password.decode('utf-8'), email=email, avatar=avatar
    )

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id
    return redirect(url_for("routes.dashboard"))


@bp.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    completed_dungeons = len(user.completed_dungeons)
    max_dungeon = None
    if user.completed_dungeons:
        max_dungeon = max(user.completed_dungeons, key=lambda dungeon: dungeon.maze_size)
        max_size = max_dungeon.maze_size
    else:
        max_size = 0  # Si no ha completado dungeons, el tamaño es 0

    points = user.points
    return render_template("dashboard.html", completed_dungeons = completed_dungeons, points = points, max_size= max_size)


@bp.route("/leaderboard")
@login_required
def leaderboard():
    
    sort_by = request.args.get('sort_by', 'completed_dungeons')  # 'completed_dungeons' como valor predeterminado
    order = request.args.get('order', 'desc')  # 'desc' como valor predeterminado
    
    
    users = User.query.all()
    users_list = [
        {
            "username": user.username,
            "completed_dungeons": len(user.completed_dungeons),
            "points": user.points,
            "max_size": max(user.completed_dungeons, key=lambda dungeon: dungeon.maze_size).maze_size  if user.completed_dungeons else 0
        }
        for user in users
    ]
    
    reverse_order = (order == 'desc')
    users_sorted = sorted(
        users_list, key=lambda u: u[sort_by], reverse=reverse_order
    )
    return render_template("leaderboard.html", users=users_sorted)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get_or_404(session["user_id"])

    if request.method != "POST":
        return render_template("profile.html", user=user, avatars=AVATARS)
    
    if selected_avatar := request.form.get("avatar"):
        user.avatar = selected_avatar
        db.session.commit()
        flash(_("Avatar updated successfully!"), "success")
    else:
        flash(_("Please, select an avatar."), "danger")
    return redirect("/profile")


@bp.route("/profile/<int:user_id>")
@login_required
def profileusers(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("profile.html", user=user)


@bp.route("/community")
@login_required
def community():
    # Obtener los parámetros de la solicitud, como el filtro y la página
    filter_by = request.args.get("filter", "created_at_desc")
    page = request.args.get("page", 1, type=int)
    per_page = 8

    # Construir la consulta base, uniendo con la tabla User
    query = build_maze_query(filter_by)

    # Paginación de los resultados
    paginated_mazes = query.paginate(page=page, per_page=per_page)

    # Serializar los laberintos
    mazes_serialized = serialize_mazes(paginated_mazes)

    # Manejo de la paginación
    pagination = {
        "page": paginated_mazes.page,
        "total_pages": paginated_mazes.pages,
        "has_next": paginated_mazes.has_next,
        "has_prev": paginated_mazes.has_prev,
        "next_num": paginated_mazes.next_num,
        "prev_num": paginated_mazes.prev_num,
    }

    # Devolver la plantilla con los datos
    return render_template(
        "community.html", mazes=json.dumps(mazes_serialized), pagination=pagination
    )


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


@bp.route("/dungeons")
@login_required
def my_mazes():
    user_id = session["user_id"]
    user_mazes = MazeBd.query.filter_by(user_id=user_id).all()

    # Convertir los mazes a diccionarios serializables
    user_mazes_serialized = serialize_mazes(user_mazes)

    return render_template("user_mazes.html", mazes=json.dumps(user_mazes_serialized))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        # Actualizar contraseña
        if "update_password" in request.form:
            return update_password(user)

        elif "update_email" in request.form:
            return update_email(user)

        elif "delete_account" in request.form:
            return delete_account(user)

        elif "update_language" in request.form:
            return update_language(user)
        
    return render_template("settings.html")


def update_password(user):
    current_password = request.form["current_password"].encode("utf-8")
    new_password = request.form["new_password"].encode("utf-8")
    confirm_password = request.form["confirm_password"].encode("utf-8")

    if not bcrypt.checkpw(current_password, user.password):
        return render_template(
            "settings.html", error=_("Incorrect current password.")
        )

    if new_password != confirm_password:
        return render_template(
            "settings.html", error=_("New passwords do not match.")
        )

    hashed_new_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
    user.password = hashed_new_password
    db.session.commit()

    return render_template(
        "settings.html", success=_("Password updated successfully.")
    )


def update_email(user):
    new_email = request.form["new_email"]
    confirm_email = request.form["confirm_email"]

    if new_email != confirm_email:
        return render_template("settings.html", error=_("Emails do not match."))

    if User.query.filter_by(email=new_email).first():
        return render_template(
            "settings.html", error=_("Email is already in use.")
        )

    user.email = new_email
    db.session.commit()

    return render_template(
        "settings.html", success=_("Email updated successfully.")
    )

def update_language(user):
    selected_language = request.form["language"]

    user.language = selected_language
    db.session.commit()

    return render_template(
        "settings.html",
        success=_("Language updated successfully."),
        user_language=selected_language
    )


def delete_account(user):
    db.session.delete(user)
    db.session.commit()

    session.clear()
    return redirect(url_for("routes.register"))


@bp.route("/map")
@login_required
def map():
    maze_id = int(request.args.get("maze_id", 0))
    maze = MazeBd.query.filter_by(id=maze_id).first()

     # Diccionario con información del laberinto
    maze_info["mapa_original"] = json.loads(maze.grid)  # Asigna el grid a mapa_original,
    maze_info["start"] = maze_info["mapa_original"].index(2)
    maze_info["map_size"] = maze.maze_size  # Calcula el tamaño del mapa

    avatar = User.query.get(session["user_id"]).avatar
    return render_template(
        "map.html",
        mapa_original=change_door(maze_info["mapa_original"]),
        avatar=avatar,
        maze_id=maze_id,
    )


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
    maze_info["mapa_original"][maze_info["mapa_original"].index(-2)] = 3
    maze_info["mapa_original"][maze_info["start"]] = -1
    emit("map", maze_info["mapa_original"])


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
    start_point, exit_point = find_points_in_grid(grid)

    if not are_points_valid(start_point, exit_point):
        return invalid_points_response()

    # Validar si el laberinto es resoluble
    if is_winneable(grid):
        return save_maze_and_respond(grid, map_grid, size)
    else:
        return jsonify({"valid": False})

# Funciones Auxiliares

def create_grid(map_grid, size):
    """Convierte el arreglo plano en una matriz 2D."""
    return [map_grid[i: i + size] for i in range(0, len(map_grid), size)]

def find_points_in_grid(grid):
    """Encuentra los puntos de inicio y salida en el mapa."""
    start_point, exit_point = None, None
    return find_points(grid=grid, start_point=start_point, exit_point=exit_point)

def are_points_valid(start_point, exit_point):
    """Valida si se encontraron el punto de inicio y salida."""
    return start_point is not None and exit_point is not None

def invalid_points_response():
    """Devuelve una respuesta JSON en caso de que falte el punto de inicio o salida."""
    return jsonify({"valid": False, "error": "No se encontró el punto de inicio o salida"}), 400

def save_maze_and_respond(grid, map_grid, size):
    """Guarda el laberinto en la base de datos y responde con la URL de redirección."""
    json_str = json.dumps(map_grid)  # Convertir el array a lista para JSON
    new_maze = MazeBd(grid=json_str, user_id=session.get("user_id"), maze_size=size)
    db.session.add(new_maze)
    db.session.commit()

    maze_id = new_maze.id

    return jsonify({"valid": True, "redirect_url": url_for("routes.map", maze_id=maze_id)})


@socketio.on("start_simulation")
def train(maze_id):

    maze = MazeBd.query.filter_by(id=maze_id).first()

    grid1 = json.loads(maze.grid)
    size = maze.maze_size

    grid = [grid1[i : i + size] for i in range(0, len(grid1), size)]

    log_dir = os.path.join("app", "saved_models", "logs", f"{maze_id}")
    os.makedirs(log_dir, exist_ok=True)

    num_envs = 5
    env = DummyVecEnv([lambda: Maze(grid) for _ in range(num_envs)])

    model_path = os.path.join(
        "app", "saved_models", "trained_models_per_id", str(maze_id), ""
    )
    os.makedirs(model_path, exist_ok=True)

    try:
        env = VecNormalize.load(load_path=model_path + "norm_env.pkl", venv=env)
        print("TrainEnv: Retraining the environment")
    except:
        env = VecNormalize(env, norm_obs=False, norm_reward=True, clip_obs=10.0)
        print("TrainEnv: Creating the environment")

    try:
        model = PPO.load(path=model_path + "ppo.zip", env=env)
        print("TrainModel: Retraining the model")
    except:
        model = PPO("MlpPolicy", env=env, verbose=0, tensorboard_log=log_dir)
        print("TrainModel: Creating the model")

    print("Training started")
    timesteps = 10000
    iterations_per_learning = 10
    for i in range(iterations_per_learning):
        print(f"Training iteration {i+1}!")
        model.learn(
            total_timesteps=timesteps, reset_num_timesteps=False, progress_bar=True
        )
        # Calcular el progreso
        progress = ((i + 1) / iterations_per_learning) * 100
        print(f"Progress: {progress:.2f}%")

        # Emitir progreso a todas las páginas conectadas
        socketio.emit("progress", {"progress": progress})
        model.save(model_path + "ppo.zip")
    print(f"Model {model_path} saved successfully")
    env.save(model_path + "norm_env.pkl")
    print("Environments saved successfully")
    print("End of training")


running_tests = {}


@socketio.on("testTraining")
def test(data):
    global running_tests

    maze_id = int(data.get("maze_id"))
    running_tests[maze_id] = True

    # Cargar el laberinto desde la base de datos
    maze, grid, size = load_maze_from_db(maze_id)

    # Vectorizar entornos y cargar el modelo
    env, model = setup_environment(grid, maze_id)

    # Ejecutar la prueba de entrenamiento
    run_training_test(env, model, maze_id, maze, size)


def load_maze_from_db(maze_id):
    """Carga el laberinto desde la base de datos y devuelve su información."""
    maze = MazeBd.query.filter_by(id=maze_id).first()
    grid1 = json.loads(maze.grid)
    size = maze.maze_size
    grid = [grid1[i: i + size] for i in range(0, len(grid1), size)]

    return maze, grid, size


def setup_environment(grid, maze_id):
    """Configura el entorno de entrenamiento y carga el modelo PPO."""
    vec_norm_path = os.path.join(
        "app", "saved_models", "trained_models_per_id", str(maze_id), "norm_env.pkl"
    )
    model_to_load = os.path.join(
        "app", "saved_models", "trained_models_per_id", str(maze_id), "ppo.zip"
    )

    env = DummyVecEnv([lambda: Maze(grid)])
    try:
        env = VecNormalize.load(load_path=vec_norm_path, venv=env)
        print(f"Loading the environment {vec_norm_path}")
    except:
        print(f"Vectorized environment not found, loading a generic one")
        env = VecNormalize(env, norm_obs=False, norm_reward=True, clip_obs=10.0)

    try:
        model = PPO.load(model_to_load, env=env)
        print(f"Loading the file {model_to_load}")
    except:
        print("Playing without a trained model!")
        model = PPO("MlpPolicy", env=env)

    return env, model


def run_training_test(env, model, maze_id, maze, size):
    """Ejecuta la prueba de entrenamiento y emite el estado del mapa en tiempo real."""
    global running_tests

    print(f"Minimum steps required to solve the maze: {env.envs[0].minimum_steps}")

    user = User.query.get(session["user_id"])
    env.training = False
    env.norm_reward = False
    obs = env.reset()
    steps = 0
    while steps < env.envs[0].maximum_steps:
        steps += 1
        print(f"Steps: {steps}")

        if not running_tests.get(maze_id):  # Si se ha solicitado detener la prueba
            print(f"Test stopped for maze_id {maze_id}")
            socketio.emit("training_status", {"status": "stopped"})
            running_tests.pop(maze_id, None)
            break

        action, _ = model.predict(obs)
        print(f"  Action according to the prediction: {action_to_string(action)}")
        obs, reward, done, _ = env.step(action)
        print(
            f"  Observation after the step: {obs_to_string(obs)}"
            + f"  Reward: {reward}, Done: {done}"
        )

        current_map_state = env.envs[0].get_current_map_state()
        socketio.emit("map", current_map_state)
        time.sleep(0.05)

        if done:
            win = env.envs[0].episode_result.get("win")
            lose_by_mine = env.envs[0].episode_result.get("lose_by_mine")
            lose_by_steps = env.envs[0].episode_result.get("lose_by_steps")
            if win:
                print("Maze solved")
                if maze not in user.completed_dungeons:
                    user.completed_dungeons.append(maze)
                    if env.envs[0].minimum_steps == steps:
                        user.points += size + steps
                    else:
                        user.points += size
                    db.session.commit()
                    socketio.emit("training_status", {"status": "finished"})
                    print(f"User {user.username} completed the maze {maze_id}.")
                else:
                    print(f"The user {user.username} already completed this maze.")
                socketio.emit("training_status", {"status": "finished"})

            if lose_by_mine:
                print("You agent died brutally when stepped in a mine")

            if lose_by_steps:
                print(
                    f"Your agent could not complete the maze in {env.envs[0].maximum_steps} steps!!"
                )

            break

    running_tests.pop(maze_id, None)  # Eliminar la prueba de la lista de ejecuciones


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
