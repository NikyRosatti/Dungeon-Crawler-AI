from app import create_app, socketio
from config import DevelopmentConfig, TestConfig, ProductionConfig
import os

debug_mode = True

if os.getenv('APP_ENV') == 'production':
    debug_mode = False
    app = create_app(ProductionConfig)
elif os.getenv('APP_ENV') == 'testing':
    app = create_app(TestConfig)
else:
    app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    socketio.run(app, debug=debug_mode)
