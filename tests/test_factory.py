from flask.testing import FlaskClient
from flaskr import create_app


def test_app_testing_config() -> None:
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing

