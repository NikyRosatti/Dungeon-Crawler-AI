from flask import Flask, redirect, render_template, request, url_for, session
from flask_socketio import SocketIO, emit
from flask_migrate import Migrate
import numpy as np
from database.models import db, User, MazeBd
from sqlalchemy import or_
import json
import threading
import time
from functools import wraps
from environment import maze

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

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Buscar el usuario en la base de datos
        user = User.query.filter(or_(User.username == username, User.email == username)).first()

        # Verificar si el usuario existe y la contraseña es correcta
        if user and user.password == password:
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
        password = request.form['password']
        email = request.form['email']

        # Comprobar si ya existe un usuario con ese nombre o correo
        existing_user = User.query.filter(or_(User.username == username, User.email == email)).first()

        if existing_user:
            # Si el usuario ya existe, devolver un mensaje de error
            return render_template('register.html', error="Usuario ya registrado")

        # Crear un nuevo usuario
        new_user = User(username=username, password=password, email=email,)
        
        # Añadir el nuevo usuario a la base de datos
        db.session.add(new_user)
        db.session.commit()

        # Guardar el ID del nuevo usuario en la sesión
        session['user_id'] = new_user.id
        
        # Redirigir al home o a la página que prefieras después del registro
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/mode_creative', methods=['GET','POST'])
def mode_creative():
    if request.method == 'POST':
        try:
            cantRow = int(request.form.get('rows', 0))
            print (1)
            cantColumn = int(request.form.get('columns', 0))
            print (2)
            entradaX = int(request.form.get('entradaX', 0))
            print (3)
            entradaY = int(request.form.get('entradaY', 0))
            print (4)
            salidaX = int(request.form.get('salidaX', 0))
            print (5)
            salidaY = int(request.form.get('salidaY', 0))
            print (6)

            if cantRow < 5 or cantColumn < 5:
                print (7)
                return render_template('mode_creative.html', error="Mapa muy pequeño")

            if entradaX >= cantRow or entradaY >= cantColumn or entradaX < 0 or entradaY < 0:
                print (8)
                return render_template('mode_creative.html', error="Entrada del maze inválida")

            if salidaX >= cantRow or salidaY >= cantColumn or salidaX < 0 or salidaY < 0:
                print (9)
                return render_template('mode_creative.html', error="Salida del maze inválida")
            print (10)
            grid = np.zeros((cantRow, cantColumn))
            grid[entradaX][entradaY] = 2
            grid[salidaX][salidaY] = 3

            for i in range(cantRow):
                for j in range(cantColumn):
                    try:
                        cell_value = int(request.form.get(f'cell_{i}_{j}', 0))
                        print (11)
                        if cell_value in [1, 4]:
                            print (12)
                            grid[i][j] = cell_value
                        else:
                            print (13)
                            return render_template('mode_creative.html', error="Número desconocido")
                    except ValueError:
                        print (14)
                        return render_template('mode_creative.html', error="Entrada inválida")

            # Aquí puedes agregar la lógica para verificar el laberinto y guardarlo en la base de datos
            print (15)
            json_str = json.dumps(grid.tolist())  # Convertir el array a lista para JSON
            print (16)
            new_maze = MazeBd(grid=json_str, entradaX=entradaX, entradaY=entradaY, salidaX=salidaX, salidaY=salidaY)
            # Si el laberinto es válido, guardar en la base de datos
            print (17)
            return render_template('mode_creative.html', success="Mapa creado exitosamente")

        except Exception as e:
            print (18)
            return render_template('mode_creative.html', error=f"Ocurrió un error: {str(e)}")

    # Si el método es GET, simplemente devuelve el formulario
    return render_template('mode_creative.html')
    

    
if __name__ == '__main__':
    socketio.run(app, debug=True)