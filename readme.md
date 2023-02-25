# What?
This project is my submission for the final task of Programmable Web Project
course at University of Oulu. If you are unfamiliar with the course, consider
this repository as a reference implementation for simplistic flask-to-redis
file storage API. Otherwise, read on.





# What to do first after cloning the repo?
Step I
* Make note that everything has been tested (only) in WSL.

Step II: install prequisites for python
* `/pwp$ pip install -r requirements.txt`

Step III: install redis
* `/pwp$ curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg`
* `/pwp$ echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list`
* `/pwp$ sudo apt-get update`
* `/pwp$ sudo apt-get install redis`

Step IV: run the project
* `/pwp$ sudo redis-server current_redis.conf # start redis backend`
* `/pwp$ python run.py # run the app itself`
* `/pwp$ sensible-browser http://127.0.0.1:8080/api/files # smoke test`

Step V: run the tests
* `/pwp$ python -m pytest -vv -s # Service must be running in background.`

Step VI: read the docs
* `/pwp$ cat readme.md # this file`
* `/pwp$ sensible-browser http://127.0.0.1:8080/ # more docs`





# How to housekeep when making changes?
Just let black format everything related to python:
* `/pwp$ black . --line-length 79`

Force free zombie ports in case of emergency:
* `/pwp$ lsof -nti:8080 | xargs kill -9`

Useful redis commands:
* `/pwp$ sudo redis-server current_redis.conf # with conf`
* `/pwp$ sudo service redis-server start # without conf`
* `/pwp$ sudo service redis-server stop # halt`

Creating more database bindings in redis:
* `/pwp$ code app/models.py`




# How to read snowflake IDs used as file identifiers?
Example: `ccfa29b9a0972f37-1745eec0568a8261-d925c3bee74746...99bef7cdeb98bab1`
* Part 1: `ccfa29b9a0972f37`
  * Is hashed server hostname identifier.
  * Sortable, but hides original names.
* Part 2: `1745eec0568a8261`
  * Is unix timestamp in nanoseconds.
  * Sortable chronologically.
  * datetime.datetime.fromtimestamp(0x1745eec0568a8261/10**9)
* Part 3: `d925c3bee74746b3b6f353253f004b7b2a6db94ce4114a1299bef7cdeb98bab1`
  * Impossible to guess random ID.
    * Like, assume quadrillion guessing attempts per second, from the big bang
      to this moment, and we have exhausted less than one octillionth of one
      nonillionth of the search space.
  * Not sortable.



# Todo?
In python:
* Replace stub functions in `permissions.py` with actual implementation.
* "personalinformation" field in redis is hard-coded to "Erkki Esimerkki".
* Add new tests when authprovider is well defined.

Architechture-wise:
* helpers.get_client() currently assumes localhost.
* helpers.get_server_address() currently assumes localhost.
* Test suites currently assume localhost.
* Deploy a WSGI like gunicorn to get flask to scale.
* Optionally deploy reverse proxy like nginx to allow for gunicorn to safely
  serve priviledged ports such as the http/https defaults 80 and 443.
  * It is not safe to run wsgi as root to serve priviledged ports.
  * It is not safe to serve on ip 0.0.0.0 with reverse proxy.
