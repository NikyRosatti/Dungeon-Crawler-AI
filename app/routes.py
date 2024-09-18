from flask import Blueprint, render_template, redirect, request, url_for, session, jsonify, flash
from app.models import User, MazeBd, db
from sqlalchemy import or_
from flask_socketio import emit
from app import socketio
import bcrypt
from functools import wraps
from app.services.map_service import move_player, change_door
from app.environment import maze
import json

bp = Blueprint('routes', __name__)

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
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']

        existing_user = User.query.filter(or_(User.username == username, User.email == email)).first()

        if existing_user:
            return render_template('register.html', error="Usuario ya registrado")

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        new_user = User(username=username, password=hashed_password, email=email)

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect(url_for('routes.dashboard'))

    return render_template('register.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/leaderboard')
def leaderboard():
    users = User.query.all()
    users_list = [{'username': user.username, 'completed_dungeons': user.completed_dungeons or 0} for user in users]
    users_sorted = sorted(users_list, key=lambda u: u['completed_dungeons'], reverse=True)
    return render_template('leaderboard.html', users=users_sorted)



@bp.route('/profile', methods=['GET', 'POST'])
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
        'static/img/avatars/SimonAvatar.png'
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

@bp.route('/map')
@login_required
def map():
    return render_template('map.html', mapa_original=change_door(mapa_original))

@socketio.on('connect')
def handle_connect():
    if not mapa_original:  # Verificar si mapa_original está inicializado
        emit('map', 'No hay un mapa cargado.')
    else:
        emit('map', mapa_original)

@socketio.on('move')
def handle_move(direction):
    global mapa_original
    move_player(direction, mapa_original, map_size)

    if -2 in mapa_original:
        emit('finish_map', 'You Win!')
              
    emit('map', mapa_original)


@socketio.on('restart_pos')
def restart_position(position):
    global mapa_original
    mapa_original[mapa_original.index(-2)] = 3
    mapa_original[position] = -1
    emit('map', mapa_original)

@bp.route('/map_creator')
def map_creator():
    return render_template('map_creator.html')

mapa_original = []
map_size = 0

@bp.route('/validate_map', methods=['POST'])
def validate_map():
    data = request.get_json()
    map_grid = data.get('map')  # El mapa que enviaste desde el frontend
    size = int(len(map_grid) ** 0.5)  # Suponiendo que el mapa es cuadrado

    # Buscar el punto de inicio y de salida en el mapa
    start_point = None
    exit_point = None

    # Convertir el arreglo plano en una matriz
    grid = [map_grid[i:i + size] for i in range(0, len(map_grid), size)]

    # Identificar el punto de inicio (2) y de salida (3)
    for row in range(size):
        for col in range(size):
            if grid[row][col] == 2:
                start_point = (row, col)
            if grid[row][col] == 3:
                exit_point = (row, col)

    if start_point is None or exit_point is None:
        return jsonify({'valid': False, 'error': 'No se encontró el punto de inicio o salida'}), 400

    # Crear la instancia del laberinto
    new_maze = maze.Maze(grid, size, start_point, exit_point)

    # Validar si el laberinto es resoluble
    if new_maze.is_winneable():
        json_str = json.dumps(map_grid)  # Convertir el array a lista para JSON
        new_maze = MazeBd(grid=json_str, user_id = session.get('user_id'))
        db.session.add(new_maze)
        db.session.commit()
        
        global mapa_original
        global map_size

        mapa_original = map_grid  # Guardar el mapa validado en la variable global
        map_size = size        
        # Redirigir a la ruta '/map' pasando el mapa validado
        return jsonify({'valid': True, 'redirect_url': url_for('routes.map')})
    else:
        return jsonify({'valid': False})

