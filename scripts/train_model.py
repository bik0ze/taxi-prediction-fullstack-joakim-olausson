"""
Träna och jämför enkla modeller för taxipris.

- Läser data/cleaned_taxi.csv (fallback: genererar syntetisk data).
- Jämför LinearRegression, RidgeCV och RandomForestRegressor.
- Väljer modellen med lägst MAE på test.
- Tränar om den bästa modellen på ALL data och sparar till backend/models/taxi_model.joblib.
"""
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

DATA_PATH = "data/cleaned_taxi.csv"
MODEL_PATH = "backend/models/taxi_model.joblib"
RANDOM_STATE = 42

# --- Läs data ---
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    # Fallback: syntetisk data så skriptet alltid fungerar
    rng = np.random.default_rng(RANDOM_STATE)
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

# Säkerställ kolumner
features = ["distance_km", "duration_min", "passenger_count"]
target = "fare"
missing = [c for c in features + [target] if c not in df.columns]
if missing:
    raise ValueError(f"Saknar kolumner i datasetet: {missing}")

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
    ("RandomForest", RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE))
]

results = []
for name, model in candidates:
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, pred)
    results.append((name, model, mae))

# Sortera på MAE (lägst är bäst)
results.sort(key=lambda t: t[2])

print("MAE per modell:")
for name, _, mae in results:
    print(f" - {name}: {mae:.3f}")

best_name, best_model, best_mae = results[0]
print(f"\nVald modell: {best_name} (MAE={best_mae:.3f})")

# Träna bästa modellen på ALL data och spara
best_model.fit(X, y)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(best_model, MODEL_PATH)
print(f"Modell sparad till {MODEL_PATH}")
