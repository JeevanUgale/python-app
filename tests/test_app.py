import os
import tempfile
import pytest
from app import create_app
from models import db as _db

@pytest.fixture
def app():
    os.environ['DB_HOST'] = '127.0.0.1'
    os.environ['DB_USER'] = 'root'
    os.environ['DB_PASS'] = ''
    os.environ['DB_NAME'] = 'test_users_db'
    app = create_app()
    app.config.update({'TESTING': True})
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    res = client.get('/')
    assert res.status_code == 200
