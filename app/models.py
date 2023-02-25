#!/usr/bin/env python3

# Redis has 16 dbs by default. Add more bindings to this table as needed.
# Do not use "request" or "collection" as dbname. These are reserved by
# hypermedia controls. See GET http://127.0.0.1:8080/api/files/ for example.
DBNAME_TO_DBID = {
    "pythonfiles": 0,
    "hiddenfiles": 1,
    "examplefiles": 2,
}

# List valid named for convenience.
DBNAMES = list(DBNAME_TO_DBID.keys())
