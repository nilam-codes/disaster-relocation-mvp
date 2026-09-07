import geopandas as gpd
import folium


# Load processed village data
file_path = "data/processed/villages/villages_processed.geojson"

villages = gpd.read_file(file_path)

print("Village data loaded.")
print("Number of villages:", len(villages))
print("CRS:", villages.crs)


# Convert to WGS84 for web mapping
villages_map = villages.to_crs(epsg=4326)

print("Converted CRS:", villages_map.crs)


# Get the center of Uttarakhand village data
center = villages_map.geometry.union_all().centroid

map_object = folium.Map(
    location=[center.y, center.x],
    zoom_start=8
)


# Add village boundaries with clickable information
folium.GeoJson(
    villages_map,
    name="Uttarakhand Villages",
    tooltip=folium.GeoJsonTooltip(
        fields=["village", "district"],
        aliases=["Village:", "District:"],
        sticky=False
    ),
    popup=folium.GeoJsonPopup(
        fields=["village", "district"],
        aliases=["Village:", "District:"],
        localize=True
    )
).add_to(map_object)


# Add layer control
folium.LayerControl().add_to(map_object)


# Save map
output_file = "data/processed/villages/villages_map.html"

map_object.save(output_file)

print("\nMap created successfully!")
print("Output:", output_file)