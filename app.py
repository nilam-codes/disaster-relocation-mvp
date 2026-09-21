import os
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium

# Frontend background asset:
# assets/dri_background.jpg = user-provided disaster-relief/evacuation image.
from streamlit_folium import st_folium


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DRI - Disaster Relocation Intelligence",
    page_icon="ðŸŒ",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FILE PATHS
# ============================================================

RISK_FILE = "data/processed/final/uttarakhand_village_risk.csv"

RELOCATION_FILE = (
    "data/processed/final/relocation_recommendations.csv"
)

VILLAGE_FILE = (
    "data/raw/villages/"
    "vb_soi_uk_geojson/"
    "vb_soi_uk.GeoJSON"
)

GIS_VILLAGE_FILE = "data/processed/villages/villages_master.geojson"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            linear-gradient(rgba(235, 239, 221, 0.78), rgba(235, 239, 221, 0.78)),
            url("assets/dri_background.jpg") center center / cover fixed no-repeat;
        min-height: 100vh;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: rgba(255,255,255,0.16);
    }

    [data-testid="stMain"] {
        background: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #1d2b20;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 16px;
        color: #526052;
        margin-top: 0;
    }

    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #263629;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .metric-card {
        background: rgba(255,255,255,0.82);
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.08);
        min-height: 105px;
    }

    .metric-label {
        font-size: 14px;
        color: #526052;
        font-weight: 600;
    }

    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #1d2b20;
        margin-top: 7px;
    }

    .risk-box {
        border-radius: 16px;
        padding: 22px;
        text-align: center;
        margin-bottom: 15px;
    }

    .risk-low {
        background: #dcefdc;
        border: 2px solid #69a969;
    }

    .risk-moderate {
        background: #fff0c9;
        border: 2px solid #d5a72b;
    }

    .risk-high {
        background: #ffd9c9;
        border: 2px solid #d36b45;
    }

    .risk-very-high {
        background: #ffd0d0;
        border: 2px solid #bd3434;
    }

    .risk-insufficient {
        background: #e8e8e8;
        border: 2px solid #999999;
    }

    .risk-number {
        font-size: 42px;
        font-weight: 900;
        color: #18231a;
    }

    .risk-label {
        font-size: 18px;
        font-weight: 800;
    }

    .info-box {
        background: rgba(255,255,255,0.78);
        border-radius: 14px;
        padding: 18px;
        border: 1px solid rgba(0,0,0,0.08);
    }

    .recommendation-card {
        background: rgba(255,255,255,0.9);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(0,0,0,0.10);
        margin-bottom: 15px;
    }

    .destination {
        font-size: 24px;
        font-weight: 900;
        color: #183d26;
    }

    .small-note {
        font-size: 12px;
        color: #687268;
    }


    .frontend-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 18px;
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(38,54,41,0.10);
        border-radius: 14px;
        padding: 12px 16px;
        margin: 8px 0 12px 0;
        box-shadow: 0 4px 16px rgba(29,43,32,0.04);
    }

    .frontend-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.8px;
        color: #23623a;
        background: #e4f3e7;
        border: 1px solid #a8d2b1;
        border-radius: 999px;
        padding: 5px 9px;
        margin-right: 8px;
    }

    .frontend-meta {
        font-size: 12px;
        color: #687268;
        font-weight: 600;
    }

    .frontend-spacer {
        height: 4px;
    }

    .dashboard-glass {
        background: rgba(232, 238, 224, 0.74);
        border: 1px solid rgba(255,255,255,0.65);
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(30, 45, 34, 0.10);
        backdrop-filter: blur(8px);
    }

    .frontend-bar {
        background: rgba(245,248,238,0.78) !important;
        backdrop-filter: blur(8px);
    }

    .metric-card, .info-box, .recommendation-card {
        backdrop-filter: blur(8px);
    }

    .section-title {
        text-shadow: 0 1px 0 rgba(255,255,255,0.5);
    }

    div.stButton > button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 42px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.58);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 12px;
        padding: 10px 12px;
    }

    .section-title {
        letter-spacing: 0.5px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "map"

if "selected_district" not in st.session_state:
    st.session_state.selected_district = None

if "selected_village" not in st.session_state:
    st.session_state.selected_village = None


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_risk_data():
    return pd.read_csv(RISK_FILE)


@st.cache_data
def load_relocation_data():
    return pd.read_csv(RELOCATION_FILE)


@st.cache_data
def load_villages():
    return gpd.read_file(VILLAGE_FILE)


@st.cache_data
def load_gis_villages():
    return gpd.read_file(GIS_VILLAGE_FILE)


try:
    risk = load_risk_data()
    relocation = load_relocation_data()
    villages = load_villages()
    gis_villages = load_gis_villages()

except Exception as e:
    st.error("Could not load project data.")
    st.exception(e)
    st.stop()


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    if pd.isna(value):
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )


