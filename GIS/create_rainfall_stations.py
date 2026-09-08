import geopandas as gpd

input_file = "data/processed/rainfall/rainfall_points.geojson"
output_file = "data/processed/rainfall/rainfall_stations.geojson"

gdf = gpd.read_file(input_file)

stations = gdf[
    ["Station", "Agency", "State", "District", "Latitude", "Longitude", "geometry"]
].drop_duplicates(subset=["Station"])

stations.to_file(output_file, driver="GeoJSON")

print("\n===== UNIQUE RAINFALL STATIONS =====")
print("Unique stations:", len(stations))
print("Geometry:", stations.geometry.geom_type.unique().tolist())
print("CRS:", stations.crs)
print("Output:", output_file)