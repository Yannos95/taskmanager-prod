import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from extensions import db
from models import User, Task
from datetime import date

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        with app.app_context():
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()
            
        return client

def register_user(client, username, password):
    return client.post(
        '/register',
        data={'username': username, 'password': password, 'confirm': password},
        follow_redirects=True
    )

def login_user(client, username, password):
    return client.post(
        '/login',
        data={'username': username, 'password': password},
        follow_redirects=True
    )

def test_register_and_login_flow(client, app):
    response = register_user(client, 'user_test_1', 'password123')
    assert b"Registration successful. Please log in." in response.data
    
    response = login_user(client, 'user_test_1', 'password123')
    assert b"Logged in successfully." in response.data
    
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200

def test_create_task_via_post(client, app):
    register_user(client, 'creator', 'pass')
    login_user(client, 'creator', 'pass')
    
    response = client.post(
        '/tasks/new',
        data={
            'title': 'Buy groceries',
            'description': 'Milk, bread, cheese',
            'due_date': str(date.today())
        },
        follow_redirects=True
    )
    assert b"Task created." in response.data
    assert b"Buy groceries" in response.data

def test_edit_task_flow(client, app):
    register_user(client, 'editor', 'pass')
    login_user(client, 'editor', 'pass')
    
    with app.app_context():
        user = User.query.filter_by(username='editor').first()
        task = Task(title="Task to Edit", user_id=user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    new_title = "Edited Task Title"
    response = client.post(
        f'/tasks/{task_id}/edit',
        data={
            'title': new_title,
            'description': 'Updated description',
            'due_date': '',
            'is_completed': 'on'
        },
        follow_redirects=True
    )
    assert b"Task updated." in response.data
    
    response = client.post(
        f'/tasks/{task_id}/toggle',
        follow_redirects=True
    )
    assert b"Task status updated." in response.data