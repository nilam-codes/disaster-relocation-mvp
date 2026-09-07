import geopandas as gpd

# Load village polygons
villages_file = "data/processed/villages/villages_processed.geojson"

# Load landslide points
landslides_file = "data/processed/landslides/landslides_processed.geojson"

villages = gpd.read_file(villages_file)
landslides = gpd.read_file(landslides_file)

print("\n===== BEFORE REPROJECTION =====")
print("Village CRS:", villages.crs)
print("Landslide CRS:", landslides.crs)

# Reproject landslides to the village CRS
landslides = landslides.to_crs(villages.crs)

print("\n===== AFTER REPROJECTION =====")
print("Village CRS:", villages.crs)
print("Landslide CRS:", landslides.crs)

# Check whether the CRS now matches
if villages.crs == landslides.crs:
    print("\nCRS MATCH: Yes")
else:
    print("\nCRS MATCH: No")

print("\nNumber of villages:", len(villages))
print("Number of landslides:", len(landslides))