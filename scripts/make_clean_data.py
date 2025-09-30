"""Rensa och förbered data för modellträning.

- Läser `data/taxi_trip_pricing.csv` (kolumner enligt uppgiften).
- Enkla steg: droppar uppenbart orimliga värden, fyller saknade med median/mode.
- Exporterar `data/cleaned_taxi.csv` med kolumner:
  distance_km, duration_min, passenger_count, fare
"""
import os
import pandas as pd
import numpy as np

RAW = "data/taxi_trip_pricing.csv"
OUT = "data/cleaned_taxi.csv"

df = pd.read_csv(RAW)

# Standardisera kolumnnamn
df = df.rename(columns={
    "Trip_Distance_km": "distance_km",
    "Trip_Duration_Minutes": "duration_min",
    "Passenger_Count": "passenger_count",
    "Trip_Price": "fare"
})

# Behåll bara de kolumner vi använder i första enkla modellen
keep = ["distance_km", "duration_min", "passenger_count", "fare"]
df = df[keep]

# Snabb sanity check: ta bort negativa och noll-distans med lång tid
df = df[(df["distance_km"] > 0) & (df["duration_min"] > 0)]

# Fyll saknade värden
for col in ["distance_km", "duration_min", "passenger_count", "fare"]:
    if df[col].dtype.kind in "iufc":
        df[col] = df[col].fillna(df[col].median())
    else:
        df[col] = df[col].fillna(df[col].mode().iloc[0])

# Ta bort outliers i target/fare (klipp till 1:a–99:e percentil)
low, high = df["fare"].quantile([0.01, 0.99])
df = df[(df["fare"] >= low) & (df["fare"] <= high)]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
df.to_csv(OUT, index=False)
print(f"Sparade {len(df)} rader till {OUT}")
