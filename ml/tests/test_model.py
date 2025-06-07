import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_predict_endpoint(monkeypatch):
    # 1. Monkey-patch get_sensor_data to avoid real HTTP calls
    def fake_get_sensor_data():
        return {"temperature": 20.0, "humidity": 50.0, "soil_moisture": 30.0}
    monkeypatch.setattr("app.main.get_sensor_data", fake_get_sensor_data)

    # 2. Monkey-patch should_activate_pump to return True
    monkeypatch.setattr("app.main.should_activate_pump", lambda data: True)

    # 3. Call the /predict endpoint
    response = client.get("/predict")
    assert response.status_code == 200

    json_data = response.json()
    assert isinstance(json_data, dict)
    assert "activate_pump" in json_data
    assert isinstance(json_data["activate_pump"], bool)
    assert json_data["activate_pump"] is True
