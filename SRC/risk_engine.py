import geopandas as gpd
import pandas as pd
import numpy as np
import os


# ============================================================
# CONFIGURATION
# ============================================================

VILLAGE_FILE = (
    "data/raw/villages/"
    "vb_soi_uk_geojson/vb_soi_uk.GeoJSON"
)

RAINFALL_FILE = (
    "data/raw/rainfall/"
    "rainfall_tel_hr_uttarakhand_uk_2021_2025.csv"
)

RIVER_FILE = (
    "data/raw/river/"
    "river_discharge_tele_hr_cwc_uk_1970_2025.csv"
)

LANDSLIDE_FILE = (
    "data/processed/landslides/"
    "uttarakhand_landslides.csv"
)

CENSUS_FILE = (
    "data/processed/final/"
    "uttarakhand_census_4districts.csv"
)

OUTPUT_DIR = "data/processed/final"

OUTPUT_FILE = (
    "data/processed/final/"
    "uttarakhand_village_risk.csv"
)

# Projected CRS for Uttarakhand distance/spatial operations
METRIC_CRS = "EPSG:7755"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def check_file(path):
    if os.path.exists(path):
        print(f"✓ Found: {path}")
        return True

    print(f"✗ NOT FOUND: {path}")
    return False


def minmax_score(series):
    """
    Convert numeric values into a 0-100 score.
    """
    series = pd.to_numeric(series, errors="coerce")

    result = pd.Series(np.nan, index=series.index, dtype=float)

    valid = series.notna()

    if valid.sum() == 0:
        return result

    minimum = series[valid].min()
    maximum = series[valid].max()

    if maximum == minimum:
        result.loc[valid] = 0.0
        return result

    result.loc[valid] = (
        (series.loc[valid] - minimum)
        / (maximum - minimum)
        * 100
    )

    return result


def clean_key(series):
    """
    Standardize village/district names for joining.
    """
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )


# ============================================================
# STEP 1 — LOAD DATA
# ============================================================

print("\n" + "=" * 70)
print("STEP 1 — LOADING DATA")
print("=" * 70)


# ---------------- Village data ----------------

if not check_file(VILLAGE_FILE):
    raise FileNotFoundError(VILLAGE_FILE)

villages = gpd.read_file(VILLAGE_FILE)

villages.columns = villages.columns.str.strip()

villages["total_population_village"] = pd.to_numeric(
    villages["total_population_village"],
    errors="coerce"
).fillna(0)

print(f"Villages loaded: {len(villages)}")
print(f"Village CRS: {villages.crs}")


# ---------------- Rainfall ----------------

if not check_file(RAINFALL_FILE):
    raise FileNotFoundError(RAINFALL_FILE)

rainfall = pd.read_csv(RAINFALL_FILE)

rainfall.columns = rainfall.columns.str.strip()

rainfall["Latitude"] = pd.to_numeric(
    rainfall["Latitude"],
    errors="coerce"
)

rainfall["Longitude"] = pd.to_numeric(
    rainfall["Longitude"],
    errors="coerce"
)

rainfall["rainfall_mm"] = pd.to_numeric(
    rainfall["Telemetry Hourly Rainfall (mm)"],
    errors="coerce"
)

rainfall = rainfall.dropna(
    subset=["Latitude", "Longitude", "rainfall_mm"]
)

# Remove physically invalid negative rainfall values
rainfall = rainfall[rainfall["rainfall_mm"] >= 0]

# Remove repeated telemetry ceiling/saturation value
rainfall = rainfall[rainfall["rainfall_mm"] < 511.5]

print(f"Rainfall records: {len(rainfall)}")

# ---------------- River ----------------

if not check_file(RIVER_FILE):
    raise FileNotFoundError(RIVER_FILE)

river = pd.read_csv(RIVER_FILE)

river.columns = river.columns.str.strip()

river["Latitude"] = pd.to_numeric(
    river["Latitude"],
    errors="coerce"
)

river["Longitude"] = pd.to_numeric(
    river["Longitude"],
    errors="coerce"
)

river["discharge"] = pd.to_numeric(
    river["Telemetry Hourly River Water Discharge (m3/sec)"],
    errors="coerce"
)

river = river.dropna(
    subset=["Latitude", "Longitude", "discharge"]
)

print(f"River records: {len(river)}")


# ---------------- Landslides ----------------

if not check_file(LANDSLIDE_FILE):
    raise FileNotFoundError(LANDSLIDE_FILE)

landslides = pd.read_csv(LANDSLIDE_FILE)

landslides.columns = landslides.columns.str.strip()

landslides["Latitude"] = pd.to_numeric(
    landslides["Latitude"],
    errors="coerce"
)

landslides["Longitude"] = pd.to_numeric(
    landslides["Longitude"],
    errors="coerce"
)

landslides = landslides.dropna(
    subset=["Latitude", "Longitude"]
)

print(f"Landslide records: {len(landslides)}")


# ============================================================
# STEP 2 — HAZARD ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("STEP 2 — HAZARD ANALYSIS")
print("=" * 70)


# ============================================================
# STEP 2A — PREPARE VILLAGE CENTROIDS
# ============================================================

print("\n" + "-" * 60)
print("STEP 2A — PREPARING VILLAGE LOCATIONS")
print("-" * 60)

# Convert village polygons to metric CRS first.
villages_metric = villages.to_crs(METRIC_CRS)

# Calculate centroid correctly in projected CRS.
village_points_metric = villages_metric.copy()

village_points_metric["geometry"] = (
    villages_metric.geometry.centroid
)

print(
    "Village points created:",
    len(village_points_metric)
)


# ============================================================
# STEP 2B — RAINFALL HAZARD
# ============================================================

print("\n" + "-" * 60)
print("STEP 2B — CALCULATING RAINFALL HAZARD")
print("-" * 60)

rainfall_points = gpd.GeoDataFrame(
    rainfall,
    geometry=gpd.points_from_xy(
        rainfall["Longitude"],
        rainfall["Latitude"]
    ),
    crs="EPSG:4326"
)

rainfall_station = (
    rainfall_points
    .groupby("Station", as_index=False)
    .agg(
        latitude=("Latitude", "first"),
        longitude=("Longitude", "first"),
        max_hourly_rainfall=("rainfall_mm", lambda x: x.quantile(0.95)),
        total_recorded_rainfall=("rainfall_mm", "sum")
    )
)

rainfall_station_points = gpd.GeoDataFrame(
    rainfall_station,
    geometry=gpd.points_from_xy(
        rainfall_station["longitude"],
        rainfall_station["latitude"]
    ),
    crs="EPSG:4326"
)

rainfall_metric = rainfall_station_points.to_crs(
    METRIC_CRS
)

# Nearest station.
# No artificial distance cutoff is used here because the
# rainfall network is sparse. Distance is retained for QA.
rainfall_match = gpd.sjoin_nearest(
    village_points_metric[
        ["geometry"]
    ],
    rainfall_metric[
        [
            "max_hourly_rainfall",
            "total_recorded_rainfall",
            "geometry"
        ]
    ],
    how="left",
    distance_col="rainfall_station_distance_m"
)

# sjoin_nearest can return duplicate rows in tie cases.
# Keep one result per village.
rainfall_match = (
    rainfall_match
    .groupby(rainfall_match.index)
    .first()
)

rainfall_values = pd.to_numeric(
    rainfall_match["max_hourly_rainfall"],
    errors="coerce"
)

villages["max_hourly_rainfall"] = (
    rainfall_values
    .reindex(villages.index)
    .values
)

villages["rainfall_station_distance_km"] = (
    pd.to_numeric(
        rainfall_match[
            "rainfall_station_distance_m"
        ],
        errors="coerce"
    )
    .reindex(villages.index)
    .values
    / 1000
)

villages["rainfall_hazard_score"] = minmax_score(
    villages["max_hourly_rainfall"]
)

print(
    "Rainfall stations:",
    len(rainfall_station)
)

print(
    "Villages with rainfall data:",
    villages["max_hourly_rainfall"].notna().sum()
)

print(
    "Median rainfall station distance (km):",
    round(
        villages["rainfall_station_distance_km"].median(),
        2
    )
)


# ============================================================
# STEP 2C — RIVER / FLOOD INDICATOR
# ============================================================

print("\n" + "-" * 60)
print("STEP 2C — CALCULATING RIVER HAZARD")
print("-" * 60)

river_points = gpd.GeoDataFrame(
    river,
    geometry=gpd.points_from_xy(
        river["Longitude"],
        river["Latitude"]
    ),
    crs="EPSG:4326"
)

