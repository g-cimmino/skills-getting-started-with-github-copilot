import copy
import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app, activities

_original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_get_activities(client):
    # Act
    response = await client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


async def test_signup_for_activity(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = await client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


async def test_signup_duplicate(client):
    # Arrange
    email = "duplicate@mergington.edu"
    await client.post("/activities/Chess Club/signup", params={"email": email})

    # Act
    response = await client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400


async def test_signup_activity_not_found(client):
    # Act
    response = await client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404


async def test_unregister_from_activity(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = await client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


async def test_unregister_not_signed_up(client):
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = await client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404


async def test_unregister_activity_not_found(client):
    # Act
    response = await client.delete(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
