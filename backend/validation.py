from typing import Any

import numpy as np
import pandas as pd

FEATURES = [
    "SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges", "gender", "Partner",
    "Dependents", "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
    "Contract", "PaperlessBilling", "PaymentMethod",
]
CATEGORIES = {
    "gender": ["Male", "Female"], "Partner": ["Yes", "No"], "Dependents": ["Yes", "No"],
    "PhoneService": ["Yes", "No"], "MultipleLines": ["Yes", "No", "No phone service"],
    "InternetService": ["DSL", "Fiber optic", "No"],
    **{c: ["Yes", "No", "No internet service"] for c in ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]},
    "Contract": ["Month-to-month", "One year", "Two year"], "PaperlessBilling": ["Yes", "No"],
    "PaymentMethod": ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
}
NUMERIC = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]


def validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        raise ValueError("The CSV contains no customer rows.")
    missing = [c for c in FEATURES if c not in frame.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    data = frame.loc[:, FEATURES].copy()
    errors: list[str] = []
    for col in FEATURES:
        nulls = data[col].isna()
        if nulls.any():
            errors.append(f"{col}: missing values in rows {', '.join(map(str, (np.flatnonzero(nulls)[:5] + 1)))}")
    for col in NUMERIC:
        vals = pd.to_numeric(data[col], errors="coerce")
        bad = vals.isna() & ~data[col].isna()
        if bad.any(): errors.append(f"{col}: must contain numeric values")
        data[col] = vals
    if data["SeniorCitizen"].notna().any() and not data["SeniorCitizen"].dropna().isin([0, 1]).all(): errors.append("SeniorCitizen: values must be 0 or 1")
    if data["tenure"].notna().any() and not data["tenure"].dropna().between(0, 72).all(): errors.append("tenure: values must be between 0 and 72")
    for col in ["MonthlyCharges", "TotalCharges"]:
        if data[col].notna().any() and (data[col].dropna() < 0).any(): errors.append(f"{col}: values must be non-negative")
    for col, allowed in CATEGORIES.items():
        if col in data:
            invalid = data[col].notna() & ~data[col].isin(allowed)
            if invalid.any():
                values = data.loc[invalid, col].astype(str).unique().tolist()[:5]
                errors.append(f"{col}: invalid value(s) {values}; expected {allowed}")
    # Reject logically inconsistent service selections without rewriting user input.
    if (data["PhoneService"].eq("No") & ~data["MultipleLines"].eq("No phone service")).any(): errors.append("MultipleLines must be 'No phone service' when PhoneService is 'No'")
    dependent = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    if (data["InternetService"].eq("No") & ~data[dependent].eq("No internet service").all(axis=1)).any(): errors.append("Internet-dependent services must be 'No internet service' when InternetService is 'No'")
    if errors: raise ValueError("; ".join(errors))
    return data


def validate_customer(payload: dict[str, Any]) -> pd.DataFrame:
    return validate_frame(pd.DataFrame([{k: payload.get(k) for k in FEATURES}]))
