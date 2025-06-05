import pandas as pd
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

RAW = Path(__file__).resolve().parents[2] / "data" / "plant_growth_data.csv"

CATEGORICAL = ["Soil_Type", "Water_Frequency", "Fertilizer_Type"]
NUMERIC     = ["Sunlight_Hours", "Temperature", "Humidity"]
TARGET      = "Growth_Milestone"

def load_raw() -> pd.DataFrame:
    return pd.read_csv(RAW)

def make_pipeline() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )

def train_test(df: pd.DataFrame, *, test_pct: float = 0.2, seed: int = 42):
    from sklearn.model_selection import train_test_split
    X = df.drop(TARGET, axis=1)
    y = df[TARGET]
    return train_test_split(X, y, test_size=test_pct, stratify=y, random_state=seed)
