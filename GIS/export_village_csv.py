import geopandas as gpd

input_file = "data/processed/villages/villages_master.geojson"
output_file = "data/processed/villages/villages_gis.csv"

gdf = gpd.read_file(input_file)

columns = [
    "village",
    "vlcode",
    "district",
    "landslide_count",
    "rainfall_station",
    "rainfall_distance_m",
    "river_station",
    "river_distance_m",
    "highway",
    "road_distance_m",
    "mean_slope_deg"
]

df = gdf[columns].copy()

df.to_csv(output_file, index=False)

print("Created:", output_file)
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nColumns:")
print(list(df.columns))