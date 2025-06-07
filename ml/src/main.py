import os
from fastapi import FastAPI, HTTPException
from mangum import Mangum

from .data_fetcher import get_sensor_data
from .predictor   import should_activate_pump

app = FastAPI(title="Greenhouse Pump Predictor")

@app.on_event("startup")
def startup_event():
    """
    Preload the model into memory on cold start.
    Any errors here will cause the Lambda to fail early.
    """
    try:
        from .model_loader import load_model
        load_model()
    except Exception as e:
        print(f"Error loading model at startup: {e}")

@app.get("/predict")
def predict_pump():
    """
    1. Fetch latest sensor data from the greenhouse API.
    2. Use the ML model to decide if the pump should activate.
    3. Return {"activate_pump": true/false}.
    """
    try:
        sensor_data = get_sensor_data()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching sensor data: {e}")

    try:
        activate = should_activate_pump(sensor_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {e}")

    return {"activate_pump": activate}

# Handler for AWS Lambda (API Gateway / Lambda Function URL)
handler = Mangum(app)

def lambda_handler(event, context):
    """
    Direct Lambda entrypoint (e.g. EventBridge scheduled trigger).
    Returns a JSON dict with the prediction result. If an exception
    is raised, Lambda will record a failure.
    """
    try:
        sensor_data = get_sensor_data()
        activate = should_activate_pump(sensor_data)
        return {"activate_pump": activate}
    except Exception as e:
        raise e
