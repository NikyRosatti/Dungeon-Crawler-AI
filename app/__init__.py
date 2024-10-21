from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate


db = SQLAlchemy()
socketio = SocketIO(async_mode='threading')

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    socketio.init_app(app)

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    Migrate(app, db)

    with app.app_context():
        db.create_all()

    return app
