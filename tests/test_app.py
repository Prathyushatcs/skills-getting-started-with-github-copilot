from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in data["participants"]

    # Restore state for later tests
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
