from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/login', methods=['GET','POST'])
def login():
    if (request.method == 'POST'):
        username = request.form['first']
        password = request.form['password']
        return redirect(url_for('home'))
    
    return render_template('login.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)
