import geopandas as gpd
import pandas as pd


# ============================================================
# FILES
# ============================================================

VILLAGE_FILE = "data/raw/villages/vb_soi_uk_geojson/vb_soi_uk.GeoJSON"
RISK_FILE = "data/processed/final/uttarakhand_village_risk.csv"


# ============================================================
# HISTORICAL EVENTS
# Coordinates are reference locations for documented events.
# ============================================================

EVENTS = [
    ("Maldevta Flash Flood 2022", 30.399108, 78.132034),
    ("Raini/Rishiganga Flash Flood 2021", 30.48723, 79.69800),
    ("Tapovan Flash Flood 2021", 30.49290, 79.63042),
    ("Kedarnath Disaster 2013", 30.73390, 79.06690),
    ("Swala Landslide 2021", 29.25522, 80.05875),
    ("Lambagarh Landslide", 30.65411, 79.51658),
    ("Sukhi Top Landslide 2021", 31.00710, 78.70740),
]


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("HISTORICAL VALIDATION")
print("=" * 70)

villages = gpd.read_file(VILLAGE_FILE)
risk = pd.read_csv(RISK_FILE)

print(f"Village polygons: {len(villages)}")
print(f"Risk records: {len(risk)}")


# ============================================================
# PREPARE COORDINATES
# ============================================================

event_points = gpd.GeoDataFrame(
    EVENTS,
    columns=["historical_event", "latitude", "longitude"],
    geometry=gpd.points_from_xy(
        [e[2] for e in EVENTS],
        [e[1] for e in EVENTS]
    ),
    crs="EPSG:4326"
)

event_points = event_points.to_crs(villages.crs)


# ============================================================
# FIND NEAREST VILLAGE
# ============================================================

results = []

for _, event in event_points.iterrows():

    distances = villages.geometry.distance(event.geometry)

    nearest_index = distances.idxmin()

    village = villages.loc[nearest_index]

    results.append({
        "historical_event": event["historical_event"],
        "event_latitude": event["latitude"],
        "event_longitude": event["longitude"],
        "district": village["district"],
        "subdistric": village["subdistric"],
        "village": village["village"],
        "distance_m": distances.loc[nearest_index],
    })


historical = pd.DataFrame(results)


# ============================================================
# JOIN MODEL RESULTS
# ============================================================

model_columns = [
    "district",
    "subdistric",
    "village",
    "hazard_score",
    "risk_score",
    "risk_category",
    "nearby_landslide_count",
]

historical = historical.merge(
    risk[model_columns],
    on=["district", "subdistric", "village"],
    how="left"
)


# ============================================================
# DISPLAY HISTORICAL VALIDATION
# ============================================================

print("\n")
print("HISTORICAL EVENT → MODEL RESULT")
print("-" * 70)

display_columns = [
    "historical_event",
    "district",
    "village",
    "distance_m",
    "hazard_score",
    "risk_score",
    "risk_category",
    "nearby_landslide_count",
]

print(
    historical[display_columns]
    .to_string(index=False)
)


# ============================================================
# VALIDATION SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

total = len(historical)

with_hazard = historical["hazard_score"].notna().sum()

print(f"Historical events tested: {total}")
print(f"Events with model hazard score: {with_hazard}")

# Moderate or higher = hazard/risk signal detected
moderate_or_higher = historical[
    historical["risk_category"].isin(["Moderate", "High"])
]

complete_risk = historical["risk_score"].notna()

if complete_risk.sum() > 0:

    detected = historical[
        complete_risk
        & historical["risk_category"].isin(["Moderate", "High"])
    ]

    coverage = len(detected) / complete_risk.sum() * 100

    print(
        f"Moderate/High coverage among complete-risk events: "
        f"{coverage:.1f}%"
    )

else:

    print(
        "Overall-risk coverage cannot be calculated because "
        "historical events lack complete Census-linked risk data."
    )


# ============================================================
# LOW-RISK CONTROL SAMPLE
# ============================================================

print("\n")
print("=" * 70)
print("LOW-RISK CONTROL SAMPLE")
print("=" * 70)

complete = risk[
    risk["risk_score"].notna()
    & risk["risk_category"].isin(["Low", "Moderate", "High"])
].copy()

low_risk = complete[
    complete["risk_category"] == "Low"
].sort_values("risk_score")

control = low_risk.head(10)

print(
    control[
        [
            "district",
            "subdistric",
            "village",
            "hazard_score",
            "risk_score",
            "risk_category",
            "nearby_landslide_count",
        ]
    ].to_string(index=False)
)

print("\n")
print("Control statistics:")
print(f"Low-risk control villages: {len(control)}")

if len(control) > 0:

    print(
        f"Average hazard score: "
        f"{control['hazard_score'].mean():.2f}"
    )

    print(
        f"Average risk score: "
        f"{control['risk_score'].mean():.2f}"
    )

    print(
        f"Average nearby landslides: "
        f"{control['nearby_landslide_count'].mean():.2f}"
    )


# ============================================================
# SAVE RESULTS
# ============================================================

OUTPUT_FILE = "data/processed/final/historical_validation_results.csv"

historical.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n")
print(f"✓ Validation results saved:")
print(OUTPUT_FILE)