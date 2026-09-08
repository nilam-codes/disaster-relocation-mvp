import pandas as pd
import geopandas as gpd

input_file = "data/processed/rainfall/rainfall_processed.csv"
output_file = "data/processed/rainfall/rainfall_points.geojson"

df = pd.read_csv(input_file)

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["Longitude"],
        df["Latitude"]
    ),
    crs="EPSG:4326"
)

gdf.to_file(output_file, driver="GeoJSON")

print("\n===== RAINFALL POINTS CREATED =====")
print("Rows:", len(gdf))
print("Stations:", gdf["Station"].nunique())
print("CRS:", gdf.crs)
print("Output:", output_file)