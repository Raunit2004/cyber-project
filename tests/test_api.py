import json

def test_scan_url_api(client):
    response = client.post('/api/scan/url', 
                           data=json.dumps({'url': 'https://example.com'}),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data
    assert 'url' in data
    assert 'is_malicious' in data
    assert data['url'] == 'https://example.com'

def test_scan_url_api_no_data(client):
    response = client.post('/api/scan/url', 
                           data=json.dumps({}),
                           content_type='application/json')
    assert response.status_code == 400

def test_scan_email_api(client):
    response = client.post('/api/scan/email', 
                           data=json.dumps({'text': 'Hello team, find the notes attached.'}),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data
    assert 'is_phishing' in data
    assert 'text_preview' in data

def test_scan_email_api_no_data(client):
    response = client.post('/api/scan/email', 
                           data=json.dumps({}),
                           content_type='application/json')
    assert response.status_code == 400

def test_stats_api(client):
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_scans' in data
    assert 'malicious' in data
    assert 'safe' in data

def test_history_api(client):
    response = client.get('/api/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
