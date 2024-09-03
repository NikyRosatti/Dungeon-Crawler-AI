from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

current_position = (0, 0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@socketio.on('position_update')
def handle_position_update(data):
    global current_position
    current_position = data['position']
    emit('position_update', {'position': current_position}, broadcast=True)

def send_position():
    while True:
        socketio.emit('position_update', {'position': current_position})
        time.sleep(0.2)

thread = threading.Thread(target=send_position)
thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
