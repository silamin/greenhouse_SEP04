import os
import requests

# Environment variables for authentication and API endpoint
GH_API_URL   = os.getenv("GH_API_URL", "https://api.my-greenhouse.com")
GH_API_USER  = os.getenv("GH_API_USER")
GH_API_PASS  = os.getenv("GH_API_PASSWORD")
GH_API_TOKEN = os.getenv("GH_API_TOKEN")

def get_sensor_data():
    """
    Fetch the latest sensor readings from the greenhouse API.
    Returns a dict with keys matching the model’s expected features, e.g.:
        {
            "temperature": float,
            "humidity": float,
            "soil_moisture": float
        }
    Assumes the greenhouse API has an endpoint GET {GH_API_URL}/sensors/latest
    that returns JSON fields “temp”, “hum”, and “soil”.
    """
    auth = None
    headers = {}

    if GH_API_TOKEN:
        headers["Authorization"] = f"Bearer {GH_API_TOKEN}"
    elif GH_API_USER and GH_API_PASS:
        auth = (GH_API_USER, GH_API_PASS)

    url = f"{GH_API_URL}/sensors/latest"
    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()
    data = response.json()

    return {
        "temperature": data.get("temp"),
        "humidity":    data.get("hum"),
        "soil_moisture": data.get("soil")
    }
