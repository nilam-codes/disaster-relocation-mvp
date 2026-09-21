"""
DRI read-only data adapter.

Connects the vanilla JS frontend to the REAL outputs already produced by
risk_engine.py / relocation_engine.py.

It does not recompute risk.
"""

import json
import math
import os
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


def _path(value: str) -> str:
    p = Path(value)

    if not p.is_absolute():
        p = (BASE_DIR / p).resolve()

    return str(p)


RISK_CSV = _path(
    os.getenv(
        "RISK_CSV",
        "../../data/processed/final/uttarakhand_village_risk.csv"
    )
)

RELOCATION_CSV = _path(
    os.getenv(
        "RELOCATION_CSV",
        "../../data/processed/final/relocation_recommendations.csv"
    )
)

VILLAGES_GEOJSON = _path(
    os.getenv(
        "VILLAGES_GEOJSON",
        "../../data/processed/villages/villages_master.geojson"
    )
)

HEALTH_CSV = _path(
    os.getenv(
        "HEALTH_CSV",
        "../../data/processed/health_facilities_uttarakhand.csv"
    )
)


INSUFFICIENT = "Insufficient Data"


# ============================================================
# BASIC HELPERS
# ============================================================

def _clean(value):

    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    if isinstance(value, str) and not value.strip():
        return None

    return value


def _norm(value) -> str:

    if value is None:
        return ""

    if isinstance(value, float) and math.isnan(value):
        return ""

    s = str(value).strip().lower()

    s = re.sub(r"\s+", " ", s)

    s = re.sub(
        r"[^a-z0-9 ]",
        "",
        s
    )

    return s


def _first(row, *names):

    for name in names:

        if name in row:

            value = _clean(
                row[name]
            )

            if value is not None:
                return value

    return None


def _numeric(value):

    value = _clean(value)

    if value is None:
        return None

    try:
        return float(value)

    except (
        TypeError,
        ValueError
    ):
        return None


# ============================================================
# GEOJSON
# ============================================================

