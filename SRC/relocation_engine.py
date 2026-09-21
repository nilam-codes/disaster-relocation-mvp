import os
import pandas as pd
import geopandas as gpd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================


VILLAGE_FILE = "data/raw/villages/vb_soi_uk_geojson/vb_soi_uk.GeoJSON"

RISK_FILE = "data/processed/final/uttarakhand_village_risk.csv"

HEALTH_FILE = "data/processed/health_facilities_uttarakhand.csv"

OUTPUT_FILE = "data/processed/final/relocation_recommendations.csv"

METRIC_CRS = "EPSG:7755"


# ============================================================
# HELPER FUNCTION
# ============================================================

def minmax_score(series):
    """
    Convert values to a 0-100 score.
    """
    series = pd.to_numeric(series, errors="coerce")

    if series.notna().sum() == 0:
        return pd.Series(0, index=series.index)

    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series(100, index=series.index)

    return ((series - min_value) / (max_value - min_value)) * 100


# ============================================================
# STEP 1 — LOAD DATA
# ============================================================

print("\n==============================")
print("STEP 1: LOADING DATA")
print("==============================")

if not os.path.exists(VILLAGE_FILE):
    raise FileNotFoundError(f"Village file not found: {VILLAGE_FILE}")

if not os.path.exists(RISK_FILE):
    raise FileNotFoundError(f"Risk file not found: {RISK_FILE}")

villages = gpd.read_file(VILLAGE_FILE)

risk = pd.read_csv(RISK_FILE)

if not os.path.exists(HEALTH_FILE):
    raise FileNotFoundError(f"Health facility file not found: {HEALTH_FILE}")

health = pd.read_csv(HEALTH_FILE)

print(f"Health facilities: {len(health):,}")

print(f"Village polygons: {len(villages):,}")
print(f"Risk records: {len(risk):,}")

print("\nRisk columns:")
print(list(risk.columns))


# ============================================================
# STEP 2 — PREPARE VILLAGE DATA
# ============================================================

print("\n==============================")
print("STEP 2: PREPARING VILLAGES")
print("==============================")

villages = villages.reset_index(drop=True)

villages["village_index"] = villages.index

# Make sure geometry has correct CRS
if villages.crs is None:
    villages = villages.set_crs(METRIC_CRS)

villages_metric = villages.to_crs(METRIC_CRS)

# Create representative point / centroid
villages_metric["point_geometry"] = villages_metric.geometry.centroid

print("Village geometry prepared.")


# ============================================================
# STEP 3 — CREATE JOIN KEYS
# ============================================================

print("\n==============================")
print("STEP 3: JOINING RISK DATA")
print("==============================")


def clean_text(value):
    if pd.isna(value):
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )


# Village fields
if "village" in villages.columns:
    villages["village_key"] = villages["village"].apply(clean_text)
elif "Village" in villages.columns:
    villages["village_key"] = villages["Village"].apply(clean_text)
elif "name" in villages.columns:
    villages["village_key"] = villages["name"].apply(clean_text)
elif "Name" in villages.columns:
    villages["village_key"] = villages["Name"].apply(clean_text)
else:
    raise ValueError(
        "Could not find village-name column in GeoJSON."
    )


# District field
if "district" in villages.columns:
    villages["district_key"] = villages["district"].apply(clean_text)
elif "District" in villages.columns:
    villages["district_key"] = villages["District"].apply(clean_text)
elif "district_name" in villages.columns:
    villages["district_key"] = villages["district_name"].apply(clean_text)
else:
    villages["district_key"] = ""


# Risk keys
if "village_key" not in risk.columns:

    if "village" in risk.columns:
        risk["village_key"] = risk["village"].apply(clean_text)

    elif "Village" in risk.columns:
        risk["village_key"] = risk["Village"].apply(clean_text)

    elif "village_name" in risk.columns:
        risk["village_key"] = risk["village_name"].apply(clean_text)

    else:
        raise ValueError(
            "Could not find village name column in risk CSV."
        )


if "district_key" not in risk.columns:

    if "district" in risk.columns:
        risk["district_key"] = risk["district"].apply(clean_text)

    elif "District" in risk.columns:
        risk["district_key"] = risk["District"].apply(clean_text)

    elif "district_name" in risk.columns:
        risk["district_key"] = risk["district_name"].apply(clean_text)

    else:
        risk["district_key"] = ""


# ============================================================
# STEP 4 — FIND IMPORTANT RISK COLUMNS
# ============================================================

