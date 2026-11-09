from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .validation import FEATURES

THRESHOLD = 0.40
MODEL_PATH = Path(__file__).resolve().parent.parent / "Churn_predict.pkl"


class ModelService:
    def __init__(self, path: Path = MODEL_PATH):
        self.path = path
        self.model: Any = None

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def load(self) -> None:
        if not self.path.is_file():
            raise FileNotFoundError(f"Required trained model was not found: {self.path}")
        self.model = joblib.load(self.path)
        classes = list(getattr(self.model, "classes_", []))
        if "Yes" not in classes:
            self.model = None
            raise ValueError(f"Model must expose positive class 'Yes'; found classes {classes}")
        if hasattr(self.model, "feature_names_in_"):
            expected = list(self.model.feature_names_in_)
            if len(expected) != len(FEATURES) or set(expected) != set(FEATURES):
                self.model = None
                raise ValueError(f"Model feature names do not match required schema. Found: {expected}")

    def predict(self, data: pd.DataFrame) -> list[dict[str, Any]]:
        if not self.loaded: raise RuntimeError("The trained model is not loaded.")
        classes = list(self.model.classes_)
        yes_index = classes.index("Yes")
        # The supplied artifact records its trained input order in feature_names_in_.
        # Reindex by those names; the public input schema remains the documented 19 fields.
        model_features = list(getattr(self.model, "feature_names_in_", FEATURES))
        probabilities = self.model.predict_proba(data.loc[:, model_features])[:, yes_index]
        if not np.isfinite(probabilities).all(): raise RuntimeError("Model returned a non-finite probability.")
        output = []
        for p in probabilities:
            p = float(p)
            output.append({"Churn_Probability": p, "Prediction": "Likely to Churn" if p >= THRESHOLD else "Unlikely to Churn", "Risk_Level": "High" if p >= .60 else "Medium" if p >= THRESHOLD else "Low"})
        return output


def model_info() -> dict[str, Any]:
    return {"algorithm": "Logistic Regression", "model_type": "Scikit-learn Pipeline", "feature_count": len(FEATURES), "features": FEATURES, "classification_threshold": THRESHOLD, "positive_class": "Yes", "risk_categories": [{"name": "Low", "range": "< 0.40"}, {"name": "Medium", "range": "0.40 to < 0.60"}, {"name": "High", "range": "≥ 0.60"}]}
