"""Lab 7 - Natalio Hassoun: database and Flask API tests using pytest fixtures."""

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

import database
from app import app


PROJECT_ROOT = Path(__file__).resolve().parent
EXPECTED_INITIAL_USERS = [
    {
        "user_id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "067765434567",
        "address": "John Doe Street, Innsbruck",
        "country": "Austria",
    }
]


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    """Give every test a fresh SQLite file without changing the app database."""
    path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DATABASE", path)
    database.create_db_table()
    return path


@pytest.fixture
def client():
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def user_data():
    return {
        "name": "Alice Test",
        "email": "alice@example.com",
        "phone": "03123456",
        "address": "Hamra, Beirut",
        "country": "Lebanon",
    }


@pytest.fixture
def saved_user(user_data):
    return database.insert_user(user_data)


def start_app_database(path):
    """Import the actual app in a new process, as happens on a fresh launch."""
    environment = os.environ.copy()
    environment["LAB5_DATABASE"] = str(path)
    result = subprocess.run(
        [sys.executable, "-c",
         "import json; import app; import database; print(json.dumps(database.get_users()))"],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    return json.loads(result.stdout)


def test_database_created_with_initial_users_on_first_app_run(tmp_path):
    path = tmp_path / "first-run.db"
    assert not path.exists()

    assert start_app_database(path) == EXPECTED_INITIAL_USERS
    assert path.is_file()
    with sqlite3.connect(path) as connection:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(users)")]
        assert columns == ["user_id", "name", "email", "phone", "address", "country"]


def test_app_restart_preserves_users_without_duplicate_seeds(tmp_path, monkeypatch):
    path = tmp_path / "restart.db"
    assert start_app_database(path) == EXPECTED_INITIAL_USERS
    monkeypatch.setattr(database, "DATABASE", path)
    changed = dict(EXPECTED_INITIAL_USERS[0], country="Lebanon")
    database.update_user(changed)

    assert start_app_database(path) == [changed]
    assert database.delete_user(1) is True
    assert start_app_database(path) == []


def test_insert_user(user_data):
    inserted = database.insert_user(user_data)

    assert type(inserted["user_id"]) is int
    assert inserted["user_id"] > 0
    assert inserted == dict(user_data, user_id=inserted["user_id"])
    assert database.get_user_by_id(inserted["user_id"]) == inserted


def test_get_users_returns_all_users_in_id_order(saved_user, user_data):
    second = database.insert_user(dict(user_data, name="Bob Test", email="bob@example.com"))

    assert database.get_users() == [saved_user, second]


def test_get_users_returns_empty_list_for_empty_database():
    assert database.get_users() == []


def test_get_users_by_id(saved_user):
    assert database.get_user_by_id(saved_user["user_id"]) == saved_user


def test_get_users_by_id_returns_none_for_missing_user():
    assert database.get_user_by_id(999) is None


def test_update_user(saved_user):
    changes = dict(saved_user, name="Updated Name", email="updated@example.com",
                   phone="03987654", address="Byblos", country="Canada")

    assert database.update_user(changes) == changes
    assert database.get_user_by_id(saved_user["user_id"]) == changes


def test_update_missing_user_does_not_insert(user_data):
    assert database.update_user(dict(user_data, user_id=999)) is None
    assert database.get_users() == []


def test_delete_user_removes_only_requested_record(saved_user, user_data):
    other = database.insert_user(dict(user_data, name="Other User"))

    assert database.delete_user(saved_user["user_id"]) is True
    assert database.get_user_by_id(saved_user["user_id"]) is None
    assert database.get_users() == [other]


def test_delete_missing_user_returns_false(saved_user):
    assert database.delete_user(999) is False
    assert database.get_users() == [saved_user]


def test_api_get_users(client, saved_user):
    response = client.get("/api/users")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == [saved_user]


def test_api_get_user(client, saved_user):
    response = client.get(f"/api/users/{saved_user['user_id']}")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == saved_user


def test_api_get_missing_user(client):
    response = client.get("/api/users/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}


def test_api_add_user(client, user_data):
    response = client.post("/api/users/add", json=user_data)

    assert response.status_code == 201
    assert response.is_json
    created = response.get_json()
    assert type(created["user_id"]) is int
    assert created["user_id"] > 0
    assert created == dict(user_data, user_id=created["user_id"])
    assert database.get_user_by_id(created["user_id"]) == created
    downloaded = client.get(f"/api/users/{created['user_id']}")
    assert downloaded.status_code == 200
    assert downloaded.get_json() == created


@pytest.mark.parametrize("invalid_body", [{}, [], {"name": "Only Name"}])
def test_api_add_invalid_user(client, invalid_body):
    response = client.post("/api/users/add", json=invalid_body)

    assert response.status_code == 400
    assert isinstance(response.get_json()["error"], str)
    assert database.get_users() == []


def test_api_update_user(client, saved_user):
    changes = dict(saved_user, name="Updated API Name", email="new@example.com",
                   phone="01234567", address="Tripoli", country="France")
    response = client.put("/api/users/update", json=changes)

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == changes
    assert database.get_user_by_id(saved_user["user_id"]) == changes
    downloaded = client.get(f"/api/users/{saved_user['user_id']}")
    assert downloaded.status_code == 200
    assert downloaded.get_json() == changes


def test_api_update_missing_user(client, user_data):
    response = client.put("/api/users/update", json=dict(user_data, user_id=999))

    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}
    assert database.get_users() == []


@pytest.mark.parametrize("invalid_id", [True, -1, "1"])
def test_api_update_invalid_id_preserves_record(client, saved_user, invalid_id):
    changes = dict(saved_user, user_id=invalid_id, name="Should Not Change")
    response = client.put("/api/users/update", json=changes)

    assert response.status_code == 400
    assert response.get_json() == {"error": "user_id must be a positive integer"}
    assert database.get_user_by_id(saved_user["user_id"]) == saved_user


def test_api_delete_user(client, saved_user, user_data):
    other = database.insert_user(dict(user_data, name="Keep This User"))
    response = client.delete(f"/api/users/delete/{saved_user['user_id']}")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"status": "User deleted successfully"}
    assert database.get_user_by_id(saved_user["user_id"]) is None
    missing = client.get(f"/api/users/{saved_user['user_id']}")
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "User not found"}
    assert database.get_users() == [other]


def test_api_delete_missing_user(client, saved_user):
    response = client.delete("/api/users/delete/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}
    assert database.get_users() == [saved_user]
