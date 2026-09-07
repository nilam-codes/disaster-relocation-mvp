import geopandas as gpd

villages_file = "data/processed/villages/villages_processed.geojson"
landslides_file = "data/processed/landslides/landslides_processed.geojson"
output_file = "data/processed/villages/villages_landslide_counts.geojson"

# Load datasets
villages = gpd.read_file(villages_file)
landslides = gpd.read_file(landslides_file)

print("\n===== DATA LOADED =====")
print("Villages:", len(villages))
print("Landslides:", len(landslides))

# Match CRS
landslides = landslides.to_crs(villages.crs)

# Spatial join
joined = gpd.sjoin(
    landslides,
    villages,
    how="left",
    predicate="within"
)

# Count landslides for each village
landslide_counts = (
    joined.dropna(subset=["index_right"])
    .groupby("index_right")
    .size()
)

# Add count to village dataset
villages["landslide_count"] = (
    villages.index.map(landslide_counts).fillna(0).astype(int)
)

print("\n===== LANDSLIDE COUNTS =====")
print("Villages with at least one landslide:",
      (villages["landslide_count"] > 0).sum())
print("Villages with zero landslides:",
      (villages["landslide_count"] == 0).sum())
print("Total assigned landslides:",
      villages["landslide_count"].sum())

# Save output
villages.to_file(output_file, driver="GeoJSON")

print("\n===== OUTPUT CREATED =====")
print("Output:", output_file)