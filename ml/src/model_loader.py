import os
import joblib

# Default path; can be overridden via environment variable MODEL_PATH
MODEL_PATH = os.getenv("MODEL_PATH", "models/pump_model.joblib")

_model = None

def load_model():
    """
    Load (and cache) the ML model from disk.
    Returns a scikit-learn estimator (or similar) loaded via joblib.
    """
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model
