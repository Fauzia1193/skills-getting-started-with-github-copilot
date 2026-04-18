import pytest
from fastapi.testclient import TestClient
from src.app import app


def test_get_activities():
    """Test GET /activities returns activity data."""
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    # Check structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]

    # Verify participant was added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity_name]["participants"]


def test_signup_invalid_activity():
    """Test signup for non-existent activity returns 404."""
    # Arrange
    client = TestClient(app)
    invalid_activity = "NonExistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_signup_duplicate_email():
    """Test signing up the same email multiple times (current behavior allows duplicates)."""
    # Arrange
    client = TestClient(app)
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"

    # Act - First signup
    response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response1.status_code == 200

    # Act - Second signup (duplicate)
    response2 = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response2.status_code == 200  # Currently allows duplicates

    # Assert - Email appears twice
    response3 = client.get("/activities")
    data = response3.json()
    count = data[activity_name]["participants"].count(email)
    assert count == 2  # Note: This test reflects current buggy behavior; should be 1 after fix