print("\n==============================")
print("STEP 4: CHECKING RISK FIELDS")
print("==============================")


def find_column(df, possible_names, required=True):

    for name in possible_names:
        if name in df.columns:
            return name

    if required:
        raise ValueError(
            f"Could not find required column. Tried: {possible_names}"
        )

    return None


risk_score_col = find_column(
    risk,
    [
        "risk_score",
        "Risk Score",
        "overall_risk_score"
    ]
)

population_col = find_column(
    risk,
    [
        "census_population_2011",
        "total_population_village",
        "population",
        "total_population",
        "Total Population Person",
        "total_population_person"
    ],
    required=False
)

priority_col = find_column(
    risk,
    [
        "relocation_priority",
        "Relocation Priority",
        "priority"
    ],
    required=False
)

category_col = find_column(
    risk,
    [
        "risk_category",
        "Risk Category",
        "category"
    ],
    required=False
)


print(f"Risk score column: {risk_score_col}")
print(f"Population column: {population_col}")
print(f"Priority column: {priority_col}")
print(f"Risk category column: {category_col}")


# ============================================================
# STEP 5 — MERGE RISK WITH VILLAGES
# ============================================================

print("\n==============================")
print("STEP 5: MERGING DATA")
print("==============================")

risk_columns = [
    "village_key",
    "district_key",
    risk_score_col
]

if population_col:
    risk_columns.append(population_col)

if priority_col:
    risk_columns.append(priority_col)

if category_col:
    risk_columns.append(category_col)

risk_subset = risk[risk_columns].copy()

# Remove duplicate village records if any
risk_subset = risk_subset.drop_duplicates(
    subset=["village_key", "district_key"]
)

village_data = villages.merge(
    risk_subset,
    on=["village_key", "district_key"],
    how="left"
)

print(
    "Villages with risk information:",
    village_data[risk_score_col].notna().sum()
)


# ============================================================
# STEP 6 — POPULATION
# ============================================================

print("\n==============================")
print("STEP 6: POPULATION / CAPACITY")
print("==============================")

if population_col:

    village_data["current_population"] = pd.to_numeric(
        village_data[population_col],
        errors="coerce"
    ).fillna(0)

else:

    # Try village geometry population field
    possible_population_fields = [
        "total_population",
        "total_population_person",
        "population",
        "Population",
        "Total_Population"
    ]

    population_field = None

    for field in possible_population_fields:
        if field in village_data.columns:
            population_field = field
            break

    if population_field:

        village_data["current_population"] = pd.to_numeric(
            village_data[population_field],
            errors="coerce"
        ).fillna(0)

    else:

        village_data["current_population"] = 0


# ------------------------------------------------------------
# IMPORTANT:
# This is only a planning proxy for MVP.
# It is NOT an official carrying-capacity value.
#
# We assume that a relocation site could accommodate
# approximately 25% of its current population as additional
# population.
# ------------------------------------------------------------

village_data["estimated_capacity"] = (
    village_data["current_population"] * 0.25
)

print(
    "Estimated capacity calculated using 25% planning proxy."
)

print(
    "Total estimated additional capacity:",
    round(village_data["estimated_capacity"].sum(), 2)
)


# ============================================================
# STEP 7 — IDENTIFY SAFE CANDIDATE SITES
# ============================================================

print("\n==============================")
print("STEP 7: CANDIDATE SITES")
print("==============================")

village_data["risk_numeric"] = pd.to_numeric(
    village_data[risk_score_col],
    errors="coerce"
)

# Candidate site:
# - has risk information
# - risk score below 50 (lower-risk site)
# - has some population/capacity
#
# This is a planning filter, not a legal declaration of safety.

candidate_sites = village_data[
    (village_data["risk_numeric"].notna())
    &
    (village_data["risk_numeric"] < 50)
    &
    (village_data["estimated_capacity"] > 0)
].copy()

candidate_sites = candidate_sites.sort_values("risk_numeric")

print(f"Candidate relocation sites (risk < 50): {len(candidate_sites):,}")


# ============================================================
# STEP 8 — SITE SAFETY SCORE
# ============================================================

print("\n==============================")
print("STEP 8: SITE SUITABILITY")
print("==============================")

# Lower risk = higher safety

candidate_sites["safety_score"] = (
    100 - candidate_sites["risk_numeric"]
)

# Higher capacity = better

candidate_sites["capacity_score"] = minmax_score(
    candidate_sites["estimated_capacity"]
)

# Suitability:
# 60% safety
# 40% capacity