def risk_class(category):
    if category == "Low":
        return "risk-low"

    if category == "Moderate":
        return "risk-moderate"

    if category == "High":
        return "risk-high"

    if category == "Very High":
        return "risk-very-high"

    return "risk-insufficient"


def risk_color(category):
    if category == "Low":
        return "#63a35c"

    if category == "Moderate":
        return "#d9a72e"

    if category == "High":
        return "#df7047"

    if category == "Very High":
        return "#c93636"

    return "#8c8c8c"


def fmt_number(value, decimals=1):

    if pd.isna(value):
        return "--"

    if decimals == 0:
        return f"{value:,.0f}"

    return f"{value:,.{decimals}f}"


def get_selected_record():

    if not st.session_state.selected_village:
        return None

    district = st.session_state.selected_district
    village = st.session_state.selected_village

    result = risk[
        (risk["district"] == district)
        &
        (risk["village"] == village)
    ]

    if len(result) == 0:
        return None

    return result.iloc[0]


def get_selected_gis_record():
    if not st.session_state.selected_village:
        return None

    district = st.session_state.selected_district
    village = st.session_state.selected_village

    if "village" not in gis_villages.columns or "district" not in gis_villages.columns:
        return None

    gv = gis_villages.copy()
    gv["_village_key"] = gv["village"].apply(clean_text)
    gv["_district_key"] = gv["district"].apply(clean_text)

    result = gv[
        (gv["_district_key"] == clean_text(district))
        &
        (gv["_village_key"] == clean_text(village))
    ]

    if len(result) == 0:
        return None

    return result.iloc[0]


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        ðŸŒ DRI â€” DISASTER RELOCATION INTELLIGENCE
    </div>
    <div class="subtitle">
        Intelligent hazard assessment & relocation decision support
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


st.caption(
    "Uttarakhand statewide prototype Â· GIS: 16,920 villages Â· "
    "Census-integrated: 8,372 villages (49.5%) Â· "
    "Complete risk profiles: 7,831 villages (46.3%) Â· "
    "Remaining villages are shown as Insufficient Data when demographic inputs are incomplete."
)

