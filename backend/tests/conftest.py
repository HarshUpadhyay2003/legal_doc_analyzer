import pytest
import os
import sys
import tempfile
import shutil

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import init_db

@pytest.fixture(scope='session')
def app():
    # Create a temporary directory for the test database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    # Create test app with temporary database
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'JWT_SECRET_KEY': 'test-secret-key'  # Add JWT secret key for testing
    })
    
    # Initialize test database
    with app.app_context():
        init_db()
    
    yield app
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def auth_headers(client):
    # Register a test user
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 201
    
    # Login to get token
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    token = response.json['access_token']
    
    return {'Authorization': f'Bearer {token}'}