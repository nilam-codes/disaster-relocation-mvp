# sample_data/ — DEV FIXTURES ONLY

These 4 files are **small, made-up placeholder files** (15 sample villages) so the
API and frontend can be run and tested locally *before* you point them at your
real pipeline output. They are NOT your GIS/census/landslide data and are NOT
used to compute anything for real villages — they only exist so `uvicorn` has
something to serve on day one.

Replace them with your real files (same column names) once you're ready:

| Sample file (dev)                     | Replace with your real file                              |
|----------------------------------------|-----------------------------------------------------------|
| uttarakhand_village_risk.csv           | data/processed/final/uttarakhand_village_risk.csv         |
| relocation_recommendations.csv         | data/processed/final/relocation_recommendations.csv       |
| villages_master.geojson                | data/processed/villages/villages_master.geojson           |
| health_facilities_uttarakhand.csv      | data/processed/health_facilities_uttarakhand.csv           |

`backend/main.py` reads whichever paths are set in `backend/.env` (see
`DATA_DIR` below) — it does not care whether the CSVs are the sample ones or
your real 16,920-village output. Villages with blank risk/demographic columns
are always shown as `"Insufficient Data"` — the API never fills in a number
that isn't in the CSV.
