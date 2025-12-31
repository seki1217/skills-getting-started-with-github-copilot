"""
Tests for the Mergington High School API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
    })


def test_root_redirects(client):
    """Test that root redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data["Chess Club"]["participants"]) == 2


def test_signup_for_activity(client):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Basketball Team/signup?email=john@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up john@mergington.edu for Basketball Team" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "john@mergington.edu" in activities_data["Basketball Team"]["participants"]


def test_signup_duplicate(client):
    """Test that duplicate signup is rejected"""
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()


def test_signup_invalid_activity(client):
    """Test signing up for non-existent activity"""
    response = client.post(
        "/activities/NonExistent/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_from_activity(client):
    """Test unregistering from an activity"""
    response = client.delete(
        "/activities/Chess Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


def test_unregister_not_signed_up(client):
    """Test unregistering when not signed up"""
    response = client.delete(
        "/activities/Basketball Team/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"].lower()


def test_unregister_invalid_activity(client):
    """Test unregistering from non-existent activity"""
    response = client.delete(
        "/activities/NonExistent/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_full_workflow(client):
    """Test complete signup and unregister workflow"""
    # Sign up
    signup_response = client.post(
        "/activities/Basketball Team/signup?email=alice@mergington.edu"
    )
    assert signup_response.status_code == 200
    
    # Verify signup
    activities_response = client.get("/activities")
    assert "alice@mergington.edu" in activities_response.json()["Basketball Team"]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        "/activities/Basketball Team/unregister?email=alice@mergington.edu"
    )
    assert unregister_response.status_code == 200
    
    # Verify unregistration
    activities_response = client.get("/activities")
    assert "alice@mergington.edu" not in activities_response.json()["Basketball Team"]["participants"]
