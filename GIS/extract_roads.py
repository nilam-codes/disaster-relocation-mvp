import geopandas as gpd

input_file = "data/raw/roads/uttarakhand-latest.osm.pbf"
output_file = "data/processed/roads/roads.geojson"

roads = gpd.read_file(input_file, layer="lines")

print("\n===== ROADS EXTRACTED =====")
print("Road features:", len(roads))
print("CRS:", roads.crs)
print("Geometry:", roads.geometry.geom_type.unique())
print("Columns:", roads.columns.tolist())

roads.to_file(output_file, driver="GeoJSON")

print("\nOutput:", output_file)