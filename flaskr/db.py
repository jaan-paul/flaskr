from typing import *
import sqlite3
import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash


class _Users:
    _connection: sqlite3.Connection

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def exists_username(self, username: str) -> bool:
        """Check if there is a user with username in database."""
        row = self._connection.execute(
            "SELECT Id FROM Users WHERE Username = ?", (username,)
        ).fetchone()

        return row is not None

    def exists(self, username: str, password: str) -> bool:
        """ Checks whether there is a user with username and password in 
            database. The password passed should not be hashed.
        """
        row = self._connection.execute(
            "SELECT * FROM Users WHERE Username = ?", (username,)
        ).fetchone()
        pw_hash = row["PasswordHash"]

        if row is None or not check_password_hash(pw_hash, password):
            return False
        else:
            return True

    def select_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        row = self._connection.execute(
            "SELECT * FROM Users WHERE Id = ?", (user_id,)
        ).fetchone()

        return row

    def select_by_username(self, username: str) -> Optional[sqlite3.Row]:
        row = self._connection.execute(
            "SELECT * FROM Users WHERE Username = ?", (username,)
        ).fetchone()

        return row

    # QUESTION: We don't treat different char case in username differently?
    def insert(self, username: str, password: str) -> None:
        pw_hash = generate_password_hash(password)
        self._connection.execute(
            "INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)",
            (username, pw_hash),
        )
        self._connection.commit()


class _Posts:
    _connection: sqlite3.Connection

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection


class _Database:
    _connection: sqlite3.Connection
    users: _Users
    posts: _Posts

    def __init__(self):
        connection = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        connection.row_factory = sqlite3.Row

        self._connection = connection
        self.users = _Users(connection)
        self.posts = _Posts(connection)

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection

    def close(self) -> None:
        self._connection.close()


def init_app(app: Flask) -> None:
    app.cli.add_command(_init_db_command)
    app.teardown_appcontext(_close_db)


@click.command("init-db")
@with_appcontext
def _init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo(f"Database {current_app.config['DATABASE']} initialized.")


def init_db() -> None:
    connection = get_db().connection
    with current_app.open_resource("schema.sql") as f:
        connection.executescript(f.read().decode("utf8"))


def _close_db(_) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_db() -> _Database:
    if "db" not in g:
        g.db = _Database()

    return g.db

