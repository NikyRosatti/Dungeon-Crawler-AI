from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_babel import Babel


db = SQLAlchemy()
socketio = SocketIO()

def get_locale():
    return request.accept_languages.best_match(['en', 'es'])


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    socketio.init_app(app)

    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)

    app.jinja_env.globals['get_locale'] = get_locale

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    Migrate(app, db)

    with app.app_context():
        db.create_all()

    return app
