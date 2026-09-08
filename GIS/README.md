# GIS Processing Pipeline

This folder contains the Python scripts used for GIS data preparation for the disaster relocation project.

## Main Workflow

The GIS pipeline processes village boundaries and associates each village with available hazard and accessibility information.

### 1. Villages

Input:

`data/raw/villages/vb_soi_uk_geojson/vb_soi_uk.GeoJSON`

Processed:

`data/processed/villages/villages_processed.geojson`

The village layer contains approximately 16,920 village features.

---

### 2. Landslides

Input:

`data/raw/landslides/uttarakhand_landslides.csv`

Processing:

- Inspect landslide records
- Convert latitude/longitude to Point geometry
- Match landslide points to village polygons
- Calculate landslide counts per village

Outputs:

- `data/processed/landslides/landslides_processed.geojson`
- `data/processed/villages/villages_landslide_counts.geojson`

Important result:

- 5,331 landslide records
- 5,324 assigned to villages
- 7 records remained outside village polygons

---

### 3. Rainfall

Input:

`data/raw/rainfall/rainfall_tel_hr_uttarakhand_uk_2021_2025.csv`

Processing:

- Clean rainfall records
- Remove negative rainfall values
- Create rainfall station/point layers
- Assign the nearest rainfall station to each village

Outputs:

- `rainfall_processed.csv`
- `rainfall_points.geojson`
- `rainfall_stations.geojson`
- `villages_rainfall_assignment.geojson`

There are 47 rainfall stations.

---

### 4. River

Input:

`data/raw/river/river_discharge_tele_hr_cwc_uk_1970_2025`

Processing:

- Process river monitoring data
- Create river station points
- Assign the nearest river station to each village

Outputs:

- `river_processed.csv`
- `river_stations.geojson`
- `villages_river_assignment.geojson`

---

### 5. Roads

Input:

`data/raw/roads/uttarakhand-latest.osm.pbf`

Processing:

- Extract OSM line features
- Filter road-related highway features
- Check road geometry
- Assign the nearest road to each village

Outputs:

- `roads_filtered.geojson`
- `villages_road_assignment.geojson`

Note:

The full extracted `roads.geojson` is approximately 129 MB and is intentionally not stored in GitHub. It can be regenerated from the raw OSM PBF using `extract_roads.py`.

---

### 6. DEM and Slope

Input:

`data/raw/dem/P5_PAN_CD_N30_250_E079_375_DEM.tif`

Processing:

- Inspect DEM
- Calculate slope in degrees
- Assign mean slope to villages covered by the DEM

Output:

`data/processed/dem/slope_degrees.tif`

Village-level output:

`data/processed/villages/villages_slope_assignment.geojson`

Important limitation:

The available DEM is only one tile and does not cover all of Uttarakhand. Therefore, slope values are available for only a subset of villages. Missing slope values must not be interpreted as zero slope.

---

## Master GIS Layer

The processed village-level datasets are merged into:

`data/processed/villages/villages_master.geojson`

The master layer contains:

- `village`
- `vlcode`
- `district`
- `landslide_count`
- `rainfall_station`
- `rainfall_distance_m`
- `river_station`
- `river_distance_m`
- `highway`
- `road_distance_m`
- `mean_slope_deg`

This master layer is intended to provide the GIS-derived attributes to the project's analysis and application layers.

## Important Notes

- Raw datasets under `data/raw/` should not be modified.
- Processed datasets are stored separately under `data/processed/`.
- No final disaster-risk score is calculated by these GIS scripts.
- GIS outputs provide spatial attributes for downstream analysis.
- Missing slope values are retained because of limited DEM coverage.