st.markdown(
    """
    <div class="frontend-bar">
        <div>
            <span class="frontend-badge">â— LIVE PROTOTYPE</span>
            <span class="frontend-meta">Uttarakhand Â· GIS + Risk Intelligence</span>
        </div>
        <div class="frontend-meta">
            Human-in-the-loop decision support Â· Authority review required
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

nav1, nav2, nav3 = st.columns(3)

with nav1:
    if st.button(
        "ðŸ—ºï¸  RISK MAP",
        use_container_width=True,
        type="primary" if st.session_state.page == "map" else "secondary"
    ):
        st.session_state.page = "map"
        st.rerun()

with nav2:
    if st.button(
        "ðŸ“Š  VILLAGE ASSESSMENT",
        use_container_width=True,
        type="primary" if st.session_state.page == "risk" else "secondary"
    ):
        st.session_state.page = "risk"
        st.rerun()

with nav3:
    if st.button(
        "ðŸ“  RELOCATION OPTIONS",
        use_container_width=True,
        type="primary" if st.session_state.page == "relocation" else "secondary"
    ):
        st.session_state.page = "relocation"
        st.rerun()

st.markdown("<div class='frontend-spacer'></div>", unsafe_allow_html=True)


# ============================================================
# PAGE 1 â€” RISK MAP
# ============================================================

if st.session_state.page == "map":

    st.markdown(
        '<div class="section-title">ðŸ—ºï¸ RISK MAP</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:

        districts = sorted(
            risk["district"]
            .dropna()
            .unique()
            .tolist()
        )

        district = st.selectbox(
            "SELECT DISTRICT",
            districts,
            index=(
                districts.index(
                    st.session_state.selected_district
                )
                if st.session_state.selected_district
                in districts
                else 0
            )
        )

        st.session_state.selected_district = district

    district_data = risk[
        risk["district"] == district
    ].copy()

    with col2:

        villages_in_district = sorted(
            district_data["village"]
            .dropna()
            .unique()
            .tolist()
        )

        village = st.selectbox(
            "SELECT VILLAGE",
            villages_in_district,
            index=(
                villages_in_district.index(
                    st.session_state.selected_village
                )
                if st.session_state.selected_village
                in villages_in_district
                else 0
            )
        )

        st.session_state.selected_village = village

    with col3:

        if st.button(
            "ðŸ“Š OPEN VILLAGE RISK ASSESSMENT",
            use_container_width=True
        ):
            st.session_state.page = "risk"
            st.rerun()


    # --------------------------------------------------------
    # DATA COVERAGE SUMMARY
    # --------------------------------------------------------
    gis_total = len(gis_villages)
    complete_risk_total = int(risk["risk_score"].notna().sum())
    coverage_pct = (complete_risk_total / gis_total * 100) if gis_total else 0

    district_gis = gis_villages[
        gis_villages["district"].astype(str).str.strip() == str(district).strip()
    ] if "district" in gis_villages.columns else gis_villages.iloc[0:0]
    district_complete = int(
        risk[(risk["district"] == district) & risk["risk_score"].notna()].shape[0]
    )
    district_gis_count = len(district_gis)
    district_coverage = (
        district_complete / district_gis_count * 100
        if district_gis_count else 0
    )

    st.caption(
        f"**Statewide GIS coverage:** {gis_total:,} villages Â· "
        f"**Complete risk coverage:** {complete_risk_total:,} villages "
        f"({coverage_pct:.1f}%) Â· "
        f"**{district} risk coverage:** {district_complete:,} / "
        f"{district_gis_count:,} villages ({district_coverage:.1f}%)"
    )

    cov1, cov2, cov3, cov4 = st.columns(4)
    with cov1:
        st.metric("GIS Villages", f"{gis_total:,}")
    with cov2:
        st.metric("Complete Risk Profiles", f"{complete_risk_total:,}")
    with cov3:
        st.metric("Statewide Risk Coverage", f"{coverage_pct:.1f}%")
    with cov4:
        high_count = int((risk["risk_category"] == "High").sum())
        very_high_count = int((risk["risk_category"] == "Very High").sum())
        st.metric("High / Very High", f"{high_count + very_high_count:,}")

    st.info(
        "The GIS layer covers the state, while complete village risk scores "
        "are available where the integrated demographic data is matched. "
        "Villages without complete demographic inputs are kept as **Insufficient Data** "
        "rather than being assigned a guessed risk score."
    )


    # --------------------------------------------------------
    # PREPARE MAP DATA
    # --------------------------------------------------------

    risk_map_data = risk[
        risk["risk_score"].notna()
    ].copy()

    risk_map_data["risk_class"] = (
        risk_map_data["risk_category"]
    )

    villages["village_key"] = (
        villages["village"]
        .apply(clean_text)
        if "village" in villages.columns
        else villages["name"].apply(clean_text)
    )

    villages["district_key"] = (
        villages["district"]
        .apply(clean_text)
        if "district" in villages.columns
        else ""
    )

    risk_map_data["village_key"] = (
        risk_map_data["village"]
        .apply(clean_text)
    )

    risk_map_data["district_key"] = (
        risk_map_data["district"]
        .apply(clean_text)
    )

    map_data = villages.merge(
        risk_map_data[
            [
                "village_key",
                "district_key",
                "risk_score",
                "risk_category",
                "hazard_score"
            ]
        ],
        on=["village_key", "district_key"],
        how="inner"
    )

    # Add GIS master attributes to the risk polygons.
    gis_map = gis_villages.copy()
    gis_map["village_key"] = gis_map["village"].apply(clean_text)
    gis_map["district_key"] = gis_map["district"].apply(clean_text)

    gis_fields = [
        "village_key",
        "district_key",
        "landslide_count",
        "mean_slope_deg",
        "road_distance_m",
        "rainfall_station",
        "rainfall_distance_m",
        "river_station",
        "river_distance_m"
    ]
    gis_fields = [c for c in gis_fields if c in gis_map.columns]

    gis_map = gis_map[gis_fields].drop_duplicates(
        subset=["village_key", "district_key"]
    )

    map_data = map_data.merge(
        gis_map,
        on=["village_key", "district_key"],
        how="left"
    )

    # Limit map to villages with complete risk data.
    map_data = map_data[
        map_data["risk_score"].notna()
    ].copy()

    # Folium requires WGS84.
    map_data = map_data.to_crs("EPSG:4326")


    # --------------------------------------------------------
    # MAP CENTER
    # --------------------------------------------------------

    if len(map_data) > 0:

        center = [
            map_data.geometry.centroid.y.mean(),
            map_data.geometry.centroid.x.mean()
        ]

    else:

        center = [
            30.0668,
            79.0193
        ]


    fmap = folium.Map(
        location=center,
        zoom_start=7,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # Fit the map to the actual Uttarakhand risk-data extent instead of
    # relying on a fixed zoom level. This keeps the state visible while
    # avoiding the overly zoomed-out India-wide view.
    try:
        minx, miny, maxx, maxy = map_data.total_bounds
        fmap.fit_bounds([[miny, minx], [maxy, maxx]], padding=(20, 20))
    except Exception:
        pass


    # --------------------------------------------------------
    # RISK POLYGONS
    # --------------------------------------------------------

    def style_function(feature):

        category = feature["properties"].get(
            "risk_category",
            ""
        )

        return {
            "fillColor": risk_color(category),
            "color": "#555555",
            "weight": 0.4,
            "fillOpacity": 0.55
        }


    folium.GeoJson(
        map_data.to_json(),
        name="Village Risk",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "village",
                "district",
                "risk_score",
                "risk_category",
                "landslide_count",
                "mean_slope_deg",
                "road_distance_m"
            ],
            aliases=[
                "Village",
                "District",
                "Risk Score",
                "Risk Category",
                "Landslides",
                "Mean Slope (Â°)",
                "Road Distance (m)"
            ],
            localize=True
        )
    ).add_to(fmap)


    # --------------------------------------------------------
    # SELECTED VILLAGE MARKER
    # --------------------------------------------------------

    selected = get_selected_record()

    if selected is not None:

        selected_geo = map_data[
            (map_data["village_key"] ==
             clean_text(selected["village"]))
            &
            (map_data["district_key"] ==
             clean_text(selected["district"]))
        ]

        if len(selected_geo) > 0:

            point = selected_geo.geometry.iloc[0].centroid

            folium.Marker(
                [
                    point.y,
                    point.x
                ],
                tooltip=selected["village"],
                popup=(
                    f"<b>{selected['village']}</b><br>"
                    f"Risk: "
                    f"{fmt_number(selected['risk_score'])}/100"
                ),
                icon=folium.Icon(
                    color="red",
                    icon="warning-sign"
                )
            ).add_to(fmap)


    folium.LayerControl().add_to(fmap)

    legend_html = """
    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999;
                background: white; padding: 10px 12px; border-radius: 8px;
                border: 1px solid #cccccc; font-size: 12px; line-height: 1.6;">
      <b>Risk Category</b><br>
      <span style="color:#63a35c">â– </span> Low (0â€“24)<br>
      <span style="color:#d9a72e">â– </span> Moderate (25â€“49)<br>
      <span style="color:#df7047">â– </span> High (50â€“74)<br>
      <span style="color:#c93636">â– </span> Very High (75â€“100)
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(legend_html))


    st_folium(
        fmap,
        width=None,
        height=560,
        returned_objects=[]
    )


    # --------------------------------------------------------
    # SELECTED VILLAGE DETAILS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">SELECTED VILLAGE DETAILS</div>',
        unsafe_allow_html=True
    )

    selected = get_selected_record()

    if selected is not None:

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Village",
                selected["village"]
            )

        with c2:
            st.metric(
                "Population",
                fmt_number(
                    selected["total_population_village"],
                    0
                )
            )

        with c3:
            st.metric(
                "Risk Score",
                f"{fmt_number(selected['risk_score'])}/100"
            )

        with c4:
            st.metric(
                "Priority",
                selected["relocation_priority"]
            )

        c5, c6, c7, c8 = st.columns(4)

        with c5:
            st.metric(
                "Rainfall Hazard",
                f"{fmt_number(selected['rainfall_hazard_score'])}/100"
            )

        with c6:
            st.metric(
                "Landslide Hazard",
                f"{fmt_number(selected['landslide_hazard_score'])}/100"
            )

        with c7:
            st.metric(
                "Vulnerability",
                f"{fmt_number(selected['vulnerability_score'])}/100"
            )

        with c8:
            st.metric(
                "Risk Category",
                selected["risk_category"]
            )


    # --------------------------------------------------------
    # GIS SPATIAL CONTEXT
    # --------------------------------------------------------

    gis_selected = get_selected_gis_record()

    st.markdown(
        '<div class="section-title">ðŸ“ GIS SPATIAL CONTEXT</div>',
        unsafe_allow_html=True
    )

    if gis_selected is not None:
        g1, g2, g3, g4 = st.columns(4)

        with g1:
            st.metric(
                "Nearby / Assigned Landslides",
                fmt_number(gis_selected.get("landslide_count"), 0)
            )

        with g2:
            slope = gis_selected.get("mean_slope_deg")
            slope_value = "--" if pd.isna(slope) else f"{float(slope):.1f}Â°"
            st.metric("Mean Slope", slope_value)

        with g3:
            road_distance = gis_selected.get("road_distance_m")
            if pd.isna(road_distance):
                road_value = "--"
            elif float(road_distance) >= 1000:
                road_value = f"{float(road_distance) / 1000:.1f} km"
            else:
                road_value = f"{float(road_distance):.0f} m"
            st.metric("Road Distance", road_value)

        with g4:
            rainfall_distance = gis_selected.get("rainfall_distance_m")
            if pd.isna(rainfall_distance):
                station_value = "--"
            elif float(rainfall_distance) >= 1000:
                station_value = f"{float(rainfall_distance) / 1000:.1f} km"
            else:
                station_value = f"{float(rainfall_distance):.0f} m"
            st.metric("Rainfall Station Distance", station_value)

        station = gis_selected.get("rainfall_station")
        river_station = gis_selected.get("river_station")
        river_distance = gis_selected.get("river_distance_m")

        station_text = "--" if pd.isna(station) else str(station)
        river_text = "--" if pd.isna(river_station) else str(river_station)

        if pd.isna(river_distance):
            river_distance_text = "--"
        elif float(river_distance) >= 1000:
            river_distance_text = f"{float(river_distance) / 1000:.1f} km"
        else:
            river_distance_text = f"{float(river_distance):.0f} m"

        st.caption(
            f"Nearest rainfall station: **{station_text}** Â· "
            f"Nearest river station: **{river_text}** "
            f"({river_distance_text})"
        )

        st.caption(
            "GIS context is derived from the spatial master dataset. "
            "Slope is shown only where DEM coverage is available. "
            "River information is supporting hydrological context and is "
            "not included in the current final risk formula."
        )
    else:
        st.info("GIS spatial context is not available for this village.")


