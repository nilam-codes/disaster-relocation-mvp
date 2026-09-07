import geopandas as gpd
from pathlib import Path


# --------------------------------------------------
# 1. Input file
# --------------------------------------------------

input_file = Path(
    "data/raw/villages/vb_soi_uk_geojson/vb_soi_uk.GeoJSON"
)


# --------------------------------------------------
# 2. Output file
# --------------------------------------------------

output_file = Path(
    "data/processed/villages/villages_processed.geojson"
)


# --------------------------------------------------
# 3. Load the original village data
# --------------------------------------------------

print("Loading village GeoJSON...")

villages = gpd.read_file(input_file)

print("Village data loaded.")
print("Number of features:", len(villages))
print("CRS:", villages.crs)


# --------------------------------------------------
# 4. Check geometry validity
# --------------------------------------------------

invalid = ~villages.geometry.is_valid

print("Invalid geometries before repair:", invalid.sum())


# --------------------------------------------------
# 5. Repair only invalid geometries
# --------------------------------------------------

if invalid.any():
    villages.loc[invalid, "geometry"] = (
        villages.loc[invalid, "geometry"].make_valid()
    )

print("Invalid geometries after repair:",
      (~villages.geometry.is_valid).sum())


# --------------------------------------------------
# 6. Create output directory
# --------------------------------------------------

output_file.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 7. Save processed dataset
# --------------------------------------------------

villages.to_file(
    output_file,
    driver="GeoJSON"
)


# --------------------------------------------------
# 8. Final confirmation
# --------------------------------------------------

print("\nProcessed village dataset created successfully!")
print("Output:", output_file)
print("Features:", len(villages))
print("CRS:", villages.crs)
print("Invalid geometries:", (~villages.geometry.is_valid).sum())