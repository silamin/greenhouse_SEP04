from joblib import dump
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report

from .features import load_raw, make_pipeline, train_test

ARTIFACT = Path(__file__).resolve().parents[2] / "model.joblib"

def main():
    df      = load_raw()
    X_tr, X_te, y_tr, y_te = train_test(df)
    pipe    = Pipeline([("prep", make_pipeline()),
                        ("clf", GradientBoostingClassifier(random_state=42))])
    pipe.fit(X_tr, y_tr)

    print("Accuracy:", accuracy_score(y_te, pipe.predict(X_te)))
    print(classification_report(y_te, pipe.predict(X_te)))

    dump(pipe, ARTIFACT)
    print("Saved", ARTIFACT)

if __name__ == "__main__":
    main()
