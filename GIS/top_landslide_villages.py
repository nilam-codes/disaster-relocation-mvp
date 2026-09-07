import geopandas as gpd

input_file = "data/processed/villages/villages_landslide_counts.geojson"

villages = gpd.read_file(input_file)

top_villages = villages.sort_values(
    by="landslide_count",
    ascending=False
).head(20)

print("\n===== TOP 20 VILLAGES BY LANDSLIDE COUNT =====")

print(
    top_villages[
        ["village", "vlcode", "landslide_count"]
    ].to_string(index=False)
)

print("\n===== COMPLETE =====")