from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # should be a dict mapping activity names to details
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # ensure email not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    before = resp.json()[activity]["participants"]
    assert email not in before

    # sign up
    url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    resp = client.post(url)
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # verify present
    resp = client.get("/activities")
    assert resp.status_code == 200
    after = resp.json()[activity]["participants"]
    assert email in after

    # unregister
    url = f"/activities/{quote(activity)}/unregister?email={quote(email)}"
    resp = client.delete(url)
    assert resp.status_code == 200
    assert f"Unregistered {email}" in resp.json().get("message", "")

    # verify removed
    resp = client.get("/activities")
    assert resp.status_code == 200
    final = resp.json()[activity]["participants"]
    assert email not in final


def test_signup_duplicate():
    activity = "Chess Club"
    # michael@mergington.edu is already in initial fixtures
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    resp = client.post(url)
    assert resp.status_code == 400
    assert resp.json().get("detail")


def test_unregister_not_found():
    activity = "Programming Class"
    email = "nonexistent@example.com"
    url = f"/activities/{quote(activity)}/unregister?email={quote(email)}"
    resp = client.delete(url)
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Participant not found"
