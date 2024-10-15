from app.models import User

def test_register_user(test_client):
    response = test_client.post('/register', data={
        'username': 'nuevo_usuario',
        'password': 'pass123',
        'email': 'nuevo@ejemplo.com',
        'avatar': '/static/img/avatars/ValenAvatar.png'
    })
    
    assert response.status_code == 302
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

    # Intentar crear el mismo usuario de nuevo
    response = test_client.post('/register', data={
        'username': 'usuario_existente',
        'password': 'pass123',
        'email': 'nuevo@ejemplo.com',
        'avatar': '/static/img/avatars/ValenAvatar.png'
    })

    assert response.status_code == 400 
    assert b'' in response.data