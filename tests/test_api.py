from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint_reports_model_status():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert "model_loaded" in response.json()


def test_model_info_endpoint_exposes_threshold():
    with TestClient(app) as client:
        response = client.get("/api/model-info")
        assert response.status_code == 200
        assert response.json()["feature_count"] == 19
        assert response.json()["classification_threshold"] == .4


def test_single_prediction_requires_loaded_model():
    with TestClient(app) as client:
        response = client.post("/api/predict", json={})
        assert response.status_code in (422, 503)


def test_bulk_csv_rejects_missing_feature_column():
    with TestClient(app) as client:
        response = client.post("/api/predict/bulk", files={"file": ("customers.csv", "tenure,gender\n2,Female\n", "text/csv")})
        if response.status_code != 503:
            assert response.status_code == 422
            assert "Missing required columns" in response.json()["detail"]
