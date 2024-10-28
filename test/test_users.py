import flask
from app.models import User

def test_login_required_redirect(test_client):

    routes = [
        '/dashboard',
        '/leaderboard',
        '/profile',
        '/community',
        '/my_mazes', 
        '/settings', 
        '/map', 
        '/logout', 
        '/dungeons', 
        '/map_creator', 
        '/validate_map'
    ]

    for route in routes:
        response = test_client.get(route)
        assert response.status_code == 302
        assert 'Location' in response.headers
        assert response.headers['Location'] in '/login'

def test_register_user(test_client):
    response = test_client.post('/register', data={
        'username': 'nuevo_usuario',
        'password': 'pass123',
        'email': 'nuevo@ejemplo.com',
        'avatar': '/static/img/avatars/ValenAvatar.png'
    })
    
    assert response.status_code == 200
    assert b'Usuario ya registrado' not in response.data

    user = User.query.filter_by(username='nuevo_usuario').first()
    assert user is not None 
    assert user.email == 'nuevo@ejemplo.com' 


def test_register_user_without_avatar(test_client):
    response = test_client.post('/register', data={
        'username': 'usuario_sin_avatar',
        'password': 'pass123',
        'email': 'sin@avatar.com',
        'avatar': ''
    })

    assert response.status_code == 400
    assert b'Please, choose an avatar before register.' in response.data  
    assert b'avatar' in response.data

def test_register_user_duplicate(test_client):
    test_client.post('/register', data={
        'username': 'usuario_existente',
        'password': 'pass123',
        'email': 'existente@ejemplo.com',
        'avatar': '/static/img/avatars/NikyAvatar.png'
    })

    response = test_client.post('/register', data={
        'username': 'usuario_existente',
        'password': 'pass123',
        'email': 'nuevo@ejemplo.com',
        'avatar': '/static/img/avatars/ValenAvatar.png'
    })

    assert response.status_code == 400 
    assert b'' in response.data
    
def test_login_success(test_client, add_user):
    response = test_client.post('/login', data={
        'username': 'usuario_test',
        'password': 'password'
    })

    assert response.status_code == 302
    with test_client.session_transaction() as sess:
        assert 'user_id' in sess
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/dashboard'


def test_get_login(test_client):
    response = test_client.get('/login', follow_redirects=True)
    assert response.status_code == 200

def test_get_register(test_client):
    response = test_client.get('/register', follow_redirects=True)
    assert response.status_code == 200

def test_login_fail(test_client, add_user):
    response = test_client.post('/login', data={
        'username': 'usuario_test',
        'password': 'passwordmal'
    })

    assert response.status_code == 400
    assert b'Incorrect credentials' in response.data
    
def test_login_user_not_exist(test_client):
    with test_client.session_transaction() as session:
        session.clear()

    response = test_client.post('/login', data={
        'username': 'usuario',
        'password': 'password'
    })

    assert response.status_code == 400
    assert b'User does not exist.' in response.data
    
def test_logout(test_client):
    response = test_client.post('/login', data={
        'username': 'usuario_test',
        'password': 'password'
    })
    
    assert response.status_code == 302
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/dashboard'
    
    response = test_client.get('/logout')
    
    assert response.status_code == 302
    with test_client.session_transaction() as sess:
        assert 'user_id' not in sess
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/login'
    
    with test_client.session_transaction() as session:
        assert 'user_id' not in session


