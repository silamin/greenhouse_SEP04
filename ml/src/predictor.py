from .model_loader import load_model

def should_activate_pump(sensor_data: dict) -> bool:
    """
    Given a dict of sensor readings, return True if the pump should
    be activated, False otherwise. Assumes the loaded model’s predict()
    returns 0 or 1 (0 = no, 1 = yes).
    """
    model = load_model()
    # The model expects features in this exact order:
    features = [
        sensor_data.get("temperature"),
        sensor_data.get("humidity"),
        sensor_data.get("soil_moisture")
    ]
    prediction = model.predict([features])
    return bool(prediction[0])
