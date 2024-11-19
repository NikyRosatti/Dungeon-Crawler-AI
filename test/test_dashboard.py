"""
Tests for the dashboard and related page functionalities in the web application.
"""


def test_redirect_map_creator(login_user):
    """Test redirection to map creator page for a logged-in user."""
    response = login_user.get('/map_creator')
    assert response.status_code == 200


def test_redirect_train_ai(login_user):
    """Test accessing a potentially restricted 'train-ai' page."""
    response = login_user.get('/train-ai')
    assert response.status_code == 404


def test_dashboard_loads_correctly(login_user):
    """Test that the dashboard loads correctly and contains expected content."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    assert b'Start New Dungeon' in response.data
    assert b'Choose Dungeon' in response.data
    assert b'Embark on a new adventure!' in response.data
    assert b'Train the AI with your own dungeons' in response.data


def test_access_dashboard_without_login(login_user):
    """Test accessing the dashboard without login status."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200


def test_access_train_ai_without_login(login_user):
    """Test accessing the 'train-ai' page without login status."""
    response = login_user.get('/train-ai')
    assert response.status_code == 404


def test_invalid_route_access(login_user):
    """Test accessing an invalid route and checking for 404 error."""
    response = login_user.get('/invalid-route')
    assert response.status_code == 404
    assert b'Not Found' in response.data


def test_dashboard_buttons_exist(login_user):
    """Test if expected buttons exist in the dashboard page."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'/map_creator' in response.data
    assert b'/community' in response.data


def test_dashboard_signs_content(login_user):
    """Test if expected signs content is present on the dashboard page."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'Embark on a new adventure!' in response.data
    assert b'Train the AI with your own dungeons' in response.data


def test_dashboard_css_loaded(login_user):
    """Test if the correct CSS file is loaded for the dashboard."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'css/dashboard.css' in response.data


def test_dashboard_structure(login_user):
    """Test for specific structure elements in the dashboard page."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'<div class="actions">' in response.data
    assert b'<div class="signs">' in response.data


def test_dashboard_signs_images(login_user):
    """Test for expected images on the dashboard signs."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'/static/img/cartelmadera.png' in response.data
    assert b'alt="Start New Dungeon Sign"' in response.data
    assert b'alt="Choose Dungeon Sign"' in response.data


def test_dashboard_links_functionality(login_user):
    """Test the functionality of expected links in the dashboard."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'href="/map_creator"' in response.data
    assert b'href="/community"' in response.data


def test_dashboard_content_order(login_user):
    """Test the order of content elements on the dashboard."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert response.data.index(
        b'<div class="actions">') < response.data.index(b'<div class="signs">')


def test_dashboard_uses_base_template(login_user):
    """Test that the dashboard page uses the base template."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'{% extends \'base.html\' %}' not in response.data
    assert b'<footer>' in response.data


def test_dashboard_meta_information(login_user):
    """Test for correct meta information in the dashboard page."""
    response = login_user.get('/dashboard')
    assert response.status_code == 200
    assert b'<meta charset="UTF-8">' in response.data
    assert b'<meta name="viewport"' in response.data
