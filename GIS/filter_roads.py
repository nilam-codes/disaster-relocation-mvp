import geopandas as gpd
import os

input_file = "data/processed/roads/roads.geojson"
output_file = "data/processed/roads/roads_filtered.geojson"

roads = gpd.read_file(input_file)

# Keep features that have an OSM highway classification
roads_filtered = roads[roads["highway"].notna()].copy()

# Keep only actual road/path-related highway types
allowed_types = [
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
    "unclassified",
    "residential",
    "living_street",
    "service",
    "track",
    "path",
    "footway",
    "pedestrian",
    "steps",
    "bridleway",
    "road",
    "construction",
    "busway",
    "cycleway"
]

roads_filtered = roads_filtered[
    roads_filtered["highway"].isin(allowed_types)
].copy()

os.makedirs(os.path.dirname(output_file), exist_ok=True)

roads_filtered.to_file(output_file, driver="GeoJSON")

print("\n===== ROAD FILTERING COMPLETE =====")
print("Original features:", len(roads))
print("Filtered road features:", len(roads_filtered))
print("CRS:", roads_filtered.crs)
print("Output:", output_file)

print("\nHighway types kept:")
print(
    roads_filtered["highway"]
    .value_counts()
    .to_string()
)