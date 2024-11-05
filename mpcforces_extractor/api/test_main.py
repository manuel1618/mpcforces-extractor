import os
from fastapi.testclient import TestClient
from mpcforces_extractor.api.main import app
from mpcforces_extractor.api.config import OUTPUT_FOLDER


class TestRoutesFileUpload:
    """
    Test the routes
    """

    def test_get_output_folder(self):
        """
        Test the get_output_folder endpoint
        """
        client = TestClient(app)
        response = client.get("api/v1/get-output-folder")
        assert response.status_code == 200
        assert response.json() == {"output_folder": str(OUTPUT_FOLDER)}
        actual_folder = os.getcwd() + "/data/output".replace("/", os.sep)
        assert response.json()["output_folder"] == actual_folder
