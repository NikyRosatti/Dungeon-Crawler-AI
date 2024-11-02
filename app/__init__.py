from flask import Flask
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
socketio = SocketIO()


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    socketio.init_app(app)

    from app.routes.auth_routes import bp as bp_auth
    from app.routes.principal_routes import bp as bp_princ
    from app.routes.game_routes import bp as bp_game

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_princ)
    app.register_blueprint(bp_game)

    Migrate(app, db)

    with app.app_context():
        from app.models import User
        db.create_all()
        if User.query.filter_by(username="TheVoidItself").first() is None:
            null_user = User(
                username="TheVoidItself",
                password="Null",
                email="TheVoidItself",
                avatar="Null",
            )
            db.session.add(null_user)
            db.session.commit()
            print("Void user created")

    return app
