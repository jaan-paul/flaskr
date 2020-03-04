from typing import *
import os
from flask import Flask
from . import db
from . import auth


def create_app(test_config=None) -> Flask:
    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    # Load the instance config, if it exists, when not testing.
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    # Load the test config passed in.
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def home() -> str:
        return "Henlo world!"

    db.init_app(app)

    app.register_blueprint(auth.blueprint)

    return app

