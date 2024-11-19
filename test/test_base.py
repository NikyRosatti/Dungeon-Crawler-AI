"""
Tests for redirect behavior and session management in the application routes.
"""


def test_redirect_dashboard(login_user):
    """Test if an authenticated user can access the dashboard page."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200


def test_redirect_profile(login_user):
    """Test if an authenticated user can access the profile page."""
    response = login_user.get('/profile')
    assert response.status_code == 200


def test_redirect_dungeons(login_user):
    """Test if an authenticated user can access the dungeons page."""
    response = login_user.get('/dungeons')
    assert response.status_code == 200


def test_redirect_community(login_user):
    """Test if an authenticated user can access the community page."""
    response = login_user.get('/community')
    assert response.status_code == 200


def test_redirect_leaderboard(login_user):
    """Test if an authenticated user can access the leaderboard page."""
    response = login_user.get('/leaderboard')
    assert response.status_code == 200


def test_redirect_settings(login_user):
    """Test if an authenticated user can access the settings page."""
    response = login_user.get('/settings')
    assert response.status_code == 200


def test_logout(login_user):
    """Test if logging out redirects the user to the login page and clears the session."""
    response = login_user.get('/logout')
    assert response.status_code == 302
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/login'

    with login_user.session_transaction() as session:
        assert 'user_id' not in session
