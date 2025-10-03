# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import joblib
import os
import json
import pandas as pd

app = FastAPI(title="Taxi Prediction API", version="0.2.0")

# CORS: tillåt allt i dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root -> /docs
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# Sökvägar till modell, metadata och cleaned data (oberoende av varifrån du startar servern)
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "taxi_model.joblib")
)
META_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "model_meta.json")
)
DATA_CLEANED_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "cleaned_taxi.csv")
)

# Ladda modell om den finns
_model = None
_model_loaded = False
if os.path.exists(MODEL_PATH):
    try:
        _model = joblib.load(MODEL_PATH)
        _model_loaded = True
    except Exception as e:
        print("Kunde inte ladda modell:", e)

def _read_meta() -> dict:
    if os.path.exists(META_PATH):
        try:
            with open(META_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Kunde inte läsa metadata:", e)
    return {}

class PredictRequest(BaseModel):
    distance_km: float = Field(..., ge=0.0, description="Resans längd i km (>= 0)")
    duration_min: float = Field(..., ge=0.0, description="Restid i minuter (>= 0)")
    passenger_count: int = Field(1, ge=1, le=8, description="Antal passagerare (1–8)")

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model_loaded}

@app.get("/model/info")
def model_info():
    meta = _read_meta()
    # Om metadata saknas, försök hämta klassnamn från modellen
    model_name = meta.get("model_name")
    if not model_name and _model_loaded:
        model_name = _model.__class__.__name__
    return {
        "model_loaded": _model_loaded,
        "model_name": model_name,
        "trained_at": meta.get("trained_at"),
        "mae": meta.get("mae"),
        "features": meta.get("features"),
        "has_cleaned_data": os.path.exists(DATA_CLEANED_PATH),
    }

@app.post("/predict")
def predict(req: PredictRequest):
    # Enkel baseline om modell saknas eller något går fel
    def baseline():
        base_fare = 3.5
        per_km = 1.8
        per_min = 0.5
        fare = base_fare + per_km * req.distance_km + per_min * req.duration_min
        return round(fare, 2), False, None

    if not _model_loaded:
        y, used_model, model_name = baseline()
        return {"predicted_fare": y, "used_model": used_model, "model_name": model_name}

    try:
        # Undvik sklearn-varningen: skicka in en DataFrame med kolumnnamn
        x_df = pd.DataFrame(
            [[req.distance_km, req.duration_min, req.passenger_count]],
            columns=["distance_km", "duration_min", "passenger_count"],
        )
        y = float(_model.predict(x_df)[0])
        y = max(y, 0.0)  # golv: inga negativa priser
        model_name = _model.__class__.__name__
        return {"predicted_fare": round(y, 2), "used_model": True, "model_name": model_name}
    except Exception as e:
        y, used_model, model_name = baseline()
        return {"predicted_fare": y, "used_model": False, "note": f"fallback: {e}"}

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
        "columns": list(df[cols].columns),
        "describe": desc,
    }

@app.get("/data/sample")
def data_sample(n: int = 5):
    if not os.path.exists(DATA_CLEANED_PATH):
        return {"rows": [], "note": "cleaned_taxi.csv saknas"}
    df = pd.read_csv(DATA_CLEANED_PATH)
    n = max(1, min(int(n), 50))  # skydda API:t
    return {"rows": df.head(n).to_dict(orient="records")}