# ============================================================
# PAGE 2 â€” VILLAGE RISK ASSESSMENT
# ============================================================

elif st.session_state.page == "risk":

    selected = get_selected_record()

    if selected is None:

        st.warning(
            "Please select a village from the Risk Map first."
        )

        if st.button("â† BACK TO RISK MAP"):
            st.session_state.page = "map"
            st.rerun()

        st.stop()


    if st.button("â† BACK TO RISK MAP"):

        st.session_state.page = "map"
        st.rerun()


    st.markdown(
        f"""
        <div class="main-title">
            Village Risk Assessment
        </div>

        <div class="subtitle">
            {selected['village']} Â·
            {selected['district']} Â·
            Uttarakhand
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # OVERALL RISK
    # --------------------------------------------------------

    category = selected["risk_category"]

    st.markdown(
        f"""
        <div class="risk-box {risk_class(category)}">

            <div class="risk-label">
                OVERALL RISK SCORE
            </div>

            <div class="risk-number">
                {fmt_number(selected['risk_score'])} / 100
            </div>

            <div class="risk-label">
                {category.upper()}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # HAZARD ASSESSMENT
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">HAZARD ASSESSMENT</div>',
        unsafe_allow_html=True
    )

    h1, h2, h3 = st.columns(3)

    with h1:
        st.metric(
            "Landslide",
            f"{fmt_number(selected['landslide_hazard_score'])}/100"
        )

    with h2:
        st.metric(
            "Rainfall",
            f"{fmt_number(selected['rainfall_hazard_score'])}/100"
        )

    with h3:
        st.metric(
            "River Data Signal",
            f"{fmt_number(selected['river_hazard_score'])}/100"
        )


    st.caption(
        "River data signal is supporting hydrological information only and "
        "is not included in the current final hazard formula."
    )


    # --------------------------------------------------------
    # POPULATION & VULNERABILITY
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">POPULATION & VULNERABILITY</div>',
        unsafe_allow_html=True
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric(
            "Population",
            fmt_number(
                selected["total_population_village"],
                0
            )
        )

    with p2:
        st.metric(
            "Children 0â€“6",
            f"{fmt_number(selected['children_0_6_pct'])}%"
        )

    with p3:
        st.metric(
            "Illiteracy",
            f"{fmt_number(selected['illiteracy_pct'])}%"
        )


    # --------------------------------------------------------
    # RISK COMPOSITION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">RISK COMPOSITION</div>',
        unsafe_allow_html=True
    )

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric(
            "Hazard",
            f"{fmt_number(selected['hazard_score'])}/100"
        )

    with r2:
        st.metric(
            "Exposure",
            f"{fmt_number(selected['population_exposure_score'])}/100"
        )

    with r3:
        st.metric(
            "Vulnerability",
            f"{fmt_number(selected['vulnerability_score'])}/100"
        )


    # --------------------------------------------------------
    # RELOCATION STATUS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">RELOCATION DECISION</div>',
        unsafe_allow_html=True
    )

    priority = selected["relocation_priority"]

    if priority == "Short-Term":

        st.error(
            f"ðŸš¨ Relocation Priority: {priority}"
        )

    elif priority == "Medium-Term":

        st.warning(
            f"âš ï¸ Relocation Priority: {priority}"
        )

    else:

        st.info(
            f"â„¹ï¸ Relocation Priority: {priority}"
        )


    if st.button(
        "ðŸŸ¢ VIEW RELOCATION OPTIONS â†’",
        use_container_width=True
    ):

        st.session_state.page = "relocation"
        st.rerun()


