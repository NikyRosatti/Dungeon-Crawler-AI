from flask import Blueprint, render_template, redirect, request, url_for, session, jsonify, flash
from app.models import User, MazeBd, db
from sqlalchemy import or_
from flask_socketio import emit
from app import socketio
import bcrypt
from functools import wraps
from app.services.map_service import move_player, change_door
from app.environment.maze import Maze
import json
from stable_baselines3 import PPO
from app.environment.utils import is_winneable, generate_random_map, find_points
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import os
import time

bp = Blueprint('routes', __name__)
mapa_original = []
map_size = 0

# Decorador de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        user = User.query.filter(or_(User.username == username, User.email == username)).first()
        if user and bcrypt.checkpw(password, user.password):
            session['user_id'] = user.id
            return redirect(url_for('routes.dashboard'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']
        avatar = request.form['avatar']
        
        existing_user = User.query.filter(or_(User.username == username, User.email == email)).first()

        if existing_user:
            return render_template('register.html', error="Usuario ya registrado")

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        new_user = User(username=username, password=hashed_password, email=email, avatar=avatar)

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect(url_for('routes.dashboard'))

    avatars = [
            '/static/img/avatars/ValenAvatar.png',
            '/static/img/avatars/NikyAvatar.png',
            '/static/img/avatars/EstebanAvatar.png',
            '/static/img/avatars/GonzaAvatar.png',
            '/static/img/avatars/FlorAvatar.png',
            '/static/img/avatars/JoaquinTAvatar.png',
            '/static/img/avatars/JoaquinBAvatar.png',
            '/static/img/avatars/BrusattiAvatar.png',
            '/static/img/avatars/SimonAvatar.png',
            '/static/img/avatars/AgusAvatar.png'
    ]
    return render_template('register.html', avatars=avatars)

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.all()
    users_list = [{'username': user.username, 'completed_dungeons': user.completed_dungeons or 0} for user in users]
    users_sorted = sorted(users_list, key=lambda u: u['completed_dungeons'], reverse=True)
    return render_template('leaderboard.html', users=users_sorted)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        selected_avatar = request.form.get('avatar')
        if selected_avatar:
            user.avatar = selected_avatar
            db.session.commit()
            flash('Avatar actualizado con éxito!', 'success')
        else:
            flash('Por favor, selecciona un avatar.', 'danger')
        return redirect('/profile')

    avatars = [
        '/static/img/avatars/ValenAvatar.png',
        '/static/img/avatars/NikyAvatar.png',
        '/static/img/avatars/EstebanAvatar.png',
        '/static/img/avatars/GonzaAvatar.png',
        '/static/img/avatars/FlorAvatar.png',
        '/static/img/avatars/JoaquinTAvatar.png',
        '/static/img/avatars/JoaquinBAvatar.png',
        '/static/img/avatars/BrusattiAvatar.png',
        '/static/img/avatars/SimonAvatar.png',
        '/static/img/avatars/AgusAvatar.png'
    ]

    return render_template('profile.html', user=user, avatars=avatars)

@bp.route('/profile/<int:user_id>')
@login_required
def profileusers(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)

@bp.route('/myDungeons')
@login_required
def myDungeons():
    return render_template('myDungeons.html')


@bp.route('/dungeons')
@login_required
def my_mazes():
    user_id = session['user_id']
    user_mazes = MazeBd.query.filter_by(user_id = user_id).all()
    return render_template('user_mazes.html', mazes=user_mazes)


@bp.route("/map")
@login_required
def map():
    maze_id = request.args.get("maze_id")
    global mapa_original
    global map_size

    # Alternar comentarios en esta parte una vez finalizada esta parte
    # if not maze_id:
    #     return "ID de mapa no proporcionado", 400

    # maze = MazeBd.query.filter_by(id=maze_id).first()
    # if not maze:
    #     return "Mapa no encontrado", 404
    grid = [
        [2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 1, 1, 0],
        [3, 0, 0, 0, 0, 0, 0, 0],
    ]
    m = Maze(grid=grid)
    mapa_original = json.dumps(m.grid.tolist())
    map_size = m.size()
    return render_template("map.html", mapa_original=change_door(mapa_original))


@socketio.on('connect')
def handle_connect():
    if not mapa_original:
        emit('map', {'message': 'No hay un mapa cargado.'})
    else:
        emit('map', {'mapaOriginal': mapa_original, 'n': map_size})

@socketio.on('move')
def handle_move(direction):
    global mapa_original
    move_player(direction, mapa_original, map_size)

    if -2 in mapa_original:
        emit('finish_map', 'You Win!')
              
    emit('map', {'mapaOriginal': mapa_original, 'n': map_size})


@socketio.on('restart_pos')
def restart_position(position):
    global mapa_original
    mapa_original[mapa_original.index(-2)] = 3
    mapa_original[position] = -1
    emit('map', {'mapaOriginal': mapa_original, 'n': map_size})

@bp.route('/map_creator')
@login_required
def map_creator():
    return render_template('map_creator.html')


@bp.route("/validate_map", methods=["POST"])
@login_required
def validate_map():
    data = request.get_json()
    map_grid = data.get("map")  # El mapa que enviaste desde el frontend
    size = data.get("size")

    # Buscar el punto de inicio y de salida en el mapa
    start_point = None
    exit_point = None

    # Convertir el arreglo plano en una matriz
    grid = [map_grid[i : i + size] for i in range(0, len(map_grid), size)]

    # Identificar el punto de inicio (2) y de salida (3)
    start_point = None
    exit_point = None
    start_point, exit_point = find_points(
        grid=grid, start_point=start_point, exit_point=exit_point
    )

    if start_point is None or exit_point is None:
        return (
            jsonify(
                {"valid": False, "error": "No se encontró el punto de inicio o salida"}
            ),
            400,
        )

    # Validar si el laberinto es resoluble
    if is_winneable(grid):
        # Crear la instancia del laberinto
        new_maze = Maze(grid)
        json_str = json.dumps(map_grid)  # Convertir el array a lista para JSON
        new_maze = MazeBd(grid=json_str, user_id=session.get("user_id"), maze_size=size)
        db.session.add(new_maze)
        db.session.commit()

        maze_id = new_maze.id

        return jsonify(
            {"valid": True, "redirect_url": url_for("routes.map", maze_id=maze_id)}
        )
    else:
        return jsonify({"valid": False})


@socketio.on("start_simulation")
def test():

    grid = [
        [2, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [3, 1, 0, 0, 0, 0, 0, 0],
    ]

    # train ahora devuelve un VecNormalize. Usar esa clase es lo mismo que usar la clase Maze, solo que hacer un metodo
    # de la clase Maze sobre VecNormalize lo va a hacer sobre todos los Maze que tenga cargados y normalizados...
    envs = train(grid)
    print("Termine de entrenar")

    # Carpeta principal de modelos de PPO guardados
    models_dir = "./app/saved_models/ppo"
    # El nombre del .zip a cargar
    n_steps_model = "150000-1727904248"
    # Concatena la extension .zip
    model_to_load = f"{n_steps_model}" + ".zip"
    # Path completo: la carpeta y el archivo .zip
    model_path = f"{models_dir}/{model_to_load}"
    # Si no existe el modelo a cargar, tira la excepcion
    if not os.path.exists(model_path):
        raise FileExistsError(f"El modelo {model_path} elegido no existe!")
    # Carga el modelo guardado
    model = PPO.load(model_path, env=envs)
    print(f"Cargando el archivo {model_path}")

    print(f"Cant minima pasos para resolver el laberinto: {envs.minimum_steps}")
    episodes = 20
    max_steps = 100
    for ep in range(episodes):
        obs = envs.reset()
        done = False
        print(f"Episodio nro: {ep}")
        for pasos in range(0, max_steps + 1):
            action, _ = model.predict(obs)
            obs, reward, done, _ = envs.step(action)

            # Imprimir acción, recompensa y estado
            print(
                f"Observation: {obs}, Action: {action}, Reward: {reward}, Done: {done}, Paso nro: {pasos}"
            )

            current_map_state = envs.render()
            socketio.emit("map_update", current_map_state)
            time.sleep(0.01)
            if done:
                print("¡Laberinto resuelto!")
                break
            if pasos == max_steps:
                print(f"{max_steps} pasos alcanzados. Proximo episodio")


def train(grid):
    models_dir = "./app/saved_models/ppo"
    logdir = "./app/saved_models/logs"

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(logdir):
        os.makedirs(logdir)
    num_envs = 5
    # Envuelto en un entorno vectorizado
    envs = DummyVecEnv([lambda: Maze(grid) for _ in range(num_envs)])
    # Normalizar el entorno
    envs = VecNormalize(envs, norm_obs=True, norm_reward=True)

    print("Model: Creando el modelo")
    model = PPO("MlpPolicy", env=envs, verbose=2, tensorboard_log=logdir)

    # env = Maze(grid)

    # envs.reset()

    # print(f"Model: Cargando el archivo {models_dir}")
    # model = PPO.load(f"{models_dir}/10000", env=env)

    # Entrenar y guardar los modelos
    print("Inicio entrenamiento")
    TIMESTEPS = 10000
    for i in range(1, 30):
        model.learn(
            total_timesteps=TIMESTEPS, reset_num_timesteps=False, progress_bar=True
        )
        model.save(f"{models_dir}/{TIMESTEPS*i}-{int(time.time())}")
    print("Fin entrenamiento")

    # env.reset()
    return envs
