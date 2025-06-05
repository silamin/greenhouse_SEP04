from joblib import load
from pathlib import Path
import pandas as pd

def test_prediction_shape():
    model = load(Path(__file__).parents[1] / "model.joblib")
    sample = pd.DataFrame([{
        "Soil_Type": "loam",
        "Sunlight_Hours": 6.0,
        "Water_Frequency": "weekly",
        "Fertilizer_Type": "organic",
        "Temperature": 24.0,
        "Humidity": 55.0,
    }])
    y = model.predict(sample)
    assert y.shape == (1,)
