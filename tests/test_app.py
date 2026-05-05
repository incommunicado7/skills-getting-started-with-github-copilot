import copy
from urllib.parse import quote

from fastapi.testclient import TestClient
import pytest

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index():
    with TestClient(app) as client:
        response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_dictionary():
    with TestClient(app) as client:
        response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_post_signup_adds_new_participant():
    email = "newstudent@mergington.edu"
    activity_name = quote("Chess Club", safe="")
    with TestClient(app) as client:
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Signed up {email} for Chess Club"


def test_post_signup_duplicate_returns_400():
    email = "michael@mergington.edu"
    activity_name = quote("Chess Club", safe="")
    with TestClient(app) as client:
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_delete_signup_removes_participant():
    email = "olivia@mergington.edu"
    activity_name = quote("Gym Class", safe="")
    with TestClient(app) as client:
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert email not in activities["Gym Class"]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from Gym Class"


def test_delete_signup_missing_returns_400():
    email = "missingstudent@mergington.edu"
    activity_name = quote("Gym Class", safe="")
    with TestClient(app) as client:
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()
