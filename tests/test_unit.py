import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta
from unittest.mock import patch
import pytest

from models import User, Task
from app import _build_postgres_uri

def test_task_is_overdue_true():
    yesterday = date.today() - timedelta(days=1)
    task = Task(title="Old Task", due_date=yesterday, is_completed=False)
    assert task.is_overdue() is True

def test_task_is_not_overdue_completed():
    yesterday = date.today() - timedelta(days=1)
    task = Task(title="Done Task", due_date=yesterday, is_completed=True)
    assert task.is_overdue() is False

def test_task_is_not_overdue_no_date():
    task = Task(title="No Due Date", due_date=None, is_completed=False)
    assert task.is_overdue() is False

def test_user_password_hashing():
    user = User(username="test_unit_user")
    raw_password = "secure_password_123"
    
    user.set_password(raw_password)
    
    assert user.check_password(raw_password) is True
    assert user.check_password("wrong_password") is False

@patch.dict(os.environ, {}, clear=True)
def test_build_postgres_uri_defaults():
    expected_uri = "postgresql+psycopg2://postgres:postgres@localhost:5432/taskmanager"
    assert _build_postgres_uri() == expected_uri

@patch.dict(os.environ, {
    "DATABASE_URL": "postgresql://external_db_url"
}, clear=True)
def test_build_postgres_uri_database_url_precedence():
    assert _build_postgres_uri() == "postgresql://external_db_url"