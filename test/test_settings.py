from app.models import User


def test_update_password(login_user):

    response = login_user.post('/settings', data={
        'update_password': True,
        'current_password': 'password',
        'new_password': 'new_password',
        'confirm_password': 'new_password'
    })

    assert response.status_code == 200
    assert b'Password updated successfully.' in response.data
    response = login_user.post('/login', data={
        'username': 'usuario_test',
        'password': 'new_password'  # Nueva contraseña
    })

    assert response.status_code == 302
    assert response.headers['Location'] == '/dashboard'

    response = login_user.post('/settings', data={
        'update_password': True,
        'current_password': 'new_password',
        'new_password': 'password',
        'confirm_password': 'password'
    })


def test_update_password_incorrect(login_user):

    response = login_user.post('/settings', data={
        'update_password': True,
        'current_password': 'password_mal',
        'new_password': 'new_password',
        'confirm_password': 'new_password'
    })

    assert response.status_code == 200
    assert b'Incorrect current password.' in response.data


def test_update_password_do_not_match(login_user):

    response = login_user.post('/settings', data={
        'update_password': True,
        'current_password': 'password',
        'new_password': 'new_password',
        'confirm_password': 'password_mal'
    })

    assert response.status_code == 200
    assert b'New passwords do not match.' in response.data


def test_update_email_correct(login_user):

    response = login_user.post('/settings', data={
        'update_email': True,
        'new_email': 'email@nuevo.com',
        'confirm_email': 'email@nuevo.com'
    })

    assert response.status_code == 200
    assert b'Email updated successfully.' in response.data

    response = login_user.post('/settings', data={
        'update_email': True,
        'new_email': 'usuario@test.com',
        'confirm_email': 'usuario@test.com'
    })


def test_update_email_error(login_user):

    response = login_user.post('/settings', data={
        'update_email': True,
        'new_email': 'email@nuevo.com',
        'confirm_email': 'email@mal.com'
    })

    assert response.status_code == 200
    assert b'Emails do not match.' in response.data


def test_delete_account(login_user):

    response = login_user.post('/settings', data={
        'delete_account': True
    })

    existing_user = User.query.filter_by(email='usuario@test.com').first()
    assert existing_user == None
    with login_user.session_transaction() as sess:
        assert 'user_id' not in sess
    assert response.status_code == 302
    assert response.headers['Location'] == '/register'


def test_update_email_duplicate(test_client, login_user):

    test_client.post('/register', data={
        'username': 'nuevo_usuario',
        'password': 'pass123',
        'email': 'nuevo@ejemplo.com',
        'avatar': '/static/img/avatars/ValenAvatar.png'
    })

    response = test_client.post('/settings', data={
        'update_email': True,
        'new_email': 'usuario@test.com',
        'confirm_email': 'usuario@test.com'
    })
    assert response.status_code == 200
    assert b'Email is already in use.' in response.data
