from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os

app = FastAPI(title="Taxi Prediction API", version="0.1.0")

# CORS: tillåt allt i dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "taxi_model.joblib")
_model = None
_model_loaded = False
if os.path.exists(MODEL_PATH):
    try:
        _model = joblib.load(MODEL_PATH)
        _model_loaded = True
    except Exception as e:
        print("Kunde inte ladda modell:", e)


class PredictRequest(BaseModel):
    distance_km: float
    duration_min: float
    passenger_count: int = 1


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
        y = _model.predict(X)[0]
        return {"predicted_fare": round(float(y), 2), "used_model": True}
    except Exception as e:
        # Fallback om något går fel
        base_fare = 3.5
        per_km = 1.8
        per_min = 0.5
        fare = base_fare + per_km * req.distance_km + per_min * req.duration_min
        return {"predicted_fare": round(float(fare), 2), "used_model": False, "note": f"fallback: {e}"}
