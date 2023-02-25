#!/usr/bin/env python3

"""Test for GET and POST for /api/files/"""

import requests
from pathlib import Path
from app.helpers import get_server_address


class TestFiles:
    """Test routes in files.py"""

    @staticmethod
    def test_files_get_ok():
        """Fetch list of endpoint names."""
        endpoint = f"{get_server_address()}/api/files/"
        response = requests.get(endpoint)
        assert response.status_code == 200
        response_json = response.json()
        assert "_links" in response_json
        assert "data" in response_json
        assert "request" in response_json["_links"]
        assert response_json["error"] == ""

    @staticmethod
    def test_files_post_fail():
        """Attempt to post, fail as expected."""
        filepath = Path(__file__).parent / Path("sample_files/hello_world.py")
        endpoint = f"{get_server_address()}/api/files/"
        response = requests.post(endpoint, filepath.open(mode="rb"))
        assert response.status_code == 403
        assert response.json() == {
            "_links": {
                "request": {"href": "/api/files/"},
                "collection": {"href": "/api/"},
            },
            "data": [],
            "error": "Creating new databases is not allowed through this API.",
        }