# ============================================================
# PAGE 3 â€” RELOCATION OPTIONS
# ============================================================

elif st.session_state.page == "relocation":

    selected = get_selected_record()

    if selected is None:

        st.warning("No village selected.")

        if st.button("â† BACK"):
            st.session_state.page = "map"
            st.rerun()

        st.stop()


    if st.button("â† BACK TO RISK ASSESSMENT"):

        st.session_state.page = "risk"
        st.rerun()


    st.markdown(
        f"""
        <div class="main-title">
            Relocation Options
        </div>

        <div class="subtitle">
            Relocation assessment for
            <b>{selected['village']}</b>
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # SOURCE INFORMATION
    # --------------------------------------------------------

    source_name = selected["village"]
    source_district = selected["district"]

    source_options = relocation[
        (relocation["source_village"] == source_name)
        &
        (relocation["source_district"] == source_district)
    ].copy()


    if len(source_options) == 0:

        st.warning(
            "No relocation recommendation is currently "
            "available for this village."
        )

        st.info(
            "The current MVP generates relocation recommendations "
            "for the highest-priority assessment set."
        )

        st.stop()


    # --------------------------------------------------------
    # SOURCE SUMMARY
    # --------------------------------------------------------

    a1, a2, a3 = st.columns(3)

    with a1:
        st.metric(
            "People to Relocate",
            fmt_number(
                selected["total_population_village"],
                0
            )
        )

    with a2:
        st.metric(
            "Current Risk",
            f"{fmt_number(selected['risk_score'])}/100"
        )

    with a3:
        st.metric(
            "Priority",
            selected["relocation_priority"]
        )


    st.markdown(
        '<div class="section-title">RECOMMENDED RELOCATION SITE</div>',
        unsafe_allow_html=True
    )


    # Show top 3 available recommendations if present.
    source_options = source_options.sort_values(
        "relocation_score",
        ascending=False
    ).head(3)


    for rank, (_, option) in enumerate(
        source_options.iterrows(),
        start=1
    ):

        st.markdown(
            f"""
            <div class="recommendation-card">

                <div class="destination">
                    #{rank} {option['candidate_village']}
                </div>

                <div class="small-note">
                    District: {option['candidate_district']}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.metric(
                "Destination Risk",
                f"{fmt_number(option['candidate_risk_score'])}/100"
            )

        with c2:
            st.metric(
                "Safety",
                f"{fmt_number(option['safety_score'])}/100"
            )

        with c3:
            st.metric(
                "Capacity",
                fmt_number(
                    option["estimated_capacity"],
                    0
                )
            )

        with c4:
            st.metric(
                "Distance",
                f"{fmt_number(option['distance_km'], 1)} km"
            )

        with c5:
            st.metric(
                "Healthcare",
                f"{fmt_number(option['healthcare_access_score'])}/100"
            )


        st.progress(
            min(
                1.0,
                float(option["relocation_score"]) / 100
            )
        )

        st.write(
            f"â­ **Relocation Suitability: "
            f"{fmt_number(option['relocation_score'])}/100**"
        )

        if bool(option["enough_capacity"]):

            st.success(
                "âœ“ Estimated capacity can accommodate "
                "the source population."
            )

        else:

            st.warning(
                "âš  Estimated capacity is below the "
                "source population."
            )

        st.divider()


    st.caption(
        "Capacity is an estimated planning proxy based on the current "
        "MVP model, not an officially approved carrying-capacity figure."
    )