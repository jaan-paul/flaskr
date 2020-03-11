import pytest
from flask import Flask, session, g
from flask.testing import FlaskClient
from flaskr.db import get_db
from http import HTTPStatus
from .conftest import AuthActions


def test_registration(client: FlaskClient, app: Flask) -> None:
    assert client.get("/auth/register").status_code == HTTPStatus.OK

    response = client.post(
        "/auth/register", data={"username": "a", "password": "a"}
    )
    assert "http://localhost/auth/login" == response.headers["Location"]

    with app.app_context():
        assert get_db().users.select_by_username("a") is not None


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        ("test", "test", b"already registered."),
    ),
)
def test_registration_input_validation(
    client: FlaskClient, username: str, password: str, message: str
):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )

    assert message in response.data


def test_login(client: FlaskClient, auth: AuthActions):
    assert client.get("/auth/login").status_code == HTTPStatus.OK

    response = auth.login("test", "test")
    assert response.headers["Location"] == "http://localhost/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["Username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", b"Unknown username."),
        ("test", "a", b"Incorrect password."),
    ),
)
def test_login_input_validation(
    auth: AuthActions, username: str, password: str, message: str
):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client: FlaskClient, auth: AuthActions):
    auth.login("test", "test")

    with client:
        auth.logout()
        assert "user_id" not in session
