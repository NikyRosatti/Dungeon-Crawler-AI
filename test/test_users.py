from app.models import User

def test_login_required_redirect(test_client):

    routes = [
        '/dashboard',
        '/leaderboard',
        '/profile',
        '/community', 
        '/settings', 
        '/map', 
        '/logout', 
        '/dungeons', 
        '/map_creator'
    ]

    for route in routes:
        response = test_client.get(route)
        assert response.status_code == 302
        assert 'Location' in response.headers
        assert response.headers['Location'] in '/login'

def test_register_user(test_client):
    response = test_client.post('/register', data={
        'username': 'nuevoUsuario',
        'password': 'password',
        'email': 'nuevo@ejemplo.com',
        'avatar': '/static/img/avatars/ValenAvatar.png'
    })
    
    assert response.status_code == 302
    assert b'Usuario ya registrado' not in response.data

    user = User.query.filter_by(username='nuevoUsuario').first()
    assert user is not None 
    assert user.email == 'nuevo@ejemplo.com' 


def test_register_user_without_avatar(test_client):
    # limpia la sesion al comenzar el test
    with test_client.session_transaction() as session:
        session.clear()

    response = test_client.post('/register', data={
        'username': 'usuarioSinAvatar',
        'password': 'password',
        'email': 'sin@avatar.com',
        'avatar': None
    })

    assert response.status_code == 400
    assert b'avatar' in response.data

def test_register_user_duplicate(test_client, add_user):
     # Primer intento de registro (este debería fallar si el usuario ya existe)
    response = test_client.post('/register', data={
        'username': 'usuarioTest',
        'password': 'password',
        'email': 'nuevo@ejemplo.com',  # Cambiamos el correo
        'avatar': '/static/img/avatars/ValenAvatar.png'
    })

    # Verifica que se reciba un error 400 (Usuario duplicado)
    assert response.status_code == 400
    assert b'' in response.data
    
def test_login_success(test_client, add_user):
    response = test_client.post('/login', data={
        'username': 'usuarioTest',
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
        'username': 'usuarioTest',
        'password': 'passwordmal'
    }, follow_redirects=True)

    assert response.status_code == 200
    
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
        'username': 'usuarioTest',
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
