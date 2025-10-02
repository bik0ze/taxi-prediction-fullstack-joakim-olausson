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
