import geopandas as gpd

input_file = "data/processed/roads/roads_filtered.geojson"

roads = gpd.read_file(input_file)

print("\n===== ROAD GEOMETRY CHECK =====")
print("Features:", len(roads))
print("CRS:", roads.crs)

print("\nGeometry types:")
print(roads.geometry.geom_type.value_counts().to_string())

print("\nEmpty geometries:", roads.geometry.is_empty.sum())
print("Missing geometries:", roads.geometry.isna().sum())

print("\n===== CHECK COMPLETE =====")
