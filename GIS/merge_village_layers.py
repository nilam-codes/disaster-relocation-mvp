import geopandas as gpd

base = "data/processed/villages/"

landslide_file = base + "villages_landslide_counts.geojson"
rainfall_file = base + "villages_rainfall_assignment.geojson"
river_file = base + "villages_river_assignment.geojson"
road_file = base + "villages_road_assignment.geojson"
slope_file = base + "villages_slope_assignment.geojson"

output_file = base + "villages_master.geojson"

# Load existing processed layers
landslides = gpd.read_file(landslide_file)
rainfall = gpd.read_file(rainfall_file)
river = gpd.read_file(river_file)
roads = gpd.read_file(road_file)
slope = gpd.read_file(slope_file)

print("\n===== LOADED EXISTING LAYERS =====")
print("Villages:", len(landslides))
print("Rainfall:", len(rainfall))
print("River:", len(river))
print("Roads:", len(roads))
print("Slope:", len(slope))

# Keep only the new information from each layer
rainfall_data = rainfall[["vlcode", "Station", "distance_m"]].copy()
rainfall_data = rainfall_data.rename(
    columns={
        "Station": "rainfall_station",
        "distance_m": "rainfall_distance_m"
    }
)

river_data = river[["vlcode", "Station", "distance_m"]].copy()
river_data = river_data.rename(
    columns={
        "Station": "river_station",
        "distance_m": "river_distance_m"
    }
)

road_data = roads[["vlcode", "highway", "road_distance_m"]].copy()

slope_data = slope[["vlcode", "mean_slope_deg"]].copy()

# Start with landslide layer
master = landslides.copy()

# Merge existing results
master = master.merge(rainfall_data, on="vlcode", how="left")
master = master.merge(river_data, on="vlcode", how="left")
master = master.merge(road_data, on="vlcode", how="left")
master = master.merge(slope_data, on="vlcode", how="left")

# Save master layer
master.to_file(output_file, driver="GeoJSON")

print("\n===== MASTER VILLAGE LAYER COMPLETE =====")
print("Villages:", len(master))
print("Landslide column:", "landslide_count" in master.columns)
print("Rainfall column:", "rainfall_distance_m" in master.columns)
print("River column:", "river_distance_m" in master.columns)
print("Road column:", "road_distance_m" in master.columns)
print("Slope column:", "mean_slope_deg" in master.columns)
print("Output:", output_file)