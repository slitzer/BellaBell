from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_route_serves_html():
    response = client.get('/')

    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert 'BellaBell Dashboard' in response.text


def test_ui_static_assets_are_served():
    response = client.get('/ui/app.js')

    assert response.status_code == 200
    assert 'javascript' in response.headers['content-type']
    assert 'loadItems' in response.text
