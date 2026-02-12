from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_upload_repo_invalid_url():
    response = client.post("/repo/upload", data={"repo_url": "https://example.com/not-github"})
    assert response.status_code == 400
    assert "Invalid GitHub repository URL" in response.json().get("detail", "")
