import pandas as pd
import geopandas as gpd

# Input CSV
input_file = "data/raw/landslides/uttarakhand_landslides.csv"

# Output GeoJSON
output_file = "data/processed/landslides/landslides_processed.geojson"

# Read landslide CSV
df = pd.read_csv(input_file)

# Convert CSV records into geographic points
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["Longitude"],
        df["Latitude"]
    ),
    crs="EPSG:4326"
)

# Save as GeoJSON
gdf.to_file(output_file, driver="GeoJSON")

print("\nLandslide point dataset created successfully!")
print("Number of landslides:", len(gdf))
print("CRS:", gdf.crs)
print("Output:", output_file)