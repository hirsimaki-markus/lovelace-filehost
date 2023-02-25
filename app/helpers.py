#!/usr/bin/env python3

from flask import request, Response
from random import choice
from .models import DBNAMES, DBNAME_TO_DBID
import redis
from typing import List
from flask import current_app as app
from textwrap import dedent


def clear_personal_information(dbname, fileid):
    """Clears personal information from a file in db."""
    client = get_client(dbname)
    if client.exists(fileid):
        client.hmset(fileid, "persnalinformation", "")


def get_client(dbname):
    """Returns a valid client based on dbname"""
    if dbname not in DBNAMES:
        raise ValueError("Invalid dbname provided.")
    return redis.StrictRedis(
        host="localhost", port=6379, db=DBNAME_TO_DBID[dbname]
    )


def get_server_address():
    return "http://127.0.0.1:8080"


def get_sitemap():
    """Returns simple sitemap information and tl;dr info about api."""
    generic_routes = sorted(
        list(set([str(rule) for rule in app.url_map.iter_rules()]))
    )
    cooked_generic_routes = "\n"
    for route in generic_routes:
        cooked_generic_routes += f"      * {route}\n"

    cooked_dbnames = "\n"
    for dbname in DBNAMES:
        cooked_dbnames += f"      * {dbname}\n"

    file_listing = "\n"
    for dbname in DBNAMES:
        file_listing += f"      * {request.base_url}api/files/{dbname}/\n"

    info = dedent(
        f"""
    --------------------------[ tl;dr documentation ]--------------------------
    About api endpoints (HATEOAS):
      * All /api/files/ endpoints respond to GET/POST with hypermedia controls.
      * Only /api/files/<dbname>/<fileid>/ will send file on GET request.
      * Only /api/files/<dbname>/ will not return error on POST request.

    About other pages (Other):
      * Root responds with readme on GET. Use POST to use admin tools.

    Metadata formats:
      * {{"filename": "asd.py", "idtype": "snowflake"}}
      * {{"filename": "asd.py", "idtype": "custom", "customid": "myname"}}

      POSTing a file requires http header-field called "metadata". The value
      of this field should be json object serialized to string. All keys and
      values should be strings in the json.



    ---------------------------[ condensed sitemap ]---------------------------
    Active routes:{cooked_generic_routes}
    Active dbnames:{cooked_dbnames}
    File listing per db:{file_listing}



    -----------------------[ permission objects scheme ]-----------------------
    This service is designed to perform permission checks against an
    "authprovider" service.

    What is expected from permission objects:
      * They are json objects.
      * They can be serialized to strings that fit in http header called
        "authprovidertoken".
      * The implementation details of permission objects are left open.
        * What permission objects could contain: a description of the
          attempted action, related context, and overrides based on aspects
          such as group.
      * Permission objects are an abstraction. A given service, such as this,
        has to decide how it associates permission objects with the resources
        it owns.
      * A permission object can be associated with any given action in any
        context. Such as: opening a door number 420 at Valkea during night when
        there is a fire in the building. The imaginary service dealing with
        opening doors at Valkea would generate/produce/fetch/read/infer the
        relevant permission object associated with the action. The permission
        object and a token identifying the user are sent to authprovider who
        will then decide if the action is allowed or not.
      * When permission object is combined with given "authprovidertoken" by
        authprovider the authprovider service is able to respond with
        allow/disallow.

    How this file storage service associates permission objects with itself:
      * Every combination of http method, such as GET, and a particular
        URL can be used to form a permission object that describes the
        priviledges needed to perform the action. An Example: GET /api/files/.
        Individual files are also acceptable URLs in this context.
      * This service makes no particular assumption about the contents of these
        objects except for the ones listed above. All functions related to
        dealing with permission objects are provided as stubs.

    What is expected from requests made to this service:
      * Each request contains a token associated with the end user.
        * The token is sent in an http header called "authprovidertoken"
      * The token is pseudonymous; only authprovider knows the following:
        * Who owns the token
        * What permissions this particular token grants

    What is expected from the authprovider service:
      * The service can be queried with a request containg:
        * The token that was used to attempt an action
        * The permission object that describes what is required to perform
          the attempted action.
        * When queried the authprovider responds with a binary answer; the
          action is allowed or disallowed.
    """[
            1:
        ]
    )

    return Response(info, mimetype="text/plain"), 200


def get_base_response(data, error=""):
    """
    Returns a base for hateoas compliant json.
    """

    # Collection is always hard coded to the relative parent. Getting the
    # collection is always safe, even for root; trailing "/" is still returned
    # if the split finds nothing else.
    return {
        "_links": {
            "request": {"href": request.path},
            "collection": {
                "href": f"{'/'.join(request.path.split('/')[:-2])}/"
            },
        },
        "data": data,
        "error": error,
    }


def get_invalid_database_name():
    """Get a redis db name that is quaranteened to not exist."""
    badname = ""
    while True:
        badname += choice("abcdefghijklmnopqrstuvwxyz")
        if badname not in DBNAMES:
            return badname


def get_valid_database_name():
    """Get a redis db name that is quaranteened to exist."""
    try:
        return list(DBNAMES)[0]
    except:
        raise RuntimeError(
            (
                "Smoke test failed: models.DBNAME_TO_DBID has zero bindings. "
                "Add a bind that connects redis database index such as db0 to "
                "a name. Example: DBNAME_TO_DBID = {'pythonfiles': 0}"
            )
        )
