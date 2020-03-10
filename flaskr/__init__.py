from typing import *
import os
from flask import Flask
from . import db
from . import auth
from . import blog


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

    # Ensure instance path is created.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(auth.blueprint)

    app.register_blueprint(blog.blueprint)
    # Associate 'index' route to '/'. So whenever url_for is given 'index', it
    # refers to 'blog.index', which blog.blueprint, we've given a root relative
    # to '/'.
    app.add_url_rule("/", endpoint="index")

    return app

