import geopandas as gpd

villages_file = "data/processed/villages/villages_processed.geojson"
landslides_file = "data/processed/landslides/landslides_processed.geojson"

# Load datasets
villages = gpd.read_file(villages_file)
landslides = gpd.read_file(landslides_file)

print("\n===== DATA LOADED =====")
print("Number of villages:", len(villages))
print("Number of landslides:", len(landslides))
print("Village CRS:", villages.crs)
print("Landslide CRS:", landslides.crs)

# Match CRS
landslides = landslides.to_crs(villages.crs)

print("\n===== CRS MATCHED =====")
print("Village CRS:", villages.crs)
print("Landslide CRS:", landslides.crs)

# Spatial join
joined = gpd.sjoin(
    landslides,
    villages,
    how="left",
    predicate="within"
)

# Count matches
matched = joined["index_right"].notna().sum()
unmatched = joined["index_right"].isna().sum()

print("\n===== SPATIAL JOIN RESULT =====")
print("Landslides assigned to a village:", matched)
print("Landslides not assigned to a village:", unmatched)
print("Total landslides:", len(landslides))

# Show details of unmatched landslides
unmatched_landslides = joined[joined["index_right"].isna()].copy()

# Keep only the original landslide fields and geometry
original_columns = [
    "Sl_No",
    "Slide_No",
    "Location_Text",
    "Latitude",
    "Longitude",
    "Material",
    "Movement_Type",
    "History",
    "geometry"
]

unmatched_landslides = unmatched_landslides[original_columns]

print("\n===== UNMATCHED LANDSLIDES =====")

if len(unmatched_landslides) > 0:
    columns = [
        "Sl_No",
        "Slide_No",
        "Location_Text",
        "Latitude",
        "Longitude"
    ]

    print(unmatched_landslides[columns].to_string(index=False))

    # Find the nearest village for each unmatched landslide
    nearest = gpd.sjoin_nearest(
        unmatched_landslides,
        villages[["village", "vlcode", "geometry"]],
        how="left",
        distance_col="distance_m"
    )

    print("\n===== NEAREST VILLAGES =====")

    nearest_columns = [
        "Sl_No",
        "Slide_No",
        "village",
        "vlcode",
        "distance_m"
    ]

    print(nearest[nearest_columns].to_string(index=False))

else:
    print("No unmatched landslides.")

print("\n===== COMPLETE =====")