river_station = (
    river_points
    .groupby("Station", as_index=False)
    .agg(
        latitude=("Latitude", "first"),
        longitude=("Longitude", "first"),
        max_discharge=("discharge", "max"),
        mean_discharge=("discharge", "mean")
    )
)

river_station_points = gpd.GeoDataFrame(
    river_station,
    geometry=gpd.points_from_xy(
        river_station["longitude"],
        river_station["latitude"]
    ),
    crs="EPSG:4326"
)

river_metric = river_station_points.to_crs(
    METRIC_CRS
)

river_match = gpd.sjoin_nearest(
    village_points_metric[
        ["geometry"]
    ],
    river_metric[
        [
            "max_discharge",
            "mean_discharge",
            "geometry"
        ]
    ],
    how="left",
    distance_col="river_station_distance_m"
)

# Keep one match per village.
river_match = (
    river_match
    .groupby(river_match.index)
    .first()
)

river_values = pd.to_numeric(
    river_match["max_discharge"],
    errors="coerce"
)

villages["max_river_discharge"] = (
    river_values
    .reindex(villages.index)
    .values
)

villages["river_station_distance_km"] = (
    pd.to_numeric(
        river_match[
            "river_station_distance_m"
        ],
        errors="coerce"
    )
    .reindex(villages.index)
    .values
    / 1000
)

villages["river_hazard_score"] = minmax_score(
    villages["max_river_discharge"]
)

print(
    "River stations:",
    len(river_station)
)

print(
    "Villages with river data:",
    villages["max_river_discharge"].notna().sum()
)

print(
    "Median river station distance (km):",
    round(
        villages["river_station_distance_km"].median(),
        2
    )
)


# ============================================================
# STEP 2D — LANDSLIDE HAZARD
# ============================================================

print("\n" + "-" * 60)
print("STEP 2D — CALCULATING LANDSLIDE HAZARD")
print("-" * 60)

landslide_points = gpd.GeoDataFrame(
    landslides,
    geometry=gpd.points_from_xy(
        landslides["Longitude"],
        landslides["Latitude"]
    ),
    crs="EPSG:4326"
)

landslide_metric = landslide_points.to_crs(
    METRIC_CRS
)

# IMPORTANT:
# Count only landslide points physically inside each
# village polygon.
#
# The previous code grouped the spatial join incorrectly
# and produced impossible counts.
joined_landslides = gpd.sjoin(
    villages_metric[
        ["geometry"]
    ],
    landslide_metric[
        ["geometry"]
    ],
    how="left",
    predicate="contains"
)

# index_left = village index
# index_right = landslide index
landslide_count = (
    joined_landslides
    .dropna(subset=["index_right"])
    .groupby(level=0)
    .size()
)

villages["nearby_landslide_count"] = (
    landslide_count
    .reindex(villages.index)
    .fillna(0)
    .astype(int)
)

villages["landslide_hazard_score"] = minmax_score(
    villages["nearby_landslide_count"]
)

print(
    "Landslide points:",
    len(landslides)
)

print(
    "Villages containing landslide points:",
    (
        villages["nearby_landslide_count"] > 0
    ).sum()
)

print(
    "Total landslide points assigned:",
    villages["nearby_landslide_count"].sum()
)


# ============================================================
# STEP 2E — COMBINED HAZARD SCORE
# ============================================================

print("\n" + "-" * 60)
print("STEP 2E — COMBINING HAZARD INDICATORS")
print("-" * 60)

# MVP expert-defined weights.
# These are NOT official government weights.
#
# Landslide = 50%
# Rainfall  = 30%
# River     = 20%

villages["hazard_score"] = (
    0.60 * villages["landslide_hazard_score"].fillna(0)
    + 0.40 * villages["rainfall_hazard_score"].fillna(0)
)

print("\nHazard score statistics:")
print(
    villages["hazard_score"].describe()
)


# ============================================================
# STEP 2F — TOP HAZARD VILLAGES
# ============================================================

print("\n" + "-" * 60)
print("TOP 10 HAZARD VILLAGES")
print("-" * 60)

top_hazard = villages.sort_values(
    "hazard_score",
    ascending=False
)

