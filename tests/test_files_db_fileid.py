#!/usr/bin/env python3

"""Test for GET and POST for /api/files/<dbname>/<fileid>/"""

import requests
from pathlib import Path
from json import dumps
from app.helpers import get_valid_database_name


class TestFilesDBFile:
    """Test routes in files_db_file.py"""

    @staticmethod
    def test_file_get_ok():
        """Post file and then get it."""
        # First post file so we can get it
        good_name = get_valid_database_name()
        filepath = Path(__file__).parent / Path("sample_files/hello_world.py")
        endpoint = f"http://127.0.0.1:8080/api/files/{good_name}/"
        metadata = dumps({"filename": "hello_world.py", "idtype": "snowflake"})
        headers = {"metadata": metadata}
        response = requests.post(
            endpoint, headers=headers, data=filepath.open(mode="rb")
        )
        response_json = response.json()
        links = response_json["_links"]
        assert response_json["error"] == ""
        assert links["collection"]["href"] == "/api/files/"
        assert links["request"]["href"] == f"/api/files/{good_name}/"

        # File has been posted. we can now get it
        fileid = response_json["data"][0]
        endpoint = f"http://127.0.0.1:8080/api/files/{good_name}/{fileid}"
        response = requests.get(endpoint)
        assert response.text == filepath.read_text()

    @staticmethod
    def test_file_get_fail():
        """Fail getting nonexistent filename."""
        good_name = get_valid_database_name()
        badfilename = "a"  # Filename too short. will never exist.
        endpoint = f"http://127.0.0.1:8080/api/files/{good_name}/{badfilename}"
        response = requests.get(endpoint)
        response_json = response.json()
        assert response_json == {
            "_links": {
                "collection": {"href": "/api/files/pythonfiles/"},
                "request": {"href": "/api/files/pythonfiles/a/"},
            },
            "data": [],
            "error": "Invalid filename 'a'.",
        }
