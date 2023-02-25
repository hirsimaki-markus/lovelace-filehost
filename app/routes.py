#!/usr/bin/env python3

"""Root of all routes. Blueprints go here. The GET/POST for root are
also stored here.
"""

from flask import Blueprint, jsonify, request
from .helpers import get_sitemap
import json
from .permissions import get_permission_for_route_that_is_not_a_file
from .permissions import (
    get_yes_or_no_from_auth_provider_with_permission_object_and_token,
)
from .helpers import clear_personal_information

# Using nested blueprints for modularity.
root = Blueprint("root", __name__)
api = Blueprint("api", __name__, url_prefix="/api")
files = Blueprint("files", __name__, url_prefix="/files")
root.register_blueprint(api)
api.register_blueprint(files)


@root.route("/", methods=["GET"])
def sitemap():
    return get_sitemap()


@root.route("/", methods=["POST"])
def admintools():
    """Admin stuff goes here. Currently only contains a method to null personal
    information from a file.

    Admin panel intentionally returns unhelpful information for those who are
    not in the know; the teapot responses are intended. HATEOAS is not followed
    here. So that brute-forcing knowledge about the endpoint is harder.

    The return values also intentionally mismatch status codes:
    "418 I'm a teapot {teapot_emoji}", 418 # unauthorized
    "200 I'm a teapot {teapot_emoji}", 418 # admin method ok
    "500 I'm a teapot {teapot_emoji}", 418 # admin method fail

    More detailed implementation is left for later date when admin tasks are
    more clearly defined and authprovider is actually able to verify such
    tasks.
    """
    teapot_emoji = b"\xf0\x9f\xab\x96".decode("utf-8")  # emojipedia.org/teapot

    permission_object = get_permission_for_route_that_is_not_a_file(
        request.path, request.url_rule
    )
    is_authorized = (
        get_yes_or_no_from_auth_provider_with_permission_object_and_token(
            permission_object, "token_from_http_header"
        )
    )
    if not is_authorized:
        return f"418 I'm a teapot {teapot_emoji}", 418
    try:
        metadata = json.loads(request.headers["metadata"])
        method = metadata["method"]
        args = metadata["args"]
    except:
        return f"418 I'm a teapot {teapot_emoji}", 418

    if method == "clear_personal_information":
        # args should be:
        # * dbname
        # * fileid
        try:
            clear_personal_information(*args)
            return f"200 I'm a teapot {teapot_emoji}", 418
        except:
            return f"500 I'm a teapot {teapot_emoji}", 418
    else:
        return f"418 I'm a teapot {teapot_emoji}", 418


# These imports do not SEEM to be used in this file but they ARE USED.
# These are required to trigger flask registration of routes.
from .files_db_fileid import files_dbname_fileid_get, files_dbname_fileid_post
from .files_db import files_dbname_get, files_dbname_post
from .files import files_get, files_post
