def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'CyberShield' in response.data

def test_dashboard_page(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Total Scans' in response.data

def test_history_page_unauthenticated(client):
    response = client.get('/history')
    # Should redirect to login
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

def test_history_page_authenticated(client, init_database):
    client.post('/auth/login', data={'identifier': 'testuser', 'password': 'testpass'})
    response = client.get('/history')
    assert response.status_code == 200
    assert b'Scan History' in response.data or b'CyberShield' in response.data
