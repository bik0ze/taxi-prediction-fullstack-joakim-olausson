# Taxi Prediction (fullstack) – startmall

Detta är en **enkel startmall** för kursprojektet. Den innehåller en minimal FastAPI-backend,
en väldigt enkel frontend samt struktur för data, notebooks och ML-skript.

## Kör igång (lokalt)

1. Skapa och aktivera virtuell miljö
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   ```
2. Installera paket
   ```bash
   pip install -r requirements.txt
   ```
3. Starta backend (FastAPI)
   ```bash
   uvicorn backend.app.main:app --reload
   ```
   Backend kör då på `http://127.0.0.1:8000` och docs på `http://127.0.0.1:8000/docs`.

4. Öppna `frontend/index.html` i webbläsaren. (I dev räcker det att dubbelklicka på filen.)

## Struktur

```
backend/
  app/
    main.py          # FastAPI-app med /health och /predict
  models/            # Här sparas tränad modell (.joblib)
data/                # Rådata eller processad data (git-ignoreras)
frontend/
  index.html         # Enkel UI
  app.js
notebooks/           # Jupyter notebooks (EDA m.m.)
scripts/
  train_model.py     # Exempelskript för att träna och spara modell
requirements.txt
.gitignore
```

## Flöde i projektet (enkelt)

- **EDA & cleaning**: lägg notebooks i `notebooks/`, exportera ren data till `data/`.
- **Träna modell**: justera `scripts/train_model.py` (läs din data), kör skriptet och spara modellen till `backend/models/taxi_model.joblib`.
- **API**: `POST /predict` tar in features och returnerar pris, använder modellen om den finns annars en enkel baseline.
- **Frontend**: Hämtar från `/predict` och visar priset.

Lycka till! 🚕


## Steg-för-steg & commit-förslag

1. **chore:** initiera projekt (den här startmallen)
2. **data:** lägg till `data/taxi_trip_pricing.csv`
3. **feat(eda):** lägg till `notebooks/EDA.ipynb`
4. **feat(cleaning):** skript `scripts/make_clean_data.py` som exporterar `data/cleaned_taxi.csv`
5. **feat(model):** träna modell (`scripts/train_model.py`) → `backend/models/taxi_model.joblib`
6. **feat(api):** använd tränad modell i `/predict`
7. **feat(frontend):** koppla UI till API och visa pris
8. **docs:** uppdatera README med resultat och körinstruktioner
