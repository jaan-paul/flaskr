from typing import *
import os
import tempfile
import pytest
from flask import Flask, Response
from flask.testing import FlaskClient, FlaskCliRunner
from flaskr import create_app
from flaskr.db import get_db, init_db

# If a callable is a generator, pytest treats the first yield as the fixture
# value handed to tests and appropriately continues running it for teardown.
@pytest.fixture
def app() -> Iterable[Flask]:
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(test_config={"TESTING": True, "DATABASE": db_path})

    with app.app_context():
        init_db()
        get_db().connection.executescript(_read_data_sql())  # insert dummy data

    yield app

    os.close(db_fd)
    os.unlink(db_path)  # delete db file


def _read_data_sql() -> str:
    with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
        return f.read().decode("utf8")


# Fixtures can depend on other fixtures! Fixtures are injected (passed,
# dependency injection!) to tests with arguments having the same name as the
# fixture registered with pytest.fixture decorator.
@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def cli(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


class AuthActions:
    _client: FlaskClient

    def __init__(self, client: FlaskClient):
        self._client = client

    def login(self, username: str, password: str) -> Response:
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self) -> Response:
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    return AuthActions(client)
