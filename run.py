from app import create_app, socketio
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    socketio.run(app, debug=True)
