import pytest
from flaskr.db import get_db
from flask import Flask
from http import HTTPStatus
from flask.testing import FlaskClient
from .conftest import AuthActions


def test_index(client: FlaskClient, auth: AuthActions):
    data = client.get("/").data
    assert b"Log In" in data
    assert b"Register" in data


def test_index_while_logged_in(client: FlaskClient, auth: AuthActions):
    auth.login("test", "test")

    data = client.get("/").data
    assert b"Log Out" in data
    assert b"Test Title" in data
    assert b"by test on 2018-01-01" in data
    assert b"Test\nbody." in data
    assert b'href="/1/update' in data


@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required_on_post_mutation(client: FlaskClient, path: str):
    response = client.post(path)

    assert response.headers["Location"] == "http://localhost/auth/login"


def test_author_can_only_mutate_own_post(
    app: Flask, client: FlaskClient, auth: AuthActions
):
    # Reassign dummy post.
    with app.app_context():
        connection = get_db().connection
        connection.execute("UPDATE Posts SET AuthorId = 2 WHERE Id = 1")
        connection.commit()

    auth.login("test", "test")

    # Current user is not allowed to modify other user's post.
    assert client.post("/1/update").status_code == HTTPStatus.FORBIDDEN
    assert client.post("/1/delete").status_code == HTTPStatus.FORBIDDEN

    # Current user should not see edit link.
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
def test_post_mutation_only_available_for_existing_post(
    client: FlaskClient, auth: AuthActions, path: str
):
    auth.login("test", "test")

    assert client.post(path).status_code == HTTPStatus.NOT_FOUND


def test_post_creation(client: FlaskClient, auth: AuthActions, app: Flask):
    auth.login("test", "test")

    assert client.get("/create").status_code == HTTPStatus.OK

    client.post("/create", data={"title": "created", "body": ""})
    with app.app_context():
        connection = get_db().connection
        count = connection.execute("SELECT COUNT(Id) FROM Posts").fetchone()[0]
        assert count == 2


def test_post_update(client: FlaskClient, auth: AuthActions, app: Flask):
    auth.login("test", "test")

    assert client.get("/1/update").status_code == HTTPStatus.OK

    client.post("/1/update", data={"title": "updated", "body": ""})
    with app.app_context():
        connection = get_db().connection
        post = connection.execute("SELECT * FROM Posts WHERE Id = 1").fetchone()
        assert post["Title"] == "updated"


@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_post_creation_or_update_requiring_title(
    client: FlaskClient, auth: AuthActions, path: str
):
    auth.login("test", "test")

    response = client.post(path, data={"title": "", "body": "Some content."})
    assert b"Title is required." in response.data


def test_post_deletion(client: FlaskClient, auth: AuthActions, app: Flask):
    auth.login("test", "test")

    response = client.post("/1/delete")
    assert response.headers["Location"] == "http://localhost/"

    with app.app_context():
        connection = get_db().connection
        post = connection.execute("SELECT * FROM Posts WHERE Id = 1").fetchone()
        assert post is None
