import asyncio
import copy

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
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_available_activities():
    # Arrange
    activity_name = "Chess Club"
    expected_participant = "michael@mergington.edu"

    # Act
    response = make_request("GET", "/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert activity_name in data
    assert data[activity_name]["max_participants"] == 12
    assert expected_participant in data[activity_name]["participants"]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    expected_message = f"Signed up {email} for {activity_name}"

    # Act
    response = make_request(
        "POST",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == expected_message
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_email():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    make_request(
        "POST",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    response = make_request(
        "POST",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity():
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = make_request(
        "POST",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_for_activity_removes_participant():
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


def test_unregister_rejects_unknown_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "unknown@mergington.edu"

    # Act
    response = make_request(
        "DELETE",
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not found in this activity"
