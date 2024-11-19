"""
This module initializes the Flask application and its extensions,
including SQLAlchemy, SocketIO, Babel for internationalization, and Flask-Migrate.
It also sets up the routes for authentication, principal, and game functionality.
"""

from flask import Flask, request
from flask_babel import Babel
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app.helpers import get_user_language

# Initialize the app extensions
db = SQLAlchemy()
socketio = SocketIO()


def get_locale():
    """
    This function determines the best language locale for the user.
    It first tries to get the user's language preference from the session,
    then falls back to the best match from the supported languages list.
    """
    user_language = get_user_language()
    if user_language:
        return user_language
    return request.accept_languages.best_match(
        ["en", "es", "ru", "it", "de", "fr", "zh", "ja", "ga", "la"]
    )


def create_app(config_class):
    """
    Creates and configures the Flask app instance using the given config class.
    Initializes all extensions and registers routes.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)

    # Set up Babel for internationalization
    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)

    app.jinja_env.globals["get_locale"] = get_locale

    # Register blueprints for different routes
    from app.routes.auth_routes import bp as bp_auth
    from app.routes.principal_routes import bp as bp_princ
    from app.routes.game_routes import bp as bp_game

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_princ)
    app.register_blueprint(bp_game)

    # Initialize migration tool
    Migrate(app, db)

    # Create the database and a default user if needed
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
