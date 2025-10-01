from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
import joblib
import os
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

# Root → /docs
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# Sökvägar till modell och cleaned data (oberoende av varifrån du startar servern)
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "taxi_model.joblib")
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


class PredictRequest(BaseModel):
    distance_km: float = Field(..., ge=0.0, description="Resans längd i km (>= 0)")
    duration_min: float = Field(..., ge=0.0, description="Restid i minuter (>= 0)")
    passenger_count: int = Field(1, ge=1, le=8, description="Antal passagerare (1–8)")



@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model_loaded}


@app.post("/predict")
def predict(req: PredictRequest):
    # Enkel baseline om modell saknas
    if not _model_loaded:
        base_fare = 3.5
        per_km = 1.8
        per_min = 0.5
        fare = base_fare + per_km * req.distance_km + per_min * req.duration_min
        return {"predicted_fare": round(float(fare), 2), "used_model": False}

    # Om modell finns, använd den
    X = [[req.distance_km, req.duration_min, req.passenger_count]]
    try:
        y = float(_model.predict(X)[0])
        y = max(y, 0.0)  # golv: tillåt inte negativa priser
        return {"predicted_fare": round(y, 2), "used_model": True}
    except Exception as e:
        # Fallback om något går fel
        base_fare = 3.5
        per_km = 1.8
        per_min = 0.5
        fare = base_fare + per_km * req.distance_km + per_min * req.duration_min
        return {"predicted_fare": round(float(fare), 2), "used_model": False, "note": f"fallback: {e}"}


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


@app.get("/data/sample")
def data_sample(n: int = 5):
    if not os.path.exists(DATA_CLEANED_PATH):
        return {"rows": [], "note": "cleaned_taxi.csv saknas"}
    df = pd.read_csv(DATA_CLEANED_PATH)
    n = max(1, min(int(n), 50))  # skydda API:t
    return {"rows": df.head(n).to_dict(orient="records")}
