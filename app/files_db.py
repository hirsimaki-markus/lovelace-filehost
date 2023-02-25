#!/usr/bin/env python3

"""GET and POST for /api/files/<dbname>/"""

from flask import request, request, jsonify
from .models import DBNAMES
import json
from time import time_ns
from socket import gethostname
from uuid import uuid4
from hashlib import sha256
from .routes import files
from .helpers import get_base_response, get_client
from .permissions import (
    get_yes_or_no_from_auth_provider_with_permission_object_and_token,
    get_personal_information_when_saving_file_to_redis_database,
    get_permission_for_route_that_is_not_a_file,
    get_partial_permission_object_to_save_in_db,
)


@files.route("/<dbname>/", methods=["GET"])
def files_dbname_get(dbname):
    """Returns available fileids for valid database name."""
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

    if dbname not in DBNAMES:
        ret = get_base_response(
            data=[], error=f"Invalid database name {repr(dbname)}."
        )
        return jsonify(ret), 404
    else:
        client = get_client(dbname)
        ret = get_base_response(
            data=[fileid.decode() for fileid in client.keys()], error=""
        )
        ret["_links"].update(
            [
                (
                    fileid,
                    {
                        "href": f"/api/files/{dbname}/{fileid}",
                        "name": client.hget(fileid, "filename").decode(),
                    },
                )
                for fileid in [fileid.decode() for fileid in client.keys()]
            ]
        )
        return jsonify(ret), 200


@files.route("/<dbname>/", methods=["POST"])
def files_dbname_post(dbname):
    """Allows clients to upload files to database."""
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

    # Save timestamp and identifier before starting detailed handling.
    timestamp = time_ns()
    personalinfo = get_personal_information_when_saving_file_to_redis_database(
        "test", "test"
    )

    # Check for bad dbname
    if dbname not in DBNAMES:
        ret = get_base_response(
            data=[], error=f"Invalid database name {repr(dbname)}."
        )
        return jsonify(ret), 404

    # Try reading the upload.
    try:
        filedata = request.stream.read()
    except:  # Too many ways for streaming to blow up. use bare except.
        ret = get_base_response(data=[], error="Failed to read upload stream.")
        return jsonify(ret), 400

    # Unpack json from the custom "metadata" header.
    try:
        metadata = json.loads(request.headers["metadata"])
    except KeyError:  # from request.headers["metadata"].
        ret = get_base_response(
            data=[],
            error="Missing header field: 'metadata'.",
        )
        return jsonify(ret), 400
    except json.decoder.JSONDecodeError:  # from json.loads().
        ret = get_base_response(
            data=[], error="Json decoding failure in header-field 'metadata'."
        )
        return jsonify(ret), 400

    # Read relevant bits from the metadata header.
    try:
        filename = metadata["filename"]
    except KeyError:
        ret = get_base_response(
            data=[],
            error="Missing key in metadata header field: 'filename'.",
        )
        return jsonify(ret), 400
    try:
        metadata_idtype = metadata["idtype"]
    except KeyError:
        ret = get_base_response(
            data=[],
            error="Missing name in metadata header field: 'idtype'.",
        )
        return jsonify(ret), 400

    # Ensure that filename is valid
    try:
        # List of characters allowed by POSIX portable filename convention.
        allowed_chars = (
            ".-_0123456789"
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        assert type(filename) == str
        for c in filename:
            assert c in allowed_chars
    except AssertionError:
        ret = get_base_response(
            data=[],
            error=f"Invalid character in filename. Allowed: '{allowed_chars}'",
        )
        return jsonify(ret), 400

    # prepare "fileid" and "fileid_type" for saving in redis
    if metadata_idtype == "snowflake":
        # Using snowflake for fileid.
        host = sha256(bytes(gethostname(), "utf-8")).hexdigest()[:16]
        timestamp = hex(int(time_ns()))[2:]
        uuid4x2 = (str(uuid4()) + str(uuid4())).replace("-", "")
        fileid = f"{host}-{timestamp}-{uuid4x2}"
        fileid_type = "snowflake"
    elif metadata_idtype == "custom":
        # Using custom ID for fileid.
        try:
            metadata_customid = metadata["customid"]
        except KeyError:
            ret = get_base_response(
                data=[],
                error="Metadata missing 'customid' key for idtype 'custom'.",
            )
            return jsonify(ret), 400
        fileid = str(metadata_customid)
        if len(fileid) < 5:
            ret = get_base_response(
                data=[],
                error="Too short customid. Minimum size is 5.",
            )
            return jsonify(ret), 400
        fileid_type = "custom"
    else:
        ret = get_base_response(
            data=[],
            error="Bad idtype. Allowed: 'snowflake', 'custom'.",
        )
        return jsonify(ret), 400

    # All the necessary data is now available. Time to save file in redis.
    client = get_client(dbname)
    if client.exists(fileid):
        ret = get_base_response(
            data=[fileid], error=f"Can not overwrite {fileid}"
        )
        return jsonify(ret), 403
    hashmapdata = {
        "fileidtype": fileid_type,
        "filename": filename,
        "timestamp": timestamp,
        "filedata": filedata,
        "partialpermissionobject": get_partial_permission_object_to_save_in_db(
            "test", "test"
        ),
        "personalinformation": personalinfo,
    }
    client.hmset(
        fileid,
        hashmapdata,
    )
    ret = get_base_response(data=[fileid], error="")
    return jsonify(ret), 201
