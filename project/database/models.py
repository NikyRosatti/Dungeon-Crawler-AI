from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class MazeBd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grid = db.Column(db.JSON, nullable = False)
    entradaX = db.Column( db.Integer, nullable=False)
    entradaY = db.Column(db.Integer, nullable=False)
    salidaX = db.Column(db.Integer, nullable=False)
    salidaY = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<MazeBd {self.grid}>'