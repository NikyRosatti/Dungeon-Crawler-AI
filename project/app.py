from flask import Flask, redirect, render_template, request, url_for, session
from flask_socketio import SocketIO, send, emit
from flask_migrate import Migrate
from database.models import db, User
from sqlalchemy import or_
import threading
import time
import bcrypt
from functools import wraps

app = Flask(__name__)

# Configuración de la base de datos (en este caso SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'  # Necesario para usar sesiones

# Inicializar la base de datos con la aplicación
db.init_app(app)
socketio = SocketIO(app)

# Crear la base de datos y las tablas si no existen
with app.app_context():
    db.create_all()

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirigir al login si no está autenticado
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        # Buscar el usuario en la base de datos
        user = User.query.filter(or_(User.username == username, User.email == username)).first()

        # Verificar si el usuario existe y la contraseña es correcta
        if user and bcrypt.checkpw(password, user.password):
            session['user_id'] = user.id  # Guardar el ID del usuario en la sesión
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Eliminar la sesión del usuario
    return redirect(url_for('login'))

# Ruta protegida, solo accesible si se ha iniciado sesión
@app.route('/home')
@login_required
def home():
    if 'user_id' in session:
        return "Bienvenido al Home!"
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        email = request.form['email']

        # Comprobar si ya existe un usuario con ese nombre o correo
        existing_user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()

        if existing_user:
            # Si el usuario ya existe, devolver un mensaje de error
            return render_template('register.html', error="Usuario ya registrado")

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        new_user = User(username=username, password=hashed_password, email=email,)
        
        # Añadir el nuevo usuario a la base de datos
        db.session.add(new_user)
        db.session.commit()

        # Guardar el ID del nuevo usuario en la sesión
        session['user_id'] = new_user.id
        
        # Redirigir al home o a la página que prefieras después del registro
        return redirect(url_for('login'))

    return render_template('register.html')

mapa_original = [
    -1, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 1, 1 , 0, 
    0, 1, 0, 0, 1, 0, 0,
    0, 1, 0, 0, 1, 0, 1,
    0, 0, 0, 0, 0, 0, 1,
    0, 1, 0, 0, 1, 0, 1,
    0, 0, 0, 1, 1, 0,3,
]

map_size = 7

def find_player_position():
    return mapa_original.index(-1)
@app.route('/map')
def map():
    return render_template('map.html', mapa_original=mapa_original)

@socketio.on('connect')
def handle_connect():
    emit('map', mapa_original)

@socketio.on('move')
def handle_move(direction):
    global mapa_original 
    print(f'Movimiento recibido: {direction}')

    player_pos = find_player_position()

    if direction == 'ArrowUp':
        new_pos = player_pos - map_size if player_pos >= map_size else player_pos
    elif direction == 'ArrowDown':
        new_pos = player_pos + map_size if player_pos < len(mapa_original) - map_size else player_pos
    elif direction == 'ArrowLeft':
        new_pos = player_pos - 1 if player_pos % map_size != 0 else player_pos
    elif direction == 'ArrowRight':
        new_pos = player_pos + 1 if (player_pos + 1) % map_size != 0 else player_pos
    else:
        new_pos = player_pos  

    if mapa_original[new_pos] == 0:
        mapa_original[player_pos] = 0
        mapa_original[new_pos] = -1  

    if mapa_original[new_pos] == 3:
        mapa_original[player_pos] = 0
        mapa_original [new_pos] = -2
        emit('finish_map', 'You Win!')
              
    emit('map', mapa_original)

@socketio.on('restart_pos')
def restart_position(position):
    global mapa_original 
    mapa_original[mapa_original.index(-2)] = 3
    mapa_original[position] = -1
    emit('map', mapa_original)

    
if __name__ == '__main__':
    socketio.run(app, debug=True)
