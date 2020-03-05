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
            "INSERT INTO Users (Username, Password) VALUES (?, ?)",
            (username, pw_hash),
        )
        self._connection.commit()


class _Posts:
    _connection: sqlite3.Connection

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
