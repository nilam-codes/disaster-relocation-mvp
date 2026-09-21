# DRI — Disaster Relocation Intelligence

A GIS + decision-support frontend for Uttarakhand disaster relocation planning,
built on top of your existing Python risk/relocation pipeline. Real HTML/CSS/JS
frontend + a small FastAPI layer that reads your pipeline's CSV/GeoJSON output.
No React, no build step, no framework — open `.html` files in a browser and go.

## 1. Architecture

```
 risk_engine.py / relocation_engine.py   (yours — untouched)
              │
              ▼  writes CSVs / GeoJSON
 data/processed/final/*.csv, villages_master.geojson
              │
              ▼  read-only
 backend/data_loader.py  ──►  backend/main.py (FastAPI)  ──►  HTTP JSON
                                                                   │
                                                                   ▼
                                          frontend/*.html + js/api.js (fetch)
                                          Leaflet.js renders the GIS map
```

The API layer never recomputes risk or relocation logic — it only loads what
your pipeline already produced, cleans NaNs into `null` (never invents a
number), and serves it as JSON. The frontend never hardcodes village data —
every page calls `js/api.js`, which calls the FastAPI endpoints.

## 2. Folder structure

```
DRI/
├── README.md                      ← this file
├── backend/
│   ├── main.py                    FastAPI app — the 6 endpoints
│   ├── data_loader.py             Reads/joins CSV + GeoJSON, no risk logic
│   ├── requirements.txt
│   ├── .env                       Points at data files + coverage totals
│   └── sample_data/                DEV FIXTURES (15 fake villages) — replace
│       ├── uttarakhand_village_risk.csv       with your real pipeline output,
│       ├── relocation_recommendations.csv     see sample_data/README.md
│       ├── villages_master.geojson
│       ├── health_facilities_uttarakhand.csv
│       └── README.md
└── frontend/
    ├── index.html                 Landing page ("Enter System")
    ├── dashboard.html             Main Risk Map Dashboard
    ├── assessment.html            Village Risk Assessment
    ├── relocation.html            Relocation Options
    ├── css/style.css              All styling (design tokens at the top)
    ├── js/
    │   ├── api.js                 Single API client — the ONLY place the
    │   │                          backend URL is set (DRI_API_BASE)
    │   ├── app.js                 Header search + nav highlighting
    │   ├── map.js                 Dashboard: Leaflet map + filters + detail panel
    │   ├── assessment.js          Assessment page rendering
    │   └── relocation.js          Relocation page rendering
    └── assets/
        ├── dri-logo.jpeg          Your logo (already wired in)
        └── README.md              Where to drop the real background image
```

## 3. Connecting to your real data

Right now `backend/.env` points at the 15-village `sample_data/` fixtures so
you can run everything today. When your real pipeline output is ready:

1. Copy your real files somewhere the backend can read them (e.g. keep your
   existing `data/processed/final/...` layout).
2. Edit `backend/.env` and point the four paths at your real files:
   ```
   RISK_CSV=../data/processed/final/uttarakhand_village_risk.csv
   RELOCATION_CSV=../data/processed/final/relocation_recommendations.csv
   VILLAGES_GEOJSON=../data/processed/villages/villages_master.geojson
   HEALTH_CSV=../data/processed/health_facilities_uttarakhand.csv
   ```
3. Restart `uvicorn`. Nothing in the frontend changes — same columns, same shape.

Required CSV columns for `uttarakhand_village_risk.csv` (blank = shown as
"Insufficient Data", never guessed):
`village_id, village_name, district, population, children_0_6,
illiteracy_rate, sc_st_pct, landslide_count, mean_slope_deg, rainfall_hazard,
landslide_hazard, river_signal, road_distance_km, nearest_rainfall_station,
nearest_river_station, hazard_score, exposure_score, vulnerability_score,
risk_score, risk_category, priority`

Required columns for `relocation_recommendations.csv`:
`source_village_id, source_village, source_district, dest_village_id,
dest_village, dest_district, dest_risk_score, dest_risk_category,
safety_score, capacity_score, distance_score, healthcare_score, distance_km,
estimated_additional_capacity, healthcare_access_note, suitability_score`

