"""
This script is the entry point for running the Flask application.

It configures the app based on the environment (production, testing, or development)
and starts the application with SocketIO.
"""

import os
from config import DevelopmentConfig, TestConfig, ProductionConfig
from app import create_app, socketio

# Constant for the debug mode, should be in uppercase
DEBUG_MODE = True

# Determine which configuration to use based on the APP_ENV environment variable
if os.getenv('APP_ENV') == 'production':
    DEBUG_MODE = False
    app = create_app(ProductionConfig)
elif os.getenv('APP_ENV') == 'testing':
    app = create_app(TestConfig)
else:
    app = create_app(DevelopmentConfig)

# Run the app with SocketIO
if __name__ == '__main__':
    socketio.run(app, debug=DEBUG_MODE)
