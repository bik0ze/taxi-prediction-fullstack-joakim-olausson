# Taxi Prediction

En liten startmall för att uppskatta taxipris med ett FastAPI‑backend och en enkel frontend.

## Krav

* Python 3.10+ och `pip`
* (Valfritt) Git

## Kom igång (lokalt)

1. Skapa och aktivera virtuell miljö + installera paket

```bash
python -m venv .venv
# Windows
.venv/Scripts/activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

2. Starta API:t

```bash
uvicorn backend.app.main:app --reload
```

Öppna `http://127.0.0.1:8000/docs` för Swagger.

3. Starta frontend

* Dubbelklicka `frontend/index.html` (eller öppna i Live Server).
* Behöver du ändra API‑adress? Justera `API_URL` i `frontend/app.js`.

## Viktiga endpoints

* `GET /health` – status och om modell är laddad.
* `POST /predict`
  Request‑body (JSON):

  ```json
  {"distance_km": 5, "duration_min": 15, "passenger_count": 1}
  ```

  Response: `{ "predicted_fare": 10.5, "used_model": true }`
* `GET /stats` – enkla beskrivande mått från datasetet.
* `GET /data/sample?n=5` – några rader exempeldata.

## Träna/uppdatera modellen

```bash
python scripts/train_model.py
```

Sparar modellen till `backend/models/taxi_model.joblib`. API:t använder den automatiskt om filen finns.

## Projektstruktur (kort)

```
backend/
  app/
    main.py          # FastAPI‑app och endpoints
  models/            # Tränad modell (.joblib)
frontend/
  index.html         # Enkel UI
  app.js             # Anropar /predict, /stats, /data/sample
notebooks/
  EDA.ipynb          # Snabb EDA
scripts/
  train_model.py     # Jämför enkla modeller, sparar bästa
requirements.txt
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
