"""Tests for the Mergington High School API backend."""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities state before and after each test."""
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant(client):
    new_email = "newstudent@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": new_email},
    )

    assert response.status_code == 200
    assert new_email in response.json()["message"]
    assert new_email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    existing_email = "michael@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_remove_participant_deletes_entry(client):
    email_to_remove = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email_to_remove},
    )

    assert response.status_code == 200
    assert email_to_remove not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "nonexistent@mergington.edu"},
    )

    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]
