from app.models import User

def test_register_user(test_client):
    """Verifica que se pueda crear un nuevo usuario."""
    response = test_client.post('/register', data={
        'username': 'nuevo_usuario',
        'password': 'pass123',
        'email': 'nuevo@ejemplo.com',
        'avatar': '/static/img/avatars/ValenAvatar.png'  # Avatar válido
    })
    
    assert response.status_code == 302  # Verificar que se redirige
    assert b'Usuario ya registrado' not in response.data  # Verificar que no hay error de usuario existente

    # Verificar que el usuario se creó en la base de datos
    user = User.query.filter_by(username='nuevo_usuario').first()
    assert user is not None  # Asegurarse de que el usuario existe
    assert user.email == 'nuevo@ejemplo.com'  # Verificar que el correo electrónico es correcto


def test_register_user_without_avatar(test_client):
    """Verifica que no se pueda crear un nuevo usuario sin seleccionar un avatar."""
    response = test_client.post('/register', data={
        'username': 'usuario_sin_avatar',
        'password': 'pass123',
        'email': 'sin@avatar.com',
        'avatar': ''  # Sin avatar
    })

    assert response.status_code == 200  # Debería mostrar el formulario de registro nuevamente
    assert b'Debes seleccionar un avatar' in response.data  # Verificar que se muestra el error
    assert b'avatar' in response.data  # Verificar que los avatares se envían al template

def test_register_user_duplicate(test_client):
    """Verifica que no se pueda crear un nuevo usuario con un nombre de usuario ya registrado."""
    # Crear primero un usuario
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

    assert response.status_code == 304  # Debería mostrar el formulario de registro nuevamente
    assert b'Usuario ya registrado' in response.data  # Verificar que se muestra el error