import geopandas as gpd
import folium

# --------------------------------------------------
# FILES
# --------------------------------------------------

village_file = "data/processed/villages/villages_gis.geojson"
landslide_file = "data/processed/landslides/landslides_processed.geojson"
rainfall_file = "data/processed/rainfall/rainfall_stations.geojson"
river_file = "data/processed/river/river_stations.geojson"
roads_file = "data/processed/roads/roads_filtered.geojson"

output_file = "data/processed/villages/villages_gis_map.html"


# --------------------------------------------------
# LOAD VILLAGES
# --------------------------------------------------

villages = gpd.read_file(village_file)
villages = villages.to_crs(epsg=4326)

center = villages.geometry.union_all().centroid

m = folium.Map(
    location=[center.y, center.x],
    zoom_start=8,
    tiles="OpenStreetMap"
)


# --------------------------------------------------
# VILLAGE LAYER
# --------------------------------------------------

village_layer = folium.FeatureGroup(
    name="Villages",
    show=True
)

folium.GeoJson(
    villages,
    tooltip=folium.GeoJsonTooltip(
        fields=[
            "village",
            "district",
            "landslide_count",
            "rainfall_station",
            "rainfall_distance_m",
            "river_station",
            "river_distance_m",
            "highway",
            "road_distance_m",
            "mean_slope_deg"
        ],
        aliases=[
            "Village",
            "District",
            "Landslides",
            "Rainfall Station",
            "Rainfall Distance (m)",
            "River Station",
            "River Distance (m)",
            "Road",
            "Road Distance (m)",
            "Mean Slope (°)"
        ]
    )
).add_to(village_layer)

village_layer.add_to(m)


# --------------------------------------------------
# LANDSLIDE LAYER
# --------------------------------------------------

landslides = gpd.read_file(landslide_file)
landslides = landslides.to_crs(epsg=4326)

landslide_layer = folium.FeatureGroup(
    name="Landslides",
    show=True
)

for _, row in landslides.iterrows():

    if row.geometry is None or row.geometry.is_empty:
        continue

    folium.CircleMarker(
        location=[
            row.geometry.y,
            row.geometry.x
        ],
        radius=3,
        tooltip=f"Landslide: {row.get('Slide_No', 'Unknown')}"
    ).add_to(landslide_layer)

landslide_layer.add_to(m)


# --------------------------------------------------
# RAINFALL STATIONS
# --------------------------------------------------

rainfall = gpd.read_file(rainfall_file)
rainfall = rainfall.to_crs(epsg=4326)

rainfall_layer = folium.FeatureGroup(
    name="Rainfall Stations",
    show=True
)

for _, row in rainfall.iterrows():

    if row.geometry is None or row.geometry.is_empty:
        continue

    folium.CircleMarker(
        location=[
            row.geometry.y,
            row.geometry.x
        ],
        radius=5,
        tooltip=f"Rainfall Station: {row.get('Station', 'Unknown')}"
    ).add_to(rainfall_layer)

rainfall_layer.add_to(m)


# --------------------------------------------------
# RIVER STATIONS
# --------------------------------------------------

river = gpd.read_file(river_file)
river = river.to_crs(epsg=4326)

river_layer = folium.FeatureGroup(
    name="River Stations",
    show=True
)

for _, row in river.iterrows():

    if row.geometry is None or row.geometry.is_empty:
        continue

    folium.CircleMarker(
        location=[
            row.geometry.y,
            row.geometry.x
        ],
        radius=5,
        tooltip=f"River Station: {row.get('Station', 'Unknown')}"
    ).add_to(river_layer)

river_layer.add_to(m)


# --------------------------------------------------
# ROADS
# --------------------------------------------------

roads = gpd.read_file(roads_file)
roads = roads.to_crs(epsg=4326)

road_layer = folium.FeatureGroup(
    name="Roads",
    show=False
)

folium.GeoJson(
    roads
).add_to(road_layer)

road_layer.add_to(m)


# --------------------------------------------------
# LAYER CONTROL
# --------------------------------------------------

folium.LayerControl(
    collapsed=False
).add_to(m)


# --------------------------------------------------
# SAVE MAP
# --------------------------------------------------

m.save(output_file)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("Created:", output_file)
print("Villages:", len(villages))
print("Landslides:", len(landslides))
print("Rainfall stations:", len(rainfall))
print("River stations:", len(river))
print("Road features:", len(roads))