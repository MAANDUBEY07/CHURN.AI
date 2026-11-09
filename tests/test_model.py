import numpy as np
import pandas as pd
import joblib
import pytest

from backend.model import ModelService
from backend.validation import FEATURES


class StubModel:
    classes_ = np.array(["No", "Yes"])
    feature_names_in_ = np.array(FEATURES)
    def predict_proba(self, frame):
        assert list(frame.columns) == FEATURES
        return np.array([[.60, .40], [.40, .60], [.39, .61]])


def test_probability_threshold_and_risk_levels():
    service = ModelService(); service.model = StubModel()
    rows = service.predict(pd.DataFrame([{c: None for c in FEATURES} for _ in range(3)]))
    assert [r["Churn_Probability"] for r in rows] == [.4, .6, .61]
    assert [r["Prediction"] for r in rows] == ["Likely to Churn"] * 3
    assert [r["Risk_Level"] for r in rows] == ["Medium", "High", "High"]


def test_below_threshold_is_low_risk():
    service = ModelService(); service.model = StubModel()
    rows = service.predict(pd.DataFrame([{c: None for c in FEATURES}]))
    # Swap in one below-threshold probability.
    service.model.predict_proba = lambda frame: np.array([[.61, .39]])
    result = service.predict(pd.DataFrame([{c: None for c in FEATURES}]))[0]
    assert result["Prediction"] == "Unlikely to Churn"
    assert result["Risk_Level"] == "Low"


def test_model_loads_once_and_requires_yes_class(tmp_path):
    path = tmp_path / "model.pkl"
    joblib.dump(StubModel(), path)
    service = ModelService(path)
    service.load()
    assert service.loaded
    assert service.model.classes_.tolist() == ["No", "Yes"]


def test_missing_model_is_reported(tmp_path):
    with pytest.raises(FileNotFoundError, match="Required trained model was not found"):
        ModelService(tmp_path / "missing.pkl").load()