print(
    top_hazard[
        [
            "district",
            "subdistric",
            "village",
            "rainfall_hazard_score",
            "river_hazard_score",
            "landslide_hazard_score",
            "hazard_score"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# STEP 2 COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("STEP 2 COMPLETE")
print("=" * 70)


# ============================================================
# STEP 3 — EXPOSURE + VULNERABILITY
# ============================================================

print("\n" + "=" * 70)
print("STEP 3 — EXPOSURE + VULNERABILITY")
print("=" * 70)


# ============================================================
# STEP 3A — LOAD COMBINED CENSUS
# ============================================================

if not check_file(CENSUS_FILE):
    raise FileNotFoundError(CENSUS_FILE)

census = pd.read_csv(
    CENSUS_FILE
)

census.columns = census.columns.str.strip()

print(
    "Combined Census records:",
    len(census)
)


# ============================================================
# STEP 3B — PREPARE CENSUS VILLAGES
# ============================================================

print("\n" + "-" * 60)
print("STEP 3B — PREPARING CENSUS VILLAGES")
print("-" * 60)


def clean_village_code(series):
    """
    Standardize Census and GIS village codes for joining.
    """
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .str.zfill(6)
    )


# The combined Census file already contains village-level
# records from Dehradun, Pauri Garhwal, Almora and Tehri Garhwal.
census_villages = census.copy()

census_villages["village_code_clean"] = clean_village_code(
    census_villages["village_code"]
)

villages["village_code_clean"] = clean_village_code(
    villages["vlcode"]
)

print(
    "Census village records:",
    len(census_villages)
)

print(
    "Unique Census village codes:",
    census_villages["village_code_clean"].nunique()
)


# Convert demographic fields to numeric.
census_fields = [
    "population",
    "children_0_6",
    "sc_population",
    "st_population",
    "illiterates"
]

for col in census_fields:
    census_villages[col] = pd.to_numeric(
        census_villages[col],
        errors="coerce"
    )


# ============================================================
# STEP 3C — JOIN CENSUS WITH GIS VILLAGES
# ============================================================

print("\n" + "-" * 60)
print("STEP 3C — JOINING CENSUS WITH VILLAGES")
print("-" * 60)


census_lookup = census_villages[
    [
        "village_code_clean",
        "population",
        "children_0_6",
        "sc_population",
        "st_population",
        "illiterates"
    ]
].drop_duplicates(
    subset=["village_code_clean"]
)


villages = villages.merge(
    census_lookup,
    on="village_code_clean",
    how="left"
)


# Rename Census fields so they are clearly separated
# from the original GIS village attributes.
villages = villages.rename(
    columns={
        "population": "census_population_2011",
        "children_0_6": "census_children_0_6",
        "sc_population": "census_sc_population",
        "st_population": "census_st_population",
        "illiterates": "census_illiterates"
    }
)


matched = villages[
    "census_population_2011"
].notna().sum()


print(
    "Villages matched with Census:",
    matched
)

print(
    "Villages without Census:",
    len(villages) - matched
)

print(
    "Census coverage:",
    round(
        matched / len(villages) * 100,
        2
    ),
    "%"
)


# ============================================================
# STEP 3D — POPULATION EXPOSURE
# ============================================================


# ============================================================

print("\n" + "-" * 60)
print("STEP 3D — CALCULATING POPULATION EXPOSURE")
print("-" * 60)

# Population exposure using percentile-based scaling.
# This reduces the effect of extreme population outliers.

population = pd.to_numeric(
    villages["census_population_2011"],
    errors="coerce"
)

p95 = population.quantile(0.95)

villages["population_exposure_score"] = (
    (population / p95) * 100
).clip(0, 100)

print(
    villages[
        "population_exposure_score"
    ].describe()
)


# ============================================================
# STEP 3E — VULNERABILITY INDICATORS
# ============================================================

print("\n" + "-" * 60)
print("STEP 3E — CALCULATING VULNERABILITY")
print("-" * 60)

census_population = pd.to_numeric(
    villages["census_population_2011"],
    errors="coerce"
)

children = pd.to_numeric(
    villages["census_children_0_6"],
    errors="coerce"
)

sc_population = pd.to_numeric(
    villages["census_sc_population"],
    errors="coerce"
)

st_population = pd.to_numeric(
    villages["census_st_population"],
    errors="coerce"
)

illiterate = pd.to_numeric(
    villages["census_illiterates"],
    errors="coerce"
)


# Children 0-6 percentage
villages["children_0_6_pct"] = np.where(
    census_population > 0,
    children / census_population * 100,
    np.nan
)


# Illiteracy percentage
villages["illiteracy_pct"] = np.where(
    census_population > 0,
    illiterate / census_population * 100,
    np.nan
)


# SC/ST proportion
villages["sc_st_pct"] = np.where(
    census_population > 0,
    (
        (sc_population + st_population)
        / census_population
        * 100
    ),
    np.nan
)


# Normalize vulnerability indicators
villages["children_vulnerability_score"] = (
    minmax_score(
        villages["children_0_6_pct"]
    )
)

villages["illiteracy_vulnerability_score"] = (
    minmax_score(
        villages["illiteracy_pct"]
    )
)

villages["social_vulnerability_score"] = (
    minmax_score(
        villages["sc_st_pct"]
    )
)


# ============================================================
# STEP 3F — COMBINED VULNERABILITY
# ============================================================

print("\n" + "-" * 60)
print("STEP 3F — COMBINING VULNERABILITY")
print("-" * 60)

villages["vulnerability_score"] = (
    villages["children_vulnerability_score"] * 0.33
    + villages["illiteracy_vulnerability_score"] * 0.33
    + villages["social_vulnerability_score"] * 0.34
)

census_available = (
    census_population.notna()
    & (census_population > 0)
)

villages.loc[
    ~census_available,
    "vulnerability_score"
] = np.nan


print(
    "Villages with vulnerability score:",
    villages["vulnerability_score"].notna().sum()
)

print("\nVulnerability statistics:")
print(
    villages["vulnerability_score"].describe()
)


# ============================================================
# STEP 3 COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("STEP 3 COMPLETE")
print("=" * 70)


# ============================================================
# STEP 4 — FINAL RISK + RELOCATION PRIORITY
# ============================================================

print("\n" + "=" * 70)
print("STEP 4 — FINAL RISK + RELOCATION PRIORITY")
print("=" * 70)


# ------------------------------------------------------------
# 4A — FINAL RISK SCORE
# ------------------------------------------------------------

print("\n" + "-" * 60)
print("STEP 4A — CALCULATING FINAL RISK")
print("-" * 60)

# Risk model:
#
# Hazard       = 50%
# Exposure     = 20%
# Vulnerability = 30%
#
# These are transparent MVP weights,
# NOT official government weights.

villages["risk_score"] = np.nan

risk_available = (
    villages["hazard_score"].notna()
    & villages["population_exposure_score"].notna()
    & villages["vulnerability_score"].notna()
)

villages.loc[
    risk_available,
    "risk_score"
] = (
    0.50 * villages.loc[
        risk_available,
        "hazard_score"
    ]
    + 0.20 * villages.loc[
        risk_available,
        "population_exposure_score"
    ]
    + 0.30 * villages.loc[
        risk_available,
        "vulnerability_score"
    ]
)

print(
    "Villages with complete risk score:",
    villages["risk_score"].notna().sum()
)


# ------------------------------------------------------------
# 4B — RISK CATEGORY
# ------------------------------------------------------------

def risk_category(score):

    if pd.isna(score):
        return "Insufficient Data"

    if score < 25:
        return "Low"

    if score < 50:
        return "Moderate"

    if score < 75:
        return "High"

    return "Very High"


villages["risk_category"] = (
    villages["risk_score"]
    .apply(risk_category)
)


# ------------------------------------------------------------
# 4C — RELOCATION PRIORITY
# ------------------------------------------------------------

print("\n" + "-" * 60)
print("STEP 4C — CALCULATING RELOCATION PRIORITY")
print("-" * 60)

# Priority is intentionally separate from risk.
#
# High risk + larger exposed population
# + higher vulnerability = higher urgency.

villages["relocation_priority_score"] = np.nan

priority_available = (
    villages["risk_score"].notna()
    & villages["population_exposure_score"].notna()
    & villages["vulnerability_score"].notna()
)

villages.loc[
    priority_available,
    "relocation_priority_score"
] = (
    0.50 * villages.loc[
        priority_available,
        "risk_score"
    ]
    + 0.25 * villages.loc[
        priority_available,
        "population_exposure_score"
    ]
    + 0.25 * villages.loc[
        priority_available,
        "vulnerability_score"
    ]
)


def relocation_priority(score):

    if pd.isna(score):
        return "Insufficient Data"

    if score >= 75:
        return "Immediate"

    if score >= 50:
        return "Short-Term"

    if score >= 25:
        return "Medium-Term"

    return "Monitor"


villages["relocation_priority"] = (
    villages["relocation_priority_score"]
    .apply(relocation_priority)
)


# ------------------------------------------------------------
# 4D — RED-ZONE CANDIDATE
# ------------------------------------------------------------

villages["red_zone_candidate"] = (
    villages["risk_score"] >= 75
)

villages["red_zone_candidate"] = (
    villages["red_zone_candidate"]
    .map({
        True: "Yes - Authority Review",
        False: "No"
    })
)


# ============================================================
# STEP 4E — DISPLAY TOP PRIORITY VILLAGES
# ============================================================

print("\n" + "-" * 60)
print("TOP RELOCATION PRIORITY VILLAGES")
print("-" * 60)

top_priority = villages.sort_values(
    "relocation_priority_score",
    ascending=False
)

print(
    top_priority[
        [
            "district",
            "subdistric",
            "village",
            "total_population_village",
            "hazard_score",
            "population_exposure_score",
            "vulnerability_score",
            "risk_score",
            "risk_category",
            "relocation_priority"
        ]
    ]
    .head(15)
    .to_string(index=False)
)


# ============================================================
# STEP 4 COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("STEP 4 COMPLETE")
print("=" * 70)

print("\nRisk category distribution:")

print(
    villages["risk_category"]
    .value_counts(dropna=False)
)


print("\nRelocation priority distribution:")

print(
    villages["relocation_priority"]
    .value_counts(dropna=False)
)


# ============================================================
# STEP 5 — SAVE FINAL DATASET
# ============================================================

print("\n" + "=" * 70)
print("STEP 5 — SAVING FINAL RISK DATASET")
print("=" * 70)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ------------------------------------------------------------
# Keep useful columns for application
# ------------------------------------------------------------

final_columns = [
    "district",
    "subdistric",
    "village",

    "total_population_village",
    "census_population_2011",

    "max_hourly_rainfall",
    "rainfall_station_distance_km",
    "rainfall_hazard_score",

    "max_river_discharge",
    "river_station_distance_km",
    "river_hazard_score",

    "nearby_landslide_count",
    "landslide_hazard_score",

    "hazard_score",

    "population_exposure_score",

    "children_0_6_pct",
    "illiteracy_pct",
    "sc_st_pct",

    "children_vulnerability_score",
    "illiteracy_vulnerability_score",
    "social_vulnerability_score",

    "vulnerability_score",

    "risk_score",
    "risk_category",

    "relocation_priority_score",
    "relocation_priority",

    "red_zone_candidate"
]


# Add columns only if they exist.
final_columns = [
    col
    for col in final_columns
    if col in villages.columns
]

final_data = villages[
    final_columns
].copy()


# Save CSV
final_data.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    f"\n✓ FINAL DATASET SAVED:"
)

print(
    OUTPUT_FILE
)

print(
    "Rows:",
    len(final_data)
)

print(
    "Columns:",
    len(final_data.columns)
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DISASTER RELOCATION RISK ENGINE COMPLETE")
print("=" * 70)

print(
    "\nPipeline:"
)

print(
    "REAL DATA"
    " → HAZARD"
    " → EXPOSURE"
    " → VULNERABILITY"
    " → RISK"
    " → PRIORITY"
)

print(
    "\nHazards:"
)

print(
    "✓ Landslide"
)

print(
    "✓ Rainfall"
)

print(
    "✓ River / flood indicator"
)

print(
    "\nFinal output:"
)

print(
    "✓ Risk score"
)

print(
    "✓ Risk category"
)

print(
    "✓ Relocation priority"
)

print(
    "✓ Red-zone candidate flag"
)

print(
    "\nNOTE:"
)

print(
    "Red-zone candidate means very-high-risk area "
    "requiring authority review."
)

print(
    "It does NOT represent a legal declaration "
    "that the village is uninhabitable."
)

print(
    "\nIntegrated demographic coverage:",
    villages["census_population_2011"].notna().sum(),
    "of",
    len(villages),
    "villages"
)

print(
    "\n✓ RISK ENGINE FINISHED SUCCESSFULLY"
)