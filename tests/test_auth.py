import pytest
from recipemod.repository import get_user_by_name


def test_register_new_user(client):
    data = {"username": "newuser", "password": "password123"}
    response = client.post("/auth/register", data=data)
    assert response.status_code == 302  # redirect to login page
    assert response.headers["Location"] == "/auth/login"

    # Check if user was created in the database
    from recipemod.repository import get_user_by_name

    with client.application.app_context():
        user = get_user_by_name("newuser")
    assert user is not None
    assert user.username == "newuser"
    assert user.password != "password123"  # password should be hashed


def test_register_duplicate_username(client):
    # Create a user with the same username
    data = {"username": "existinguser", "password": "password123"}
    client.post("/auth/register", data=data)

    # Try to register again with the same username
    data = {"username": "existinguser", "password": "password456"}
    response = client.post("/auth/register", data=data)
    assert response.status_code == 200  # error page
    assert f"User existinguser is already registered" in response.text


def test_register_missing_username(client):
    data = {"password": "password123"}
    response = client.post("/auth/register", data=data)
    assert response.status_code == 400  # error page from Flask
    assert "Error" in response.text


def test_register_missing_password(client):
    data = {"username": "newuser"}
    response = client.post("/auth/register", data=data)
    assert response.status_code == 400  # error page
    assert "Error" in response.text


def test_login_valid_credentials(client):
    # Create a user with valid credentials
    data = {"username": "existinguser", "password": "password123"}
    client.post("/auth/register", data=data)

    # Try to login with valid credentials
    data = {"username": "existinguser", "password": "password123"}
    response = client.post("/auth/login", data=data)
    assert response.status_code == 302  # redirect to index page
    assert response.headers["Location"] == "/"


def test_login_invalid_credentials(client):
    # Create a user with valid credentials
    data = {"username": "existinguser", "password": "password123"}
    client.post("/auth/register", data=data)

    # Try to login with invalid credentials
    data = {"username": "existinguser", "password": "wrongpassword"}
    response = client.post("/auth/login", data=data)
    assert response.status_code == 200  # error page
    assert "Incorrect password" in response.text


def test_login_missing_username(client):
    data = {"password": "password123"}
    response = client.post("/auth/login", data=data)
    assert response.status_code == 400  # error page
    assert "Error" in response.text


def test_login_missing_password(client):
    data = {"username": "existinguser"}
    response = client.post("/auth/login", data=data)
    assert response.status_code == 400  # error page
    assert "Error" in response.text


def test_login_user_not_found(client):
    data = {"username": "nonexistentuser", "password": "password123"}
    response = client.post("/auth/login", data=data)
    assert response.status_code == 200  # error page
    assert "User not found" in response.text


def test_login_user_session(client):
    # Create a user with valid credentials
    data = {"username": "existinguser", "password": "password123"}
    client.post("/auth/register", data=data)

    # Try to login with valid credentials
    data = {"username": "existinguser", "password": "password123"}
    response = client.post("/auth/login", data=data)

    # Check if user is logged in
    with client.application.app_context():
        user = get_user_by_name("existinguser")
        assert user.username == "existinguser"

    with client.session_transaction() as session:
        assert session["user_id"] == user.id
