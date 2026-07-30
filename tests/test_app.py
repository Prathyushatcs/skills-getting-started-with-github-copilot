import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from src.app import activities, app


def make_request(method: str, path: str, **kwargs):
    async def _request():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(_request())


@pytest.fixture(autouse=True)
def reset_activity_state():
    # Arrange
    original_participants = activities["Chess Club"]["participants"][:]
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    yield
    activities["Chess Club"]["participants"] = original_participants


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    expected_message = f"Removed {email} from {activity_name}"

    # Act
    response = make_request(
        "DELETE",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == expected_message
    assert email not in data["participants"]
