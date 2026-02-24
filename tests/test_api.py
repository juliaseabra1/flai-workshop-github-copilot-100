import os
import sys

# ensure that the src directory is on the import path so that we can import `app`
root = os.path.dirname(os.path.dirname(__file__))
src = os.path.join(root, "src")
if src not in sys.path:
    sys.path.insert(0, src)

from fastapi.testclient import TestClient

from app import app, activities

client = TestClient(app)


def _ensure_not_registered(activity_name: str, email: str):
    # helper to keep tests isolated
    if email in activities.get(activity_name, {}).get("participants", []):
        activities[activity_name]["participants"].remove(email)


def test_root_redirect():
    # root path should redirect to the static index
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities_returns_dict():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # at least some activities should be present
    assert "Tennis Club" in data
    assert "participants" in data["Tennis Club"]


def test_signup_and_unregister_cycle():
    activity_name = "Tennis Club"
    email = "pytest@example.com"

    # make sure participant isn't already registered
    _ensure_not_registered(activity_name, email)

    # sign up the student
    resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity_name]["participants"]

    # signing up again should return 400
    resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp.status_code == 400

    # unregister the student
    resp = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in activities[activity_name]["participants"]

    # unregistering again should return 400
    resp = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert resp.status_code == 400


def test_invalid_activity_errors():
    # signing up for non-existent activity
    resp = client.post("/activities/InvalidActivity/signup?email=test@foo.com")
    assert resp.status_code == 404

    resp = client.delete("/activities/InvalidActivity/unregister?email=test@foo.com")
    assert resp.status_code == 404


def test_signup_reflects_in_get():
    activity_name = "Basketball Team"
    email = "refresh2@mergington.edu"

    _ensure_not_registered(activity_name, email)

    resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp.status_code == 200

    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity_name]["participants"]

