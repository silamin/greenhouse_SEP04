def _login(client):
    res = client.post("/auth/token", json={"username": "admin", "password": "secret"})
    assert res.status_code == 200
    return res.json()["access_token"]


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Auth flow
# ---------------------------------------------------------------------------
def test_login_and_logout_flow(client, admin_user):
    token = _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # logout
    logout = client.post("/auth/logout", headers=headers)
    assert logout.status_code == 200
    assert "logged out" in logout.json()["message"]

    # token should now be rejected
    res = client.get("/sensors/", headers=headers)
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Sensors
# ---------------------------------------------------------------------------
def test_sensor_crud(client, admin_user):
    token = _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "temp": 23.3,
        "hum": 55,
        "soil": 250,
        "light": 500,
        "dist": 10,
        "motion": False,
        "acc_x": 0,
        "acc_y": 0,
        "acc_z": 0,
    }

    created = client.post("/sensors/", json=payload, headers=headers)
    assert created.status_code == 201
    sensor = created.json()
    assert sensor["id"] is not None

    # list
    res = client.get("/sensors/", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
def test_settings_read_write(client, admin_user):
    token = _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    config = {
        "name": "Main GH",
        "temp_min": 18,
        "temp_max": 28,
        "light_min": 300,
        "light_max": 700,
        "hum_min": 40,
        "hum_max": 60,
        "soil_min": 200,
    }

    save = client.post("/settings/", json=config, headers=headers)
    assert save.status_code == 200
    data = save.json()
    assert data["owner"] == "admin"
    assert data["temp_max"] == 28

    # fetch
    get = client.get("/settings/", headers=headers)
    assert get.status_code == 200
    assert get.json()["name"] == "Main GH"
