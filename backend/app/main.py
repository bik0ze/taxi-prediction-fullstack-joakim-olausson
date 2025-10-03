from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import joblib
import os
import pandas as pd

app = FastAPI(title="Taxi Prediction API", version="0.2.0")

# ---- CORS: tillåt allt i dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Root -> /docs
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# ---- Sökvägar till modell och cleaned data (oberoende av varifrån du startar servern)
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "taxi_model.joblib")
)
MODEL_META_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "taxi_model.meta.json")
)
DATA_CLEANED_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "cleaned_taxi.csv")
)

# ---- Ladda modell om den finns
_model = None
_model_loaded = False
_model_name = None
_model_meta = {}

if os.path.exists(MODEL_PATH):
    try:
        _model = joblib.load(MODEL_PATH)
        _model_loaded = True
        _model_name = type(_model).__name__
        if os.path.exists(MODEL_META_PATH):
            import json
            with open(MODEL_META_PATH, "r", encoding="utf-8") as f:
                _model_meta = json.load(f)
    except Exception as e:
        print("Kunde inte ladda modell:", e)


# ---- Request-schema
class PredictRequest(BaseModel):
    distance_km: float = Field(..., ge=0.0, description="Resans längd i km (>= 0)")
    duration_min: float = Field(..., ge=0.0, description="Restid i minuter (>= 0)")
    passenger_count: int = Field(1, ge=1, le=8, description="Antal passagerare (1–8)")


# ---- Health
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model_loaded}


# ---- Model info
@app.get("/model/info")
def model_info():
    has_data = os.path.exists(DATA_CLEANED_PATH)
    info = {
        "model_loaded": _model_loaded,
        "model_name": _model_name,
        "has_cleaned_data": has_data,
    }
    if _model_meta:
        info["meta"] = _model_meta
    return info


# ---- Predict
@app.post("/predict")
def predict(req: PredictRequest):
    # Enkel baseline om modell saknas eller fel uppstår
    def _baseline():
        base_fare = 3.5
        per_km = 1.8
        per_min = 0.5
        fare = base_fare + per_km * req.distance_km + per_min * req.duration_min
        return {"predicted_fare": round(float(fare), 2), "used_model": False}

    if not _model_loaded:
        return _baseline()

    # Bygg en DataFrame med rätt kolumnnamn -> tar bort sklearn-varning
    X = pd.DataFrame(
        [
            {
                "distance_km": req.distance_km,
                "duration_min": req.duration_min,
                "passenger_count": req.passenger_count,
            }
        ]
    )

    try:
        y = float(_model.predict(X)[0])
        y = max(y, 0.0)  # golv: tillåt inte negativa priser
        return {
            "predicted_fare": round(y, 2),
            "used_model": True,
            "model_name": _model_name,
        }
    except Exception as e:
        # Fallback om något går fel
        out = _baseline()
        out["note"] = f"fallback: {e}"
        return out


# ---- Stats på cleaned data
@app.get("/stats")
def stats():
    if not os.path.exists(DATA_CLEANED_PATH):
        return {"has_data": False, "note": "cleaned_taxi.csv saknas"}
    df = pd.read_csv(DATA_CLEANED_PATH)
    cols = ["distance_km", "duration_min", "passenger_count", "fare"]
    desc = df[cols].describe().round(2).to_dict()
    return {
        "has_data": True,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "describe": desc,
    }


# ---- Några exempelrader
@app.get("/data/sample")
def data_sample(n: int = 5):
    if not os.path.exists(DATA_CLEANED_PATH):
        return {"rows": [], "note": "cleaned_taxi.csv saknas"}
    df = pd.read_csv(DATA_CLEANED_PATH)
    n = max(1, min(int(n), 50))  # skydda API:t
    return {"rows": df.head(n).to_dict(orient="records")}
