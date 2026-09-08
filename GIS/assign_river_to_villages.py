import geopandas as gpd

villages_file = "data/processed/villages/villages_processed.geojson"
stations_file = "data/processed/river/river_stations.geojson"
output_file = "data/processed/villages/villages_river_assignment.geojson"

villages = gpd.read_file(villages_file)
stations = gpd.read_file(stations_file)

print("\n===== DATA LOADED =====")
print("Villages:", len(villages))
print("River stations:", len(stations))

# Reproject stations to village CRS for accurate distance calculation
stations = stations.to_crs(villages.crs)

# Find nearest river station
nearest = gpd.sjoin_nearest(
    villages,
    stations[["Station", "geometry"]],
    how="left",
    distance_col="distance_m"
)

# Resolve ties so every village appears exactly once
nearest = nearest.drop_duplicates(
    subset="vlcode",
    keep="first"
)

# Save result
nearest.to_file(output_file, driver="GeoJSON")

print("\n===== RIVER ASSIGNMENT COMPLETE =====")
print("Villages processed:", len(nearest))
print("Villages with station:", nearest["Station"].notna().sum())
print("Maximum distance (m):", nearest["distance_m"].max())
print("Average distance (m):", nearest["distance_m"].mean())
print("Output:", output_file)