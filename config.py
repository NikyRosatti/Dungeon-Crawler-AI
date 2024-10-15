import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mysecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dataBase.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    Testing = True
    Debug = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False