import pandas as pd
import geopandas as gpd
import os

input_file = "data/processed/river/river_processed.csv"
output_file = "data/processed/river/river_stations.geojson"

df = pd.read_csv(input_file)

# Keep one record per river station
stations = (
    df[
        ["Station", "Agency", "State", "District", "Latitude", "Longitude"]
    ]
    .drop_duplicates(subset=["Station"])
    .copy()
)

# Create spatial points
gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(
        stations["Longitude"],
        stations["Latitude"]
    ),
    crs="EPSG:4326"
)

os.makedirs("data/processed/river", exist_ok=True)

gdf.to_file(output_file, driver="GeoJSON")

print("\n===== RIVER STATION POINTS CREATED =====")
print("Stations:", len(gdf))
print("Geometry:", gdf.geometry.geom_type.unique().tolist())
print("CRS:", gdf.crs)
print("Output:", output_file)