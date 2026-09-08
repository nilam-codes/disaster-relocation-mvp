import geopandas as gpd

villages_file = "data/processed/villages/villages_processed.geojson"
landslides_file = "data/processed/landslides/landslides_processed.geojson"
output_file = "data/processed/villages/villages_landslide_counts.geojson"

villages = gpd.read_file(villages_file)
landslides = gpd.read_file(landslides_file)

print("\n===== DATA LOADED =====")
print("Villages:", len(villages))
print("Landslides:", len(landslides))

# Match CRS
landslides = landslides.to_crs(villages.crs)

# Spatially assign landslides to villages
joined = gpd.sjoin(
    landslides,
    villages[["vlcode", "geometry"]],
    how="left",
    predicate="within"
)

# Count landslides per village
counts = (
    joined.dropna(subset=["vlcode"])
    .groupby("vlcode")
    .size()
    .reset_index(name="landslide_count")
)

# Add counts to all villages
villages = villages.merge(
    counts,
    on="vlcode",
    how="left"
)

# Villages with no recorded landslide get 0
villages["landslide_count"] = (
    villages["landslide_count"]
    .fillna(0)
    .astype(int)
)

villages.to_file(output_file, driver="GeoJSON")

print("\n===== LANDSLIDE COUNTS COMPLETE =====")
print("Villages:", len(villages))
print(
    "Villages with landslides:",
    (villages["landslide_count"] > 0).sum()
)
print(
    "Villages with zero landslides:",
    (villages["landslide_count"] == 0).sum()
)
print("Maximum landslides in one village:", villages["landslide_count"].max())
print("Total assigned landslides:", villages["landslide_count"].sum())
print("Output:", output_file)

print("\nTop 10 villages:")
print(
    villages[
        ["village", "vlcode", "landslide_count"]
    ]
    .sort_values("landslide_count", ascending=False)
    .head(10)
    .to_string(index=False)
)