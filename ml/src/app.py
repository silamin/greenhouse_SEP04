from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load
from pathlib import Path
import pandas as pd

MODEL = load(Path(__file__).resolve().parents[2] / "model.joblib")

class SensorPayload(BaseModel):
    Soil_Type: str
    Sunlight_Hours: float
    Water_Frequency: str
    Fertilizer_Type: str
    Temperature: float
    Humidity: float

app = FastAPI(title="Plant-Growth Predictor")

@app.post("/predict")
def predict(p: SensorPayload):
    df = pd.DataFrame([p.model_dump()])
    pred = int(MODEL.predict(df)[0])
    return {"growth_milestone": pred}
