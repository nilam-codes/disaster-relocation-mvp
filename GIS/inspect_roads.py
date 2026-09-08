import geopandas as gpd

roads_file = "data/processed/roads/roads.geojson"

roads = gpd.read_file(roads_file)

print("\n===== ROAD DATA INSPECTION =====")
print("Total features:", len(roads))
print("CRS:", roads.crs)

print("\nHighway types:")
print(roads["highway"].value_counts(dropna=False).head(30).to_string())

print("\nNon-road feature counts:")
print("Waterways:", roads["waterway"].notna().sum())
print("Railways:", roads["railway"].notna().sum())
print("Aerialways:", roads["aerialway"].notna().sum())
print("Barriers:", roads["barrier"].notna().sum())

print("\n===== INSPECTION COMPLETE =====")