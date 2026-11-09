import pandas as pd
import pytest

from backend.validation import FEATURES, validate_frame


def valid_row():
    return {"SeniorCitizen": 0, "tenure": 24, "MonthlyCharges": 70.0, "TotalCharges": 1680.0,
            "gender": "Female", "Partner": "No", "Dependents": "No", "PhoneService": "Yes",
            "MultipleLines": "No", "InternetService": "Fiber optic", "OnlineSecurity": "No",
            "OnlineBackup": "No", "DeviceProtection": "No", "TechSupport": "No", "StreamingTV": "No",
            "StreamingMovies": "No", "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check"}


def test_validation_preserves_feature_order():
    result = validate_frame(pd.DataFrame([valid_row()]))
    assert list(result.columns) == FEATURES


def test_missing_column_rejected():
    row = valid_row(); row.pop("gender")
    with pytest.raises(ValueError, match="Missing required columns: gender"):
        validate_frame(pd.DataFrame([row]))


def test_invalid_category_rejected():
    row = valid_row(); row["gender"] = "Other"
    with pytest.raises(ValueError, match="gender: invalid"):
        validate_frame(pd.DataFrame([row]))


def test_invalid_numeric_rejected():
    row = valid_row(); row["tenure"] = 90
    with pytest.raises(ValueError, match="tenure: values must be between"):
        validate_frame(pd.DataFrame([row]))


def test_missing_values_rejected():
    row = valid_row(); row["Partner"] = None
    with pytest.raises(ValueError, match="Partner: missing values"):
        validate_frame(pd.DataFrame([row]))


def test_invalid_phone_combination_rejected():
    row = valid_row(); row["PhoneService"] = "No"
    with pytest.raises(ValueError, match="MultipleLines must"):
        validate_frame(pd.DataFrame([row]))


def test_empty_frame_rejected():
    with pytest.raises(ValueError, match="no customer rows"):
        validate_frame(pd.DataFrame(columns=FEATURES))
