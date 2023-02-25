#!/usr/bin/env python3

"""This is NOT the entrypoint. Check run.py instead.

* Start the redis backend '/pwp$ sudo redis-server current_redis.conf'
* Use '/pwp$ python run.py to start the app.
* Check out 'http://127.0.0.1:8080/'
"""

from flask import Flask
from .routes import root
from .helpers import get_valid_database_name, get_client
import redis


def create_app():
    """Construct the flask app and return it. Also checks Redis connection."""
    try:
        get_client(get_valid_database_name()).ping()
    except redis.exceptions.ConnectionError:
        msg = (
            "Can't connect to Redis. Aborting. Try doing: "
            "'/pwp$ sudo redis-server current_redis.conf'"
        )
        raise RuntimeError(msg) from None
    app = Flask(__name__, static_folder=None)
    app.register_blueprint(root)
    return app
