#!/usr/bin/env python3

"""This IS the entrypoint.

* Start the redis backend '/pwp$ sudo redis-server current_redis.conf'
* Use '/pwp$ python run.py to start the app.
* Check out 'http://127.0.0.1:8080/'

This flask app provides file storage system by serving REST interface that
connects to the backend file storage, Redis.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8080")  # Can't use priviledged port 80.
