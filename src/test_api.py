from fastapi.testclient import TestClient

from app import app, activities

client = TestClient(app)


def test_unregister_and_signup_cycle():
    activity_name = "Tennis Club"
    email = "teststudent@mergington.edu"

    # make sure participant isn't already registered
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # sign up the student
    resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity_name]["participants"]

    # unregister the student
    resp = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in activities[activity_name]["participants"]

    # unregistering again should return 400
    resp = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert resp.status_code == 400


def test_unregister_invalid_activity():
    resp = client.delete("/activities/Nonexistent/unregister?email=foo@bar.com")
    assert resp.status_code == 404
