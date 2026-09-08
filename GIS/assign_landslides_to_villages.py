import geopandas as gpd

villages_file = "data/processed/villages/villages_processed.geojson"
landslides_file = "data/processed/landslides/landslides_processed.geojson"

villages = gpd.read_file(villages_file)
landslides = gpd.read_file(landslides_file)

print("\n===== DATA LOADED =====")
print("Villages:", len(villages))
print("Landslides:", len(landslides))

# Match CRS
landslides = landslides.to_crs(villages.crs)

# Assign each landslide point to the village polygon containing it
joined = gpd.sjoin(
    landslides,
    villages[["vlcode", "village", "geometry"]],
    how="left",
    predicate="within"
)

matched = joined["index_right"].notna().sum()
unmatched = joined["index_right"].isna().sum()

print("\n===== LANDSLIDE ASSIGNMENT COMPLETE =====")
print("Landslides processed:", len(joined))
print("Landslides assigned to village:", matched)
print("Landslides not assigned:", unmatched)

print("\nSample:")
print(
    joined[
        ["Slide_No", "Location_Text", "vlcode", "village"]
    ].head(10).to_string(index=False)
)