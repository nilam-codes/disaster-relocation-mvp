import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np

villages_file = "data/processed/villages/villages_processed.geojson"
slope_file = "data/processed/dem/slope_degrees.tif"
output_file = "data/processed/villages/villages_slope_assignment.geojson"

villages = gpd.read_file(villages_file)

print("\n===== SLOPE ASSIGNMENT =====")
print("Villages:", len(villages))

with rasterio.open(slope_file) as src:

    # Reproject villages to slope raster CRS
    villages = villages.to_crs(src.crs)

    slope_values = []

    for geometry in villages.geometry:

        try:
            out_image, _ = mask(
                src,
                [geometry],
                crop=True,
                nodata=-9999
            )

            values = out_image[0]
            values = values[values != -9999]
            values = values[np.isfinite(values)]

            if len(values) > 0:
                slope_values.append(float(np.mean(values)))
            else:
                slope_values.append(np.nan)

        except Exception:
            slope_values.append(np.nan)

villages["mean_slope_deg"] = slope_values

# Save result
villages.to_file(output_file, driver="GeoJSON")

print("Villages with slope:", villages["mean_slope_deg"].notna().sum())
print("Villages without slope:", villages["mean_slope_deg"].isna().sum())
print("Output:", output_file)

print("\n===== COMPLETE =====")