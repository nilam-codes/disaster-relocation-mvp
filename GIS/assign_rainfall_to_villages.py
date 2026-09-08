import geopandas as gpd

villages_file = "data/processed/villages/villages_processed.geojson"
stations_file = "data/processed/rainfall/rainfall_stations.geojson"

villages = gpd.read_file(villages_file)
stations = gpd.read_file(stations_file)

print("\n===== DATA LOADED =====")
print("Villages:", len(villages))
print("Rainfall stations:", len(stations))

# Use the village CRS for distance calculations
stations = stations.to_crs(villages.crs)

# Find the nearest rainfall station for every village
nearest = gpd.sjoin_nearest(
    villages,
    stations[["Station", "geometry"]],
    how="left",
    distance_col="distance_m"
)

print("\n===== NEAREST RAINFALL STATIONS =====")
print("Villages processed:", len(nearest))
print("Villages with station:", nearest["Station"].notna().sum())
print("Maximum distance (m):", nearest["distance_m"].max())
print("Average distance (m):", nearest["distance_m"].mean())

print("\nSample:")
print(
    nearest[["village", "vlcode", "Station", "distance_m"]]
    .head(10)
    .to_string(index=False)
)

print("\n===== COMPLETE =====")