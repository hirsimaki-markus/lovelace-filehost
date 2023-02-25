#!/usr/bin/env python3

"""GET and POST for /api/files/<dbname>/<fileid>/"""


from flask import jsonify, make_response, request
from .helpers import get_client
from .helpers import get_base_response
from .routes import files
from .permissions import get_permission_for_route_thats_a_file_in_db
from .permissions import (
    get_yes_or_no_from_auth_provider_with_permission_object_and_token,
)


@files.route("/<dbname>/<fileid>/", methods=["GET"])
def files_dbname_fileid_get(dbname, fileid):
    """Allows client to download file."""
    # Authorization check beging.
    permission_object = get_permission_for_route_thats_a_file_in_db(
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

    try:
        client = get_client(dbname)
    except ValueError:
        ret = get_base_response(
            data=[], error=f"Invalid database name {repr(dbname)}."
        )
        return jsonify(ret), 404
    if not client.exists(fileid):
        ret = get_base_response(
            data=[], error=f"Invalid filename {repr(fileid)}."
        )
        return jsonify(ret), 404

    filedata = client.hget(fileid, "filedata")
    filename = client.hget(fileid, "filename")
    response = make_response(filedata)
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename={filename.decode()}"
    return response


@files.route("/<dbname>/<fileid>/", methods=["POST"])
def files_dbname_fileid_post(dbname, fileid):
    """Allways returns error. Modifying files is not allowed."""
    # Authorization check beging.
    permission_object = get_permission_for_route_thats_a_file_in_db(
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
        data=[], error="Modifying this file is not allowed through this API."
    )
    return jsonify(ret), 403
