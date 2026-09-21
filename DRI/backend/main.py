"""
main.py — DRI API layer

A clean FastAPI wrapper around the CSV / GeoJSON output of your existing
risk_engine.py and relocation_engine.py. It does not reimplement or modify
that logic — it only reads the files those scripts already produce and
serves them to the frontend as JSON.

Run:
    uvicorn main:app --reload --port 8000
"""

from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import data_loader as dl


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="DRI API",
    description="Disaster Relocation Intelligence — Uttarakhand",
    version="0.1.0",
)


# =========================================================
# CORS
# =========================================================
# Frontend runs separately on port 5500.
# Allow both localhost and 127.0.0.1 because browsers treat
# them as different origins.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# COVERAGE
# =========================================================

@app.get("/api/coverage")
def coverage():
    """Statewide coverage numbers shown in the dashboard sidebar."""
    return dl.get_coverage()


# =========================================================
# DISTRICTS
# =========================================================

@app.get("/api/districts")
def districts():
    return {
        "districts": dl.get_districts()
    }


# =========================================================
# VILLAGES
# =========================================================

@app.get("/api/villages")
def villages(
    district: Optional[str] = None,
    q: Optional[str] = None,
):
    """
    List villages, optionally filtered by district and/or
    a search term matched against village name.
    """

    results = dl.get_all_villages(
        district=district
    )

    if q:
        q_lower = q.lower()

        results = [
            v
            for v in results
            if q_lower in (
                v.get("village_name") or ""
            ).lower()
        ]

    return {
        "count": len(results),
        "villages": results,
    }


# =========================================================
# VILLAGE GEOJSON
# =========================================================

@app.get("/api/villages/geojson")
def villages_geojson(
    district: Optional[str] = None,
):
    """
    Return village polygons with risk/GIS attributes attached
    as GeoJSON properties for Leaflet.
    """

    risk_by_id = {
        v["village_id"]: v
        for v in dl.get_all_villages(
            district=district
        )
    }

    return dl.get_villages_geojson(
        risk_by_id=risk_by_id
    )


# =========================================================
# SINGLE VILLAGE
# =========================================================

@app.get("/api/villages/{village_id}")
def village_detail(
    village_id: str,
):
    village = dl.get_village(
        village_id
    )

    if village is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Village '{village_id}' not found"
            ),
        )

    return village


# =========================================================
# RISK ASSESSMENT
# =========================================================

@app.get("/api/risk/{village_id}")
def risk_detail(
    village_id: str,
):
    """
    Risk breakdown for the Village Risk Assessment page.
    """

    village = dl.get_village(
        village_id
    )

    if village is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Village '{village_id}' not found"
            ),
        )

    # -----------------------------------------------------
    # Incomplete profile
    # -----------------------------------------------------

    if not village["has_complete_risk_profile"]:

        return {
            "village_id": village_id,
            "village_name": village["village_name"],
            "district": village["district"],
            "status": (
                "Risk Assessment Pending — "
                "Insufficient Data"
            ),
            "has_complete_risk_profile": False,
        }

    # -----------------------------------------------------
    # Complete profile
    # -----------------------------------------------------

    return {
        "village_id": village["village_id"],
        "village_name": village["village_name"],
        "district": village["district"],
        "has_complete_risk_profile": True,

        "risk_score": village["risk_score"],
        "risk_category": village["risk_category"],
        "priority": village["priority"],

        "hazard": {
            "score": village["hazard_score"],
            "landslide_hazard": village[
                "landslide_hazard"
            ],
            "rainfall_hazard": village[
                "rainfall_hazard"
            ],
            "river_signal": village[
                "river_signal"
            ],
            "river_signal_note": (
                "Supporting hydrological context only "
                "— not part of the current risk formula."
            ),
        },

        "exposure": {
            "score": village["exposure_score"],
            "population": village["population"],
        },

        "vulnerability": {
            "score": village[
                "vulnerability_score"
            ],
            "children_0_6": village[
                "children_0_6"
            ],
            "illiteracy_rate": village[
                "illiteracy_rate"
            ],
            "sc_st_pct": village[
                "sc_st_pct"
            ],
        },

        "supporting_signals": {
            "mean_slope_deg": village[
                "mean_slope_deg"
            ],
            "road_distance_km": village[
                "road_distance_km"
            ],
            "nearest_rainfall_station": village[
                "nearest_rainfall_station"
            ],
            "nearest_river_station": village[
                "nearest_river_station"
            ],
            "landslide_count": village[
                "landslide_count"
            ],
        },
    }


# =========================================================
# RELOCATION
# =========================================================

@app.get("/api/relocation/{village_id}")
def relocation_detail(
    village_id: str,
):
    """
    Relocation recommendation(s) for a source village.

    Returns an empty list if no recommendation has been
    generated for that village yet.
    """

    village = dl.get_village(
        village_id
    )

    if village is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Village '{village_id}' not found"
            ),
        )

    recs = dl.get_relocation_for_source(
        village_id
    )

    return {
        "source_village_id": village_id,
        "source_village": village["village_name"],
        "source_district": village["district"],
        "source_population": village["population"],
        "source_risk_score": village["risk_score"],
        "source_priority": village["priority"],
        "recommendations": recs,
    }


# =========================================================
# HEALTH FACILITIES
# =========================================================

@app.get("/api/health-facilities")
def health_facilities(
    district: Optional[str] = None,
):
    return {
        "facilities": dl.get_health_facilities(
            district=district
        )
    }


# =========================================================
# ROOT / HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "DRI API",
        "docs": "/docs",
    }