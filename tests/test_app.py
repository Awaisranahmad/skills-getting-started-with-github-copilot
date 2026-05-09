import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# Preserve the initial state of activities so each test runs isolated
initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield

@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant(client):
    email = "teststudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_registration_returns_400(client):
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Club/signup?email=teststudent@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_student(client):
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_activity_returns_404(client):
    response = client.delete("/activities/Unknown%20Club/unregister?email=teststudent@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_registered_returns_400(client):
    email = "newstudent@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"