candidate_sites["site_suitability_score"] = (
    0.60 * candidate_sites["safety_score"]
    +
    0.40 * candidate_sites["capacity_score"]
)

print("Site suitability scores calculated.")

# ============================================================
# STEP 8B — HEALTHCARE ACCESS
# ============================================================

print("\n==============================")
print("STEP 8B: HEALTHCARE ACCESS")
print("==============================")

health = health.dropna(
    subset=["longitude", "latitude"]
).copy()

health_gdf = gpd.GeoDataFrame(
    health,
    geometry=gpd.points_from_xy(
        health["longitude"],
        health["latitude"]
    ),
    crs="EPSG:4326"
)

health_gdf = health_gdf.to_crs(METRIC_CRS)

health_gdf["facility_type"] = (
    health_gdf["other_tags"]
    .fillna("")
    .str.extract(
        r'amenity.*?=>.*?([a-zA-Z]+)',
        expand=False
    )
    .str.lower()
)

facility_weights = {
    "hospital": 1.0,
    "clinic": 0.7,
    "doctors": 0.6,
    "pharmacy": 0.5,
    "blood": 0.5,
    "dentist": 0.2
}

health_gdf["facility_weight"] = (
    health_gdf["facility_type"]
    .map(facility_weights)
    .fillna(0)
)

health_gdf = health_gdf[
    health_gdf["facility_weight"] > 0
].copy()

print(
    f"Usable healthcare facilities: "
    f"{len(health_gdf):,}"
)

HEALTH_RADIUS = 25000

health_points = health_gdf.geometry

health_scores = []

for _, candidate in candidate_sites.iterrows():

    candidate_point = candidate.geometry.centroid

    distances = health_points.distance(
        candidate_point
    )

    nearby = health_gdf.loc[
        distances <= HEALTH_RADIUS
    ].copy()

    if len(nearby) == 0:
        health_scores.append(0.0)
        continue

    nearby_distances = distances.loc[
        nearby.index
    ]

    distance_factor = (
        1 - nearby_distances / HEALTH_RADIUS
    ).clip(lower=0)

    weighted_access = (
        nearby["facility_weight"]
        * distance_factor
    ).sum()

    health_scores.append(
        weighted_access
    )

candidate_sites["healthcare_access_score"] = (
    health_scores
)

candidate_sites["healthcare_access_score"] = (
    minmax_score(
        candidate_sites["healthcare_access_score"]
    )
)

print(
    "Healthcare access scores calculated."
)

print(
    candidate_sites["healthcare_access_score"]
    .describe()
)

# ============================================================
# STEP 9 — FIND VILLAGES NEEDING RELOCATION
# ============================================================

print("\n==============================")
print("STEP 9: RELOCATION SOURCES")
print("==============================")

source_villages = village_data[
    village_data["risk_numeric"].notna()
    &
    (village_data["risk_numeric"] >= 50)
].copy()

source_villages = (
    source_villages
    .sort_values("risk_numeric", ascending=False)
    .head(100)
)

print(
    f"Villages requiring relocation assessment: {len(source_villages):,}"
)


# ============================================================
# STEP 10 — CALCULATE RELOCATION OPTIONS
# ============================================================

print("\n==============================")
print("STEP 10: GENERATING OPTIONS")
print("==============================")

recommendations = []


if len(source_villages) == 0:

    print(
        "\nNo villages currently meet the risk >= 50 "
        "relocation assessment threshold."
    )

