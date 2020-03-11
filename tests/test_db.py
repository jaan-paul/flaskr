import sqlite3
import pytest
from flask import Flask
from flask.testing import FlaskCliRunner
from flaskr.db import get_db


def test_get_db_caching(app: Flask) -> None:
    with app.app_context():
        db = get_db()
        assert db is get_db()


def test_db_closed_on_app_context_exit(app: Flask) -> None:
    with app.app_context():
        connection = get_db().connection

    with pytest.raises(sqlite3.ProgrammingError) as err_info:
        connection.execute("SELECT 1")

    assert "closed" in str(err_info.value)


def test_init_db_command_called_in_cli(
    cli: FlaskCliRunner, monkeypatch
) -> None:
    is_db_initialized = False

    def fake_init_db() -> None:
        nonlocal is_db_initialized
        is_db_initialized = True

    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = cli.invoke(args="init-db")

    assert "initialized" in result.output
    assert is_db_initialized
