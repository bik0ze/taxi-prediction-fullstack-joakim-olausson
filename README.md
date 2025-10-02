# Taxi Prediction – enkel fullstack (Python)

En minimal helhetsapp som **förutspår taxipris**.  
Projektet innehåller:
- **Datahantering** (EDA/cleaning)
- **ML-modell** (scikit-learn, sparad med `joblib`)
- **Backend** (FastAPI + endpoints för `/predict`, `/stats`, m.m.)
- **Frontend** (vanilla HTML/JS som anropar API:et)

---

## 🚀 Snabbstart

> Kör kommandona i projektets rot (där `backend/`, `frontend/`, `scripts/` finns).

```bash
# 1) Skapa och aktivera virtuell miljö
python -m venv .venv
# Windows (PowerShell):
. .venv\Scripts\Activate
# macOS/Linux:
# source .venv/bin/activate

# 2) Installera paket
pip install -r requirements.txt

# 3) Rensa data (skapar data/cleaned_taxi.csv)
python scripts/make_clean_data.py

# 4) Träna modell (skapar backend/models/taxi_model.joblib)
python scripts/train_model.py

# 5) Starta API (FastAPI/uvicorn)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
# API docs: http://127.0.0.1:8000/docs

### Modellval
Testade LinearRegression (MAE 12.967), RidgeCV (12.983) och RandomForest (13.675).
Valde **LinearRegression** (lägst MAE). Modellen sparas som `backend/models/taxi_model.joblib`.

### Modellval & resultat
Vi testade tre modeller på `cleaned_taxi.csv`:

- LinearRegression — **MAE 12.967**  ← vald modell  
- RidgeCV — MAE 12.983  
- RandomForest — MAE 13.675  

Valde **LinearRegression** (lägst MAE). Modellen sparas som `backend/models/taxi_model.joblib` och laddas av API:t.