else:

    # Work on a mutable candidate table so that capacity consumed
    # by one relocation is unavailable to later relocations.
    candidate_points = candidate_sites.copy()

    candidate_points = candidate_points.to_crs(METRIC_CRS)

    candidate_points["candidate_point"] = (
        candidate_points.geometry.centroid
    )

    # Maximum distance used for relative distance score.
    MAX_DISTANCE = 100000  # 100 km

    for _, source in source_villages.iterrows():

        source_population = float(
            source["current_population"]
        )

        source_point = (
            villages_metric.loc[
                source["village_index"],
                "point_geometry"
            ]
        )

        options = []

        # Recalculate capacity score using the CURRENT remaining
        # capacities before evaluating this source village.
        candidate_points["capacity_score_current"] = minmax_score(
            candidate_points["estimated_capacity"]
        )

        for _, candidate in candidate_points.iterrows():

            # Do not relocate a village to itself.
            if (
                candidate["village_key"]
                == source["village_key"]
                and
                candidate["district_key"]
                == source["district_key"]
            ):
                continue

            candidate_capacity = float(
                candidate["estimated_capacity"]
            )

            # A destination with zero remaining capacity is not usable.
            if candidate_capacity <= 0:
                continue

            candidate_point = candidate["candidate_point"]

            distance_m = source_point.distance(
                candidate_point
            )

            distance_km = distance_m / 1000

            # Distance score:
            # 0 km = 100
            # 100 km or more = 0
            distance_score = max(
                0,
                100 * (
                    1 - distance_m / MAX_DISTANCE
                )
            )

            capacity_score = float(
                candidate["capacity_score_current"]
            )

            safety_score = float(
                candidate["safety_score"]
            )

            healthcare_score = float(
                candidate["healthcare_access_score"]
            )

            relocation_score = (
                0.35 * safety_score
                +
                0.25 * capacity_score
                +
                0.20 * distance_score
                +
                0.20 * healthcare_score
            )

            enough_capacity = (
                candidate_capacity
                >=
                source_population
            )

            options.append(
                {
                    "source_village":
                        source.get("village", ""),

                    "source_district":
                        source.get("district", ""),

                    "source_population":
                        source_population,

                    "source_risk_score":
                        source["risk_numeric"],

                    "candidate_village":
                        candidate.get("village", ""),

                    "candidate_district":
                        candidate.get("district", ""),

                    "candidate_population":
                        candidate["current_population"],

                    "estimated_capacity":
                        candidate_capacity,

                    "candidate_risk_score":
                        candidate["risk_numeric"],

                    "safety_score":
                        safety_score,

                    "capacity_score":
                        capacity_score,

                    "distance_km":
                        distance_km,

                    "distance_score":
                        distance_score,

                    "healthcare_access_score":
                        healthcare_score,

                    "relocation_score":
                        relocation_score,

                    "enough_capacity":
                        enough_capacity
                }
            )

        if not options:
            continue

        options_df = pd.DataFrame(options)

        # Prefer sites that can accommodate the whole source
        # population. If none can, use the best available site.
        enough_capacity_options = options_df[
            options_df["enough_capacity"] == True
        ]

        if len(enough_capacity_options) > 0:

            best = (
                enough_capacity_options
                .sort_values(
                    "relocation_score",
                    ascending=False
                )
                .iloc[0]
            )

        else:

            best = (
                options_df
                .sort_values(
                    "relocation_score",
                    ascending=False
                )
                .iloc[0]
            )

        # Record the selected relocation.
        recommendations.append(best.to_dict())

        # Consume capacity from the selected destination.
        candidate_index = candidate_points[
            (
                candidate_points["village_key"]
                == best["candidate_village"]
            )
            &
            (
                candidate_points["district_key"]
                == best["candidate_district"]
            )
        ].index

        if len(candidate_index) > 0:

            candidate_points.loc[
                candidate_index,
                "estimated_capacity"
            ] = (
                candidate_points.loc[
                    candidate_index,
                    "estimated_capacity"
                ]
                - source_population
            ).clip(lower=0)




# ============================================================
# STEP 11 — SAVE RESULTS
# ============================================================

print("\n==============================")
print("STEP 11: SAVING RESULTS")
print("==============================")

recommendations_df = pd.DataFrame(
    recommendations
)

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

recommendations_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Relocation recommendations saved to:\n{OUTPUT_FILE}"
)

print(
    f"Recommendations generated: "
    f"{len(recommendations_df):,}"
)

print(
    "NOTE: Relocation destinations are lower-risk planning "
    "candidates (risk < 50), not legally certified safe sites."
)


# ============================================================
# STEP 12 — SHOW SAMPLE
# ============================================================

if len(recommendations_df) > 0:

    print("\n==============================")
    print("TOP RELOCATION RECOMMENDATIONS")
    print("==============================")

    display_columns = [
        "source_village",
        "source_district",
        "source_population",
        "source_risk_score",
        "candidate_village",
        "candidate_district",
        "estimated_capacity",
        "candidate_risk_score",
        "distance_km",
        "relocation_score"
    ]

    available_display_columns = [
        col for col in display_columns
        if col in recommendations_df.columns
    ]

    print(
        recommendations_df[
            available_display_columns
        ]
        .sort_values(
            "relocation_score",
            ascending=False
        )
        .head(10)
        .to_string(index=False)
    )

else:

    print("\nNo relocation recommendations generated.")

print("\n==============================")
print("RELOCATION ENGINE COMPLETE")
print("==============================")