@lru_cache(maxsize=1)
def load_geojson() -> dict:

    if not os.path.exists(
        VILLAGES_GEOJSON
    ):
        raise FileNotFoundError(
            f"Villages GeoJSON not found: {VILLAGES_GEOJSON}"
        )

    with open(
        VILLAGES_GEOJSON,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


@lru_cache(maxsize=1)
def geo_lookup() -> dict:

    """
    Create stable frontend IDs from the official GIS village code (vlcode).

    Risk CSVs are keyed by village name and district, so we bridge them
    to the GIS code without changing the risk model.
    """

    lookup = {}

    for feature in load_geojson().get(
        "features",
        []
    ):

        properties = feature.get(
            "properties",
            {}
        )

        village_id = _clean(
            properties.get("vlcode")
            or properties.get("village_id")
        )

        village_name = _clean(
            properties.get("village")
            or properties.get("village_name")
        )

        district = _clean(
            properties.get("district")
        )

        if (
            village_id is not None
            and village_name is not None
        ):

            lookup[
                (
                    _norm(village_name),
                    _norm(district)
                )
            ] = str(village_id)

    return lookup


# ============================================================
# RISK DATA CANONICALIZATION
# ============================================================

def _canonicalize_risk(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()


    # --------------------------------------------------------
    # Village name / district
    # --------------------------------------------------------

    df["village_name"] = df.apply(
        lambda r: _first(
            r,
            "village_name",
            "village",
            "Name"
        ),
        axis=1
    )

    df["district"] = df.apply(
        lambda r: _first(
            r,
            "district",
            "District",
            "district_name",
            "District_Name"
        ),
        axis=1
    )


    # --------------------------------------------------------
    # Village ID
    # --------------------------------------------------------

    if "village_id" not in df.columns:
        df["village_id"] = None

    df["village_id"] = df[
        "village_id"
    ].where(
        df["village_id"].notna(),
        None
    )

    if df["village_id"].isna().all():

        mapping = geo_lookup()

        df["village_id"] = [
            mapping.get(
                (
                    _norm(name),
                    _norm(district)
                )
            )
            for name, district
            in zip(
                df["village_name"],
                df["district"]
            )
        ]


    # ========================================================
    # IMPORTANT:
    # REAL RISK CSV COLUMN ALIASES
    # ========================================================

    aliases = {

        # ----------------------------------------------------
        # Population
        # ----------------------------------------------------

        "population": (
            "population",
            "census_population_2011",
            "total_population_village",
            "total_population",
        ),


        # ----------------------------------------------------
        # Children
        # ----------------------------------------------------

        "children_0_6": (
            "children_0_6",
            "census_children_0_6",
            "children_0_6_count",
        ),


        # ----------------------------------------------------
        # Illiteracy
        # ----------------------------------------------------

        "illiteracy_rate": (
            "illiteracy_rate",
            "illiteracy_pct",
            "census_illiterates",
        ),


        # ----------------------------------------------------
        # Social vulnerability
        # ----------------------------------------------------

        "sc_st_pct": (
            "sc_st_pct",
            "social_vulnerability_score",
        ),


        # ----------------------------------------------------
        # Landslide count
        # ----------------------------------------------------

        "landslide_count": (
            "landslide_count",
            "nearby_landslide_count",
        ),


        # ----------------------------------------------------
        # Slope
        # ----------------------------------------------------

        "mean_slope_deg": (
            "mean_slope_deg",
        ),


        # ----------------------------------------------------
        # Rainfall hazard
        # ----------------------------------------------------

        "rainfall_hazard": (
            "rainfall_hazard",
            "rainfall_hazard_score",
        ),


        # ----------------------------------------------------
        # Landslide hazard
        # ----------------------------------------------------

        "landslide_hazard": (
            "landslide_hazard",
            "landslide_hazard_score",
        ),


        # ----------------------------------------------------
        # River signal
        # ----------------------------------------------------

        "river_signal": (
            "river_signal",
            "river_hazard_score",
        ),


        # ----------------------------------------------------
        # Rainfall station
        # ----------------------------------------------------

        "nearest_rainfall_station": (
            "nearest_rainfall_station",
            "rainfall_station",
        ),


        # ----------------------------------------------------
        # River station
        # ----------------------------------------------------

        "nearest_river_station": (
            "nearest_river_station",
            "river_station",
        ),


        # ----------------------------------------------------
        # Overall hazard
        # ----------------------------------------------------

        "hazard_score": (
            "hazard_score",
            "hazard",
        ),


        # ----------------------------------------------------
        # Exposure
        # ----------------------------------------------------

        "exposure_score": (
            "exposure_score",
            "population_exposure_score",
        ),


        # ----------------------------------------------------
        # Vulnerability
        # ----------------------------------------------------

        "vulnerability_score": (
            "vulnerability_score",
        ),


        # ----------------------------------------------------
        # Overall risk
        # ----------------------------------------------------

        "risk_score": (
            "risk_score",
        ),


        # ----------------------------------------------------
        # Risk category
        # ----------------------------------------------------

        "risk_category": (
            "risk_category",
        ),


        # ----------------------------------------------------
        # Priority
        # ----------------------------------------------------

        "priority": (
            "priority",
            "relocation_priority",
        ),


        # ----------------------------------------------------
        # Road distance
        # ----------------------------------------------------

        "road_distance_km": (
            "road_distance_km",
        ),

    }


    # --------------------------------------------------------
    # Apply aliases
    # --------------------------------------------------------

    for target, names in aliases.items():

        if target not in df.columns:

            df[target] = df.apply(
                lambda r, ns=names:
                    _first(
                        r,
                        *ns
                    ),
                axis=1
            )


    # ========================================================
    # DERIVED DISPLAY FIELDS
    # ========================================================

    # --------------------------------------------------------
    # Children percentage
    # --------------------------------------------------------

    if (
        "children_0_6" in df.columns
        and "population" in df.columns
    ):

        children_numeric = pd.to_numeric(
            df["children_0_6"],
            errors="coerce"
        )

        population_numeric = pd.to_numeric(
            df["population"],
            errors="coerce"
        )

        # Only calculate percentage when the source appears
        # to contain a count rather than an already calculated %
        df["children_0_6"] = (
            children_numeric /
            population_numeric *
            100
        )


    # --------------------------------------------------------
    # Illiteracy percentage
    # --------------------------------------------------------

    if "illiteracy_rate" in df.columns:

        ill_numeric = pd.to_numeric(
            df["illiteracy_rate"],
            errors="coerce"
        )

        # The current risk engine output uses illiteracy_pct,
        # so this is already percentage when available.
        df["illiteracy_rate"] = ill_numeric


    # --------------------------------------------------------
    # SC/ST percentage
    # --------------------------------------------------------

    if (
        "sc_st_pct" not in df.columns
        or df["sc_st_pct"].isna().all()
    ):

        sc = pd.to_numeric(
            df.get(
                "census_sc_population"
            ),
            errors="coerce"
        )

        st = pd.to_numeric(
            df.get(
                "census_st_population"
            ),
            errors="coerce"
        )

        pop = pd.to_numeric(
            df["population"],
            errors="coerce"
        )

        df["sc_st_pct"] = (
            (
                sc.fillna(0)
                +
                st.fillna(0)
            )
            /
            pop
            *
            100
        )


    # --------------------------------------------------------
    # Road distance
    # --------------------------------------------------------

    if (
        "road_distance_km" not in df.columns
        or df["road_distance_km"].isna().all()
    ):

        if "road_distance_m" in df.columns:

            rd = pd.to_numeric(
                df["road_distance_m"],
                errors="coerce"
            )

            df["road_distance_km"] = (
                rd / 1000
            )


    return df


# ============================================================
# LOAD RISK CSV
# ============================================================

@lru_cache(maxsize=1)
def load_risk_df() -> pd.DataFrame:

    if not os.path.exists(
        RISK_CSV
    ):

        raise FileNotFoundError(
            f"Risk CSV not found: {RISK_CSV}"
        )

    raw = pd.read_csv(
        RISK_CSV
    )

    return _canonicalize_risk(
        raw
    )


# ============================================================
# LOAD RELOCATION CSV
# ============================================================

@lru_cache(maxsize=1)
def load_relocation_df() -> pd.DataFrame:
    """
    Load the REAL relocation_engine output.

    The current relocation_engine writes:
        source_village
        source_district
        candidate_village
        candidate_district
        estimated_capacity
        candidate_risk_score
        safety_score
        capacity_score
        distance_km
        distance_score
        healthcare_access_score
        relocation_score
        enough_capacity

    The frontend uses destination-oriented names, so this adapter
    converts candidate_* fields into dest_* fields without changing
    the underlying relocation logic.
    """

    if not os.path.exists(RELOCATION_CSV):
        return pd.DataFrame()

    raw = pd.read_csv(RELOCATION_CSV)

    if raw.empty:
        return raw


    # ---------------------------------------------------------
    # SOURCE VILLAGE ID
    # ---------------------------------------------------------

    if "source_village_id" not in raw.columns:

        source_name_col = (
            "source_village"
            if "source_village" in raw.columns
            else "source_village_name"
            if "source_village_name" in raw.columns
            else None
        )

        source_district_col = (
            "source_district"
            if "source_district" in raw.columns
            else "source_district_name"
            if "source_district_name" in raw.columns
            else None
        )

        if source_name_col and source_district_col:

            raw["source_village_id"] = [
                geo_lookup().get(
                    (
                        _norm(name),
                        _norm(district)
                    )
                )
                for name, district in zip(
                    raw[source_name_col],
                    raw[source_district_col]
                )
            ]

        else:

            raw["source_village_id"] = [
                None
            ] * len(raw)


    # ---------------------------------------------------------
    # DESTINATION / CANDIDATE VILLAGE ID
    # ---------------------------------------------------------

    if "dest_village_id" not in raw.columns:

        # Current relocation_engine uses candidate_village.
        dest_name_col = (
            "dest_village"
            if "dest_village" in raw.columns
            else "candidate_village"
            if "candidate_village" in raw.columns
            else "dest_village_name"
            if "dest_village_name" in raw.columns
            else None
        )

        dest_district_col = (
            "dest_district"
            if "dest_district" in raw.columns
            else "candidate_district"
            if "candidate_district" in raw.columns
            else "dest_district_name"
            if "dest_district_name" in raw.columns
            else None
        )

        if dest_name_col and dest_district_col:

            raw["dest_village_id"] = [
                geo_lookup().get(
                    (
                        _norm(name),
                        _norm(district)
                    )
                )
                for name, district in zip(
                    raw[dest_name_col],
                    raw[dest_district_col]
                )
            ]

        else:

            raw["dest_village_id"] = [
                None
            ] * len(raw)


    # ---------------------------------------------------------
    # NORMALISE DESTINATION FIELD NAMES
    # ---------------------------------------------------------

    if (
        "dest_village" not in raw.columns
        and "candidate_village" in raw.columns
    ):
        raw["dest_village"] = raw["candidate_village"]


    if (
        "dest_district" not in raw.columns
        and "candidate_district" in raw.columns
    ):
        raw["dest_district"] = raw["candidate_district"]


    if (
        "dest_risk_score" not in raw.columns
        and "candidate_risk_score" in raw.columns
    ):
        raw["dest_risk_score"] = raw["candidate_risk_score"]


    if (
        "estimated_additional_capacity" not in raw.columns
        and "estimated_capacity" in raw.columns
    ):
        raw["estimated_additional_capacity"] = (
            raw["estimated_capacity"]
        )


    # ---------------------------------------------------------
    # FRONTEND SUITABILITY NAME
    # ---------------------------------------------------------

    if (
        "suitability_score" not in raw.columns
        and "relocation_score" in raw.columns
    ):
        raw["suitability_score"] = (
            raw["relocation_score"]
        )


    # ---------------------------------------------------------
    # DESTINATION RISK CATEGORY
    #
    # The relocation CSV stores the destination risk score,
    # while the risk CSV stores the category.
    # Resolve it from the REAL risk output.
    # ---------------------------------------------------------

    if "dest_risk_category" not in raw.columns:

        try:

            risk_df = load_risk_df()

            category_lookup = {}

            for _, row in risk_df.iterrows():

                key = (
                    _norm(row.get("village_name")),
                    _norm(row.get("district"))
                )

                category_lookup[key] = _clean(
                    row.get("risk_category")
                )


            raw["dest_risk_category"] = [
                category_lookup.get(
                    (
                        _norm(name),
                        _norm(district)
                    )
                )
                for name, district in zip(
                    raw["dest_village"],
                    raw["dest_district"]
                )
            ]

        except Exception:

            raw["dest_risk_category"] = [
                None
            ] * len(raw)


    # ---------------------------------------------------------
    # SOURCE RISK CATEGORY — optional compatibility field
    # ---------------------------------------------------------

    if "source_risk_category" not in raw.columns:

        try:

            risk_df = load_risk_df()

            category_lookup = {}

            for _, row in risk_df.iterrows():

                key = (
                    _norm(row.get("village_name")),
                    _norm(row.get("district"))
                )

                category_lookup[key] = _clean(
                    row.get("risk_category")
                )


            raw["source_risk_category"] = [
                category_lookup.get(
                    (
                        _norm(name),
                        _norm(district)
                    )
                )
                for name, district in zip(
                    raw["source_village"],
                    raw["source_district"]
                )
            ]

        except Exception:

            raw["source_risk_category"] = [
                None
            ] * len(raw)


    return raw


# ============================================================
# VILLAGE RECORD
# ============================================================

def _row_to_village(
    row: dict
) -> dict:

    risk_score = _numeric(
        row.get(
            "risk_score"
        )
    )

    population = _numeric(
        row.get(
            "population"
        )
    )

    children_count = _numeric(
        row.get(
            "children_0_6"
        )
    )


    # UI expects a percentage for children.
    # Risk engine stores Census 0–6 count.
    children_pct = None

    if (
        population
        and children_count is not None
    ):

        children_pct = (
            children_count
            /
            population
            *
            100
        )


    return {

        "village_id":
            str(
                row.get(
                    "village_id"
                )
            )
            if _clean(
                row.get(
                    "village_id"
                )
            ) is not None
            else None,


        "village_name":
            _clean(
                row.get(
                    "village_name"
                )
            ),


        "district":
            _clean(
                row.get(
                    "district"
                )
            ),


        "population":
            population,


        "children_0_6":
            children_pct,


        "illiteracy_rate":
            _numeric(
                row.get(
                    "illiteracy_rate"
                )
            ),


        "sc_st_pct":
            _numeric(
                row.get(
                    "sc_st_pct"
                )
            ),


        "landslide_count":
            _numeric(
                row.get(
                    "landslide_count"
                )
            ),


        "mean_slope_deg":
            _numeric(
                row.get(
                    "mean_slope_deg"
                )
            ),


        "rainfall_hazard":
            _numeric(
                row.get(
                    "rainfall_hazard"
                )
            ),


        "landslide_hazard":
            _numeric(
                row.get(
                    "landslide_hazard"
                )
            ),


        "river_signal":
            _numeric(
                row.get(
                    "river_signal"
                )
            ),


        "road_distance_km":
            _numeric(
                row.get(
                    "road_distance_km"
                )
            ),


        "nearest_rainfall_station":
            _clean(
                row.get(
                    "nearest_rainfall_station"
                )
            ),


        "nearest_river_station":
            _clean(
                row.get(
                    "nearest_river_station"
                )
            ),


        "hazard_score":
            _numeric(
                row.get(
                    "hazard_score"
                )
            ),


        "exposure_score":
            _numeric(
                row.get(
                    "exposure_score"
                )
            ),


        "vulnerability_score":
            _numeric(
                row.get(
                    "vulnerability_score"
                )
            ),


        "risk_score":
            risk_score,


        "risk_category":
            _clean(
                row.get(
                    "risk_category"
                )
            )
            if risk_score is not None
            else INSUFFICIENT,


        "priority":
            _clean(
                row.get(
                    "priority"
                )
            )
            if risk_score is not None
            else INSUFFICIENT,


        "has_complete_risk_profile":
            risk_score is not None,
    }


# ============================================================
# ALL VILLAGES
# ============================================================

def get_all_villages(
    district: str | None = None,
    q: str | None = None
) -> list[dict]:

    df = load_risk_df()


    if district:

        df = df[
            df["district"]
            .fillna("")
            .astype(str)
            .str.lower()
            ==
            district.lower()
        ]


    if q:

        qn = _norm(q)

        df = df[
            df.apply(
                lambda r:
                    qn in _norm(
                        r.get(
                            "village_name"
                        )
                    )
                    or
                    qn in _norm(
                        r.get(
                            "district"
                        )
                    ),
                axis=1
            )
        ]


    return [
        _row_to_village(
            row
        )

        for row
        in df.to_dict(
            orient="records"
        )
    ]


# ============================================================
# SINGLE VILLAGE
# ============================================================

def get_village(
    village_id: str
) -> dict | None:

    df = load_risk_df()


    match = df[
        df["village_id"]
        .astype(str)
        ==
        str(village_id)
    ]


    if match.empty:
        return None


    return _row_to_village(
        match.iloc[
            0
        ].to_dict()
    )


# ============================================================
# DISTRICTS
# ============================================================

def get_districts() -> list[str]:

    return sorted(
        load_risk_df()[
            "district"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


# ============================================================
# GEOJSON FOR LEAFLET
# ============================================================

def get_villages_geojson(
    district: str | None = None
):

    """
    Return village polygons as GeoJSON in EPSG:4326
    for Leaflet.

    Source GIS data is EPSG:7755, so it must be
    reprojected to longitude/latitude.
    """

    if not os.path.exists(
        VILLAGES_GEOJSON
    ):

        return {
            "type": "FeatureCollection",
            "features": []
        }


    try:

        import geopandas as gpd


        # ----------------------------------------------------
        # LOAD REAL GIS VILLAGES
        # ----------------------------------------------------

        gdf = gpd.read_file(
            VILLAGES_GEOJSON,
            engine="pyogrio"
        )


        # ----------------------------------------------------
        # DISTRICT FILTER
        # ----------------------------------------------------

        if district:

            district_column = None


            for column in [
                "district",
                "District",
                "DISTRICT"
            ]:

                if column in gdf.columns:

                    district_column = column
                    break


            if district_column:

                gdf = gdf[
                    gdf[district_column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    ==
                    str(district)
                    .strip()
                    .lower()
                ].copy()


        # ----------------------------------------------------
        # SOURCE CRS
        # ----------------------------------------------------

        if gdf.crs is None:

            gdf = gdf.set_crs(
                "EPSG:7755",
                allow_override=True
            )


        # ----------------------------------------------------
        # CRITICAL:
        # EPSG:7755 -> EPSG:4326
        # ----------------------------------------------------

        if gdf.crs.to_epsg() != 4326:

            gdf = gdf.to_crs(
                "EPSG:4326"
            )


        # ----------------------------------------------------
        # BUILD FEATURES
        # ----------------------------------------------------

        features = []


        for _, row in gdf.iterrows():

            properties = {}


            for column in gdf.columns:

                if column == "geometry":
                    continue


                value = row[column]


                try:

                    if pd.isna(value):
                        value = None

                except Exception:
                    pass


                if hasattr(
                    value,
                    "item"
                ):

                    try:

                        value = value.item()

                    except Exception:
                        pass


                properties[column] = value


            # ------------------------------------------------
            # STANDARD FRONTEND FIELDS
            # ------------------------------------------------

            village_name = (
                properties.get(
                    "village_name"
                )
                or properties.get(
                    "village"
                )
                or properties.get(
                    "Name"
                )
                or "Unknown Village"
            )


            district_name = (
                properties.get(
                    "district"
                )
                or properties.get(
                    "District"
                )
                or "Unknown District"
            )


            village_id = (
                properties.get(
                    "village_id"
                )
                or properties.get(
                    "vlcode"
                )
                or properties.get(
                    "id"
                )
            )


            properties["village_id"] = (
                str(village_id)
                if village_id is not None
                else None
            )


            properties["village_name"] = (
                str(village_name)
            )


            properties["district"] = (
                str(district_name)
            )


            # ------------------------------------------------
            # ADD REAL RISK DATA TO MAP PROPERTIES
            # ------------------------------------------------

            try:

                risk_records = get_all_villages(
                    district=district_name
                )

                risk_lookup = {
                    str(v["village_id"]): v
                    for v in risk_records
                    if v.get("village_id") is not None
                }

                risk = risk_lookup.get(
                    str(properties["village_id"])
                )

                if risk:

                    properties.update({

                        "population":
                            risk.get(
                                "population"
                            ),

                        "priority":
                            risk.get(
                                "priority"
                            ),

                        "hazard_score":
                            risk.get(
                                "hazard_score"
                            ),

                        "rainfall_hazard":
                            risk.get(
                                "rainfall_hazard"
                            ),

                        "landslide_hazard":
                            risk.get(
                                "landslide_hazard"
                            ),

                        "river_signal":
                            risk.get(
                                "river_signal"
                            ),

                        "exposure_score":
                            risk.get(
                                "exposure_score"
                            ),

                        "vulnerability_score":
                            risk.get(
                                "vulnerability_score"
                            ),

                        "risk_score":
                            risk.get(
                                "risk_score"
                            ),

                        "risk_category":
                            risk.get(
                                "risk_category"
                            ),

                        "landslide_count":
                            risk.get(
                                "landslide_count"
                            ),

                        "mean_slope_deg":
                            risk.get(
                                "mean_slope_deg"
                            ),

                        "road_distance_km":
                            risk.get(
                                "road_distance_km"
                            ),

                        "nearest_rainfall_station":
                            risk.get(
                                "nearest_rainfall_station"
                            ),

                        "nearest_river_station":
                            risk.get(
                                "nearest_river_station"
                            ),

                    })

            except Exception as risk_error:

                print(
                    "Risk enrichment warning:",
                    repr(risk_error)
                )


            # ------------------------------------------------
            # GEOMETRY
            # ------------------------------------------------

            geometry = row.geometry


            if geometry is None:
                continue


            features.append({

                "type":
                    "Feature",

                "properties":
                    properties,

                "geometry":
                    geometry.__geo_interface__

            })


        return {

            "type":
                "FeatureCollection",

            "features":
                features

        }


    except Exception as e:

        print(
            "GeoJSON loading error:",
            repr(e)
        )


        return {

            "type":
                "FeatureCollection",

            "features":
                []

        }


# ============================================================
# RELOCATION
# ============================================================

def get_relocation_for_source(
    village_id: str
) -> list[dict]:

    df = load_relocation_df()


    if df.empty:
        return []


    rows = df[
        df["source_village_id"]
        .astype(str)
        ==
        str(village_id)
    ]


    results = []


    for row in rows.to_dict(
        orient="records"
    ):

        row = {
            key: _clean(value)
            for key, value
            in row.items()
        }


        source = get_village(
            village_id
        )


        source_pop = (

            _numeric(
                row.get(
                    "source_population"
                )
            )

            if row.get(
                "source_population"
            ) is not None

            else (
                source["population"]
                if source
                else None
            )

        )


        capacity = _numeric(
            row.get(
                "estimated_additional_capacity"
            )
        )


        row[
            "source_population"
        ] = source_pop


        row[
            "capacity_note"
        ] = None


        if (
            capacity is not None
            and source_pop is not None
        ):

            row[
                "capacity_note"
            ] = (

                "Estimated capacity can accommodate "
                "source population."

                if capacity >= source_pop

                else

                "Estimated capacity is below "
                "source population."

            )


        results.append(
            row
        )


    return results


# ============================================================
# COVERAGE
# ============================================================

def get_coverage() -> dict:

    df = load_risk_df()


    gis_total = int(
        os.getenv(
            "GIS_VILLAGES_TOTAL",
            16920
        )
    )


    census_total = int(
        os.getenv(
            "CENSUS_INTEGRATED_TOTAL",
            8372
        )
    )


    risk_total = int(
        os.getenv(
            "COMPLETE_RISK_TOTAL",
            7831
        )
    )


    def pct(
        a,
        b
    ):

        return (
            round(
                a / b * 100,
                1
            )
            if b
            else 0.0
        )


    return {

        "gis_villages_total":
            gis_total,

        "census_integrated_total":
            census_total,

        "census_integrated_pct":
            pct(
                census_total,
                gis_total
            ),

        "complete_risk_total":
            risk_total,

        "complete_risk_pct":
            pct(
                risk_total,
                gis_total
            ),

        "loaded_rows_in_current_dataset":
            len(df),

    }


# ============================================================
# HEALTH FACILITIES
# ============================================================

def get_health_facilities(
    district: str | None = None
) -> list[dict]:

    if not os.path.exists(
        HEALTH_CSV
    ):

        return []


    df = pd.read_csv(
        HEALTH_CSV
    )


    if (
        district
        and "district" in df.columns
    ):

        df = df[
            df["district"]
            .fillna("")
            .astype(str)
            .str.lower()
            ==
            district.lower()
        ]


    return [

        {
            key: _clean(value)
            for key, value
            in row.items()
        }

        for row
        in df.to_dict(
            orient="records"
        )

    ]