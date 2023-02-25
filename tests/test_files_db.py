#!/usr/bin/env python3

"""Test for GET and POST for /api/files/<dbname>/"""

import requests
from pathlib import Path
from json import dumps
from app.helpers import get_invalid_database_name, get_valid_database_name


class TestFilesDB:
    """Test routes in files_db.py"""

    @staticmethod
    def test_database_get_ok():
        """Get list of files in given database."""
        good_name = get_valid_database_name()
        endpoint = f"http://127.0.0.1:8080/api/files/{good_name}/"
        response = requests.get(endpoint)
        assert response.status_code == 200
        response_json = response.json()
        assert "_links" in response_json
        assert "data" in response_json
        assert "request" in response_json["_links"]
        assert response_json["error"] == ""

    @staticmethod
    def test_database_get_fail():
        """Fail to get list of files in invalid database name."""
        bad_name = get_invalid_database_name()
        endpoint = f"http://127.0.0.1:8080/api/files/{bad_name}/"
        response = requests.get(endpoint)
        assert response.status_code == 404
        assert response.json() == {
            "_links": {
                "request": {"href": f"/api/files/{bad_name}/"},
                "collection": {"href": f"/api/files/"},
            },
            "data": [],
            "error": f"Invalid database name {repr(bad_name)}.",
        }

    @staticmethod
    def test_database_post_ok_and_fail():
        """Posts file twice, first with random id. Then reposts by using the
        random id again. First post should ok and second should fail."""
        # First do the ok pos.
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

        # Do the failed post after ok post.
        snowflake_id = response_json["data"][0]
        metadata = dumps(
            {
                "filename": "hello_world.py",
                "idtype": "custom",
                "customid": snowflake_id,
            }
        )
        headers = {"metadata": metadata}
        response = requests.post(
            endpoint, headers=headers, data=filepath.open(mode="rb")
        )
        response_json = response.json()
        links = response_json["_links"]
        assert response_json["error"] == f"Can not overwrite {snowflake_id}"
        assert links["collection"]["href"] == "/api/files/"
        assert links["request"]["href"] == f"/api/files/{good_name}/"

    @staticmethod
    def test_database_post_bad_id():
        """Fail posting new file to database due to bad metadata."""
        good_name = get_valid_database_name()
        filepath = Path(__file__).parent / Path("sample_files/hello_world.py")
        endpoint = f"http://127.0.0.1:8080/api/files/{good_name}/"

        metadata = dumps({"filename": "hello_world.py"})
        headers = {"metadata": metadata}

        response = requests.post(
            endpoint, headers=headers, data=filepath.open(mode="rb")
        )

        assert response.json() == {
            "_links": {
                "collection": {"href": "/api/files/"},
                "request": {"href": "/api/files/pythonfiles/"},
            },
            "data": [],
            "error": ("Missing name in metadata header field: 'idtype'."),
        }
