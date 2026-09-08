import geopandas as gpd

input_file = "data/processed/villages/villages_master.geojson"
output_file = "data/processed/villages/villages_gis.geojson"

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
    "mean_slope_deg",
    "geometry"
]

gdf = gdf[columns].copy()

gdf.to_file(output_file, driver="GeoJSON")

print("Created:", output_file)
print("Features:", len(gdf))
print("CRS:", gdf.crs)
print("Columns:", len(gdf.columns))