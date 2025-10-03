"""
Träna och jämför enkla modeller för taxipris och spara metadata.

- Läser data/cleaned_taxi.csv (fallback: syntetisk data om fil saknas).
- Jämför LinearRegression, RidgeCV och RandomForestRegressor.
- Väljer modellen med lägst MAE på test.
- Tränar om den bästa modellen på ALL data och sparar till backend/models/taxi_model.joblib.
- Spara även metadata till backend/models/model_meta.json.
"""

import os
import json
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import sklearn
import joblib

DATA_PATH = "data/cleaned_taxi.csv"
MODEL_PATH = "backend/models/taxi_model.joblib"
META_PATH = "backend/models/model_meta.json"
RANDOM_STATE = 42

# --- Läs data ---
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    data_source = DATA_PATH
else:
    # Fallback: syntetisk data så skriptet alltid fungerar
    rng = np.random.default_rng(RANDOM_STATE)
    n = 200
    distance = rng.uniform(0.5, 25.0, n)
    duration = 6 + 2.2 * distance + rng.normal(0, 4, n)
    passengers = rng.integers(1, 5, n)
    fare = 3.5 + 1.8 * distance + 0.5 * duration + rng.normal(0, 2.0, n)
    df = pd.DataFrame({
        "distance_km": distance,
        "duration_min": duration,
        "passenger_count": passengers,
        "fare": fare,
    })
    data_source = "synthetic"

# Säkerställ kolumner
features = ["distance_km", "duration_min", "passenger_count"]
target = "fare"
missing = [c for c in features + [target] if c not in df.columns]
if missing:
    raise ValueError(f"Saknar kolumn(er) i datasetet: {missing}")

# Droppa ev. NA
df = df[features + [target]].dropna()

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

candidates = [
    ("LinearRegression", LinearRegression()),
    ("RidgeCV", RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0])),
    ("RandomForest", RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE)),
]

results = []
for name, model in candidates:
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, pred)
    results.append((name, model, mae))

# Sortera på MAE (lägst är bäst)
results.sort(key=lambda t: t[2])
best_name, best_model, best_mae = results[0]

print("MAE per modell:")
for name, _, mae in results:
    print(f" - {name}: {mae:.3f}")

print(f"\nVald modell: {best_name} (MAE={best_mae:.3f})")

# Träna bästa modellen på ALL data och spara
best_model.fit(X, y)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(best_model, MODEL_PATH)
print(f"Modell sparad till {MODEL_PATH}")

# --- Spara metadata ---
meta = {
    "model_name": best_name,
    "mae": float(best_mae),
    "trained_at": datetime.utcnow().isoformat() + "Z",
    "features": features,
    "target": target,
    "n_rows": int(len(df)),
    "data_source": data_source,
    "sklearn": sklearn.__version__,
}
with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"Metadata sparad till {META_PATH}")