`villages_master.geojson` needs a `village_id` property on each feature so the
API can join it to the risk CSV.

## 4. Installation (Windows)

Open **Terminal 1** for the backend:

```bat
cd DRI\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

(If you already have a Python environment with pandas installed for your
pipeline, you can skip the venv and just `pip install fastapi uvicorn
python-dotenv` into it instead — nothing here conflicts with your existing
packages.)

## 5. Running it

**Terminal 1 — backend (FastAPI):**

```bat
cd DRI\backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Leave this running. Check it worked: open `http://127.0.0.1:8000/docs` in a
browser — you should see the interactive API docs with 7 endpoints.

**Terminal 2 — frontend (static file server):**

Any static server works. Simplest option, no install needed:

```bat
cd DRI\frontend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500/index.html` in your browser.

> If you open `index.html` directly by double-clicking it (`file://…`), the
> `fetch()` calls to the API will be blocked by the browser for CORS/security
> reasons — always serve `frontend/` through `http://` as above.

If you serve the frontend from a different port, no code change is needed —
`js/api.js` defaults to `http://127.0.0.1:8000`. To point at a different
backend host, set `window.DRI_API_BASE = "http://..."` in a `<script>` tag
before `api.js` loads.

## 6. Testing checklist

- [ ] `http://127.0.0.1:8000/docs` loads and lists 7 endpoints
- [ ] `http://127.0.0.1:8000/api/coverage` returns JSON with village counts
- [ ] `index.html` loads, shows the logo, hero stats populate from the API
- [ ] "Enter System" → `dashboard.html` loads with the Leaflet map and 15
      sample village polygons colored by risk
- [ ] District dropdown filters both the map and the village dropdown
- [ ] Clicking a village polygon opens its detail panel on the right
- [ ] Header search (type "Sherpur") shows a dropdown result, click it —
      dashboard updates and pans to that village
- [ ] "Full assessment" button → `assessment.html` shows the risk ring,
      hazard/vulnerability/composition sections
- [ ] Selecting village `V1006` (Nagthat) shows **"Insufficient Data"**
      instead of a fake score, on both dashboard and assessment
- [ ] "Relocation options" for Sherpur, Lakha Mandal, or Chatra shows the
      Hrishikesh recommendation card with the planning-proxy capacity note
- [ ] Relocation page for a village with no recommendation (e.g. V1011 Almora
      Rural) shows the "no recommendation yet" empty state, not an error
- [ ] Stop the backend (Ctrl+C) and reload the dashboard — you get a visible
      "couldn't reach the API" state, not a blank/broken page

## 7. Demonstrating DRI at SIH

A tight run-through that shows the full decision-support loop in under 3
minutes:

1. **Landing page** — state the problem in one line: which villages need to
   move, where to, and whether the destination can actually hold them.
2. **Risk Map** — filter to a district, point out the color-coded legend, and
   click a **High** or **Very High** village. Call out that DRI labels it a
   "Red-Zone Candidate — Authority Review Required," not a legal declaration.
3. **Village Assessment** — open the same village's full assessment. Show the
   hazard/exposure/vulnerability breakdown and explicitly point out the River
   Data Signal note ("supporting only, not in the formula") — this shows
   judgment, not just data plumbing.
4. **Insufficient Data village** — click a village like Nagthat and show it
   honestly reports "Insufficient Data" instead of a fabricated score. Judges
   notice when a team resists the temptation to fake completeness.
5. **Relocation Options** — go to Sherpur → Hrishikesh. Walk through safety,
   distance, healthcare access, and the capacity planning-proxy note ("can
   accommodate source population"). This is the differentiator — say it
   explicitly.
6. **Coverage stats** — close on the sidebar numbers (16,920 GIS villages,
   49.5% census-integrated, 46.3% complete risk) to show the scale of the real
   pipeline behind the 15-village demo dataset, and that the system is honest
   about what it doesn't yet know.
