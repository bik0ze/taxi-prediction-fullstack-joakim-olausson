"""Träna en enkel regressionsmodell för taxipris.

- Läser `data/cleaned_taxi.csv` om den finns med kolumner:
  distance_km, duration_min, passenger_count, fare
- Annars genererar syntetisk data så att allt går att köra direkt.

Sparar modellen till `backend/models/taxi_model.joblib`.
"""

import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

DATA_PATH = "data/cleaned_taxi.csv"
MODEL_PATH = "backend/models/taxi_model.joblib"

if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    # Skapa syntetisk data (enkel linjär relation) för demo
    rng = np.random.default_rng(42)
    n = 2000
    distance = rng.uniform(0.5, 25.0, n)
    duration = distance * rng.uniform(2.0, 4.0, n) + rng.normal(0, 3, n)
    passengers = rng.integers(1, 5, n)
    fare = 3.5 + 1.8 * distance + 0.5 * duration + rng.normal(0, 2.0, n)
    df = pd.DataFrame({
        "distance_km": distance,
        "duration_min": duration,
        "passenger_count": passengers,
        "fare": fare
    })

X = df[["distance_km", "duration_min", "passenger_count"]]
y = df["fare"] if "fare" in df.columns else df.get("Trip_Price")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

pred = model.predict(X_test)
mae = mean_absolute_error(y_test, pred)
print(f"MAE: {mae:.2f}")

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"Modell sparad till {MODEL_PATH}")
