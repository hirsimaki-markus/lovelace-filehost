#!/usr/bin/env python3

"""GET and POST for /api/files/"""

from flask import jsonify, url_for, request
from .models import DBNAMES
from .routes import files
from .helpers import get_base_response
from .permissions import get_permission_for_route_that_is_not_a_file
from .permissions import (
    get_yes_or_no_from_auth_provider_with_permission_object_and_token,
)


@files.route("/", methods=["GET"])
def files_get():
    """Returns available database names"""
    # Authorization check beging.
    permission_object = get_permission_for_route_that_is_not_a_file(
        request.path, request.url_rule
    )
    is_authorized = (
        get_yes_or_no_from_auth_provider_with_permission_object_and_token(
            permission_object, "token_from_http_header"
        )
    )
    if not is_authorized:
        ret = get_base_response(
            data=[], error="Token has insufficient permissions."
        )
        return jsonify(ret), 401
    # Authorization check end.

    ret = get_base_response(data=DBNAMES, error="")
    ret["_links"].update(
        [(dbname, {"href": f"/api/files/{dbname}/"}) for dbname in DBNAMES]
    )
    return jsonify(ret), 200


@files.route("/", methods=["POST"])
def files_post():
    """Returns 403 always; creating new databases is not allowed here."""
    # Authorization check beging.
    permission_object = get_permission_for_route_that_is_not_a_file(
        request.path, request.url_rule
    )
    is_authorized = (
        get_yes_or_no_from_auth_provider_with_permission_object_and_token(
            permission_object, "token_from_http_header"
        )
    )
    if not is_authorized:
        ret = get_base_response(
            data=[], error="Token has insufficient permissions."
        )
        return jsonify(ret), 401
    # Authorization check end.

    ret = get_base_response(
        data=[],
        error="Creating new databases is not allowed through this API.",
    )
    return jsonify(ret), 403
