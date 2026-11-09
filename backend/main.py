import io
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .model import ModelService, model_info
from .schemas import CustomerInput
from .validation import FEATURES, validate_customer, validate_frame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
model_service = ModelService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        model_service.load()
        logger.info("Trained model loaded from %s", model_service.path)
    except Exception as exc:
        logger.exception("Could not load required trained model")
        app.state.model_error = str(exc)
    else:
        app.state.model_error = None
    yield


app = FastAPI(title="CHURN.AI API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def require_model():
    if not model_service.loaded:
        raise HTTPException(503, detail=f"Prediction model unavailable: {getattr(app.state, 'model_error', 'model is not loaded')}")


@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": model_service.loaded, "model_error": getattr(app.state, "model_error", None)}


@app.get("/api/model-info")
def get_model_info():
    return {**model_info(), "model_loaded": model_service.loaded}


@app.post("/api/predict")
def predict(customer: CustomerInput):
    require_model()
    try:
        validated = validate_customer(customer.model_dump())
        return model_service.predict(validated)[0]
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc


@app.post("/api/predict/bulk")
async def predict_bulk(file: UploadFile = File(...)):
    require_model()
    if not file.filename or Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(400, detail="Upload a .csv file.")
    raw = await file.read()
    if not raw: raise HTTPException(400, detail="The uploaded CSV is empty.")
    if len(raw) > 20 * 1024 * 1024: raise HTTPException(413, detail="CSV exceeds the 20 MB upload limit.")
    try:
        original = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        raise HTTPException(400, detail=f"Could not parse CSV: {exc}") from exc
    try:
        validated = validate_frame(original)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    reserved = {"Churn_Probability", "Prediction", "Risk_Level"}.intersection(original.columns)
    if reserved:
        raise HTTPException(422, detail="Input CSV contains reserved result column(s): " + ", ".join(sorted(reserved)))
    results = model_service.predict(validated)
    result_frame = original.reset_index(drop=True).copy()
    for col in ["Churn_Probability", "Prediction", "Risk_Level"]:
        result_frame[col] = [row[col] for row in results]
    return {"count": len(results), "results": result_frame.where(pd.notnull(result_frame), None).to_dict(orient="records"), "summary": {"likely_to_churn": sum(x["Prediction"] == "Likely to Churn" for x in results), "low_risk": sum(x["Risk_Level"] == "Low" for x in results), "medium_risk": sum(x["Risk_Level"] == "Medium" for x in results), "high_risk": sum(x["Risk_Level"] == "High" for x in results), "average_probability": sum(x["Churn_Probability"] for x in results) / len(results)}}


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        target = (DIST / path).resolve()
        if target.is_relative_to(DIST.resolve()) and target.is_file(): return FileResponse(target)
        return FileResponse(DIST / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
