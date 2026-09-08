import geopandas as gpd

villages_file = "data/processed/villages/villages_processed.geojson"
roads_file = "data/processed/roads/roads_filtered.geojson"
output_file = "data/processed/villages/villages_road_assignment.geojson"

villages = gpd.read_file(villages_file)
roads = gpd.read_file(roads_file)

print("\n===== DATA LOADED =====")
print("Villages:", len(villages))
print("Roads:", len(roads))

# Use a projected CRS so distance is measured in meters
villages_projected = villages.to_crs("EPSG:32644")
roads_projected = roads.to_crs("EPSG:32644")

# Keep only geometry needed for nearest-road calculation
roads_projected = roads_projected[["highway", "geometry"]]

result = gpd.sjoin_nearest(
    villages_projected,
    roads_projected,
    how="left",
    distance_col="road_distance_m"
)

# Remove duplicate village rows if a tie produced multiple nearest roads
result = result.drop_duplicates(subset="vlcode")

# Convert back to geographic CRS
result = result.to_crs("EPSG:4326")

result.to_file(output_file, driver="GeoJSON")

print("\n===== ROAD ASSIGNMENT COMPLETE =====")
print("Villages processed:", len(result))
print("Villages with road:", result["road_distance_m"].notna().sum())
print("Maximum distance (m):", result["road_distance_m"].max())
print("Average distance (m):", result["road_distance_m"].mean())
print("Output:", output_file)

print("\nSample:")
print(
    result[["village", "vlcode", "highway", "road_distance_m"]]
    .head(10)
    .to_string(index=False)
)