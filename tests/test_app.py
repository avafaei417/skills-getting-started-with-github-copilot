import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Original activities data for resetting
ORIGINAL_ACTIVITIES = {
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
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Music Club": {
        "description": "Learn to play instruments and perform music",
        "schedule": "Wednesdays and Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["lisa@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art forms like painting and drawing",
        "schedule": "Mondays, 3:00 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["anna@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act in plays and improve public speaking",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["ben@mergington.edu"]
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 14,
        "participants": ["chris@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and learn about science",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 16,
        "participants": ["diana@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    from src.app import activities
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES.copy())

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 8  # Number of activities
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]

def test_signup_successful():
    """Test successful signup"""
    response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]

    # Verify the student was added
    response = client.get("/activities")
    activities = response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    """Test signing up for an activity twice"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    
    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for a nonexistent activity"""
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_successful():
    """Test successful unregistration"""
    # First signup
    client.post("/activities/Programming%20Class/signup?email=removeme@mergington.edu")
    
    # Then unregister
    response = client.delete("/activities/Programming%20Class/signup?email=removeme@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered removeme@mergington.edu from Programming Class" in data["message"]

    # Verify the student was removed
    response = client.get("/activities")
    activities = response.json()
    assert "removeme@mergington.edu" not in activities["Programming Class"]["participants"]

def test_unregister_not_signed_up():
    """Test unregistering a student who is not signed up"""
    response = client.delete("/activities/Chess%20Club/signup?email=notsignedup@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up" in data["detail"]

def test_unregister_nonexistent_activity():
    """Test unregistering from a nonexistent activity"""
    response = client.delete("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    """Test root endpoint redirects to static index"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]