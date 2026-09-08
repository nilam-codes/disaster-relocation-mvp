import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

input_file = "data/raw/dem/P5_PAN_CD_N30_250_E079_375_DEM.tif"
output_file = "data/processed/dem/slope_degrees.tif"

target_crs = "EPSG:32644"  # UTM Zone 44N

with rasterio.open(input_file) as src:

    transform, width, height = calculate_default_transform(
        src.crs,
        target_crs,
        src.width,
        src.height,
        *src.bounds
    )

    elevation = np.empty((height, width), dtype=np.float32)

    reproject(
        source=rasterio.band(src, 1),
        destination=elevation,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=target_crs,
        resampling=Resampling.bilinear
    )

    pixel_size_x = transform.a
    pixel_size_y = abs(transform.e)

    # Calculate elevation change in X and Y directions
    dz_dx, dz_dy = np.gradient(
        elevation,
        pixel_size_x,
        pixel_size_y
    )

    # Calculate slope in degrees
    slope = np.degrees(
        np.arctan(
            np.sqrt(dz_dx ** 2 + dz_dy ** 2)
        )
    )

    profile = src.profile.copy()
    profile.update(
        driver="GTiff",
        height=height,
        width=width,
        transform=transform,
        crs=target_crs,
        count=1,
        dtype="float32",
        nodata=-9999
    )

    slope[np.isnan(slope)] = -9999

    with rasterio.open(output_file, "w", **profile) as dst:
        dst.write(slope.astype(np.float32), 1)

print("\n===== SLOPE CALCULATION COMPLETE =====")
print("CRS:", target_crs)
print("Slope minimum:", round(float(slope[slope != -9999].min()), 2), "degrees")
print("Slope maximum:", round(float(slope[slope != -9999].max()), 2), "degrees")
print("Output:", output_file)