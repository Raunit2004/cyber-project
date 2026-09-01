def test_login_page_renders(client):
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_register_page_renders(client):
    response = client.get('/auth/register')
    assert response.status_code == 200

def test_user_registration(client, app):
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to login or dashboard
    # Verify in DB
    from database.models import User
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'new@example.com'

def test_user_login_logout(client, init_database):
    # Test Login
    response = client.post('/auth/login', data={
        'identifier': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Test Logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
