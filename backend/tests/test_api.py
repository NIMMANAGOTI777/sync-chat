import tempfile
from backend.app import create_app


def _create_client():
    db_file = tempfile.NamedTemporaryFile(delete=False)
    app = create_app({"TESTING": True, "DATABASE": db_file.name})
    return app.test_client()


def test_health():
    client = _create_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_login_and_profile_flow():
    client = _create_client()
    login = client.post(
        "/api/auth/login",
        json={"phone": "+911234567890", "firebaseUid": "uid-1", "displayName": "Test User"},
    )
    assert login.status_code == 200
    token = login.get_json()["sessionToken"]

    me = client.get("/api/profile", headers={"X-Session-Token": token})
    assert me.status_code == 200
    assert me.get_json()["phone"] == "+911234567890"
