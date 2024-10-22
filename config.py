import os
import sys
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mysecretkey'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    if getattr(sys, 'frozen', False):
        # Si está en un ejecutable, asegura que apunte al directorio correcto
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(sys._MEIPASS, "instance", "dataBase.db")}'
    else:
        # Si no, apunta al directorio del proyecto
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "instance", "dataBase.db")}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    Testing = True
    Debug = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False