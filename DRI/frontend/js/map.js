// ============================================================
// DRI — DISASTER RELOCATION INTELLIGENCE
// Interactive GIS Risk Map
// ============================================================

let leafletMap = null;
let villageLayer = null;
let selectedVillageId = null;


// ============================================================
// MAP RISK COLOURS
// ============================================================

const MAP_RISK_COLORS = {
    "Low": "#6e8f63",
    "Moderate": "#d9a441",
    "High": "#c77b3d",
    "Very High": "#a83232",
    "Insufficient Data": "#9b9788"
};


function riskColor(category) {

    return MAP_RISK_COLORS[category] ||
           MAP_RISK_COLORS["Insufficient Data"];

}


// ============================================================
// HELPERS
// ============================================================

function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function fmt(value, decimals = 1) {

    if (
        value === null ||
        value === undefined ||
        value === "" ||
        Number.isNaN(Number(value))
    ) {
        return "—";
    }

    return Number(value).toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: decimals
        }
    );
}


// ============================================================
// VILLAGE DETAIL PANEL
// ============================================================

function renderVillageDetail(village) {

    if (!village) {
        return `
            <div class="state-msg">
                No village selected.
            </div>
        `;
    }

    const villageName =
        village.village_name ||
        village.village ||
        "Unknown Village";

    const district =
        village.district ||
        "Unknown District";

    const population =
        village.population ??
        village.census_population_2011 ??
        "—";

    const riskScore =
        village.risk_score ??
        "—";

    const riskCategory =
        village.risk_category ||
        "Insufficient Data";

    const priority =
        village.priority ||
        village.relocation_priority ||
        "—";

    const hazardScore =
        village.hazard_score ??
        "—";

    const exposureScore =
        village.exposure_score ??
        "—";

    const vulnerabilityScore =
        village.vulnerability_score ??
        "—";

    const rainfallHazard =
        village.rainfall_hazard ??
        "—";

    const landslideHazard =
        village.landslide_hazard ??
        "—";

    const riverSignal =
        village.river_signal ??
        "—";

    const landslideCount =
        village.landslide_count ??
        "—";

    const slope =
        village.mean_slope_deg ??
        "—";

    const roadDistance =
        village.road_distance_km ??
        "—";

    const rainfallStation =
        village.nearest_rainfall_station ||
        village.rainfall_station ||
        "—";

    const riverStation =
        village.nearest_river_station ||
        village.river_station ||
        "—";


    return `

        <div style="
            padding:4px;
            font-family:Arial,sans-serif;
            color:#24362b;
        ">

            <!-- HEADER -->

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:15px;
                margin-bottom:18px;
            ">

                <div>

                    <div style="
                        font-size:10px;
                        font-weight:700;
                        color:#68736b;
                        text-transform:uppercase;
                        letter-spacing:.08em;
                        margin-bottom:5px;
                    ">
                        SELECTED VILLAGE
                    </div>

                    <h2 style="
                        margin:0;
                        font-size:23px;
                        color:#183526;
                    ">
                        ${escapeHtml(villageName)}
                    </h2>

                    <div style="
                        margin-top:4px;
                        color:#68736b;
                        font-size:13px;
                    ">
                        ${escapeHtml(district)}, Uttarakhand
                    </div>

                </div>


                <div style="
                    padding:7px 11px;
                    border-radius:20px;
                    background:#f0f3ed;
                    font-size:11px;
                    font-weight:700;
                    white-space:nowrap;
                ">
                    ${escapeHtml(riskCategory)}
                </div>

            </div>


            <!-- RISK / PRIORITY -->

            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:12px;
                margin-bottom:18px;
            ">

                <div style="
                    background:#f4f6f1;
                    border-radius:10px;
                    padding:14px;
                ">

                    <div style="
                        font-size:10px;
                        color:#68736b;
                        text-transform:uppercase;
                        margin-bottom:5px;
                    ">
                        Overall Risk
                    </div>

                    <strong style="
                        font-size:25px;
                        color:#183526;
                    ">
                        ${
                            riskScore === "—"
                                ? "—"
                                : `${fmt(riskScore)}/100`
                        }
                    </strong>

                </div>


                <div style="
                    background:#f4f6f1;
                    border-radius:10px;
                    padding:14px;
                ">

                    <div style="
                        font-size:10px;
                        color:#68736b;
                        text-transform:uppercase;
                        margin-bottom:5px;
                    ">
                        Relocation Priority
                    </div>

                    <strong style="
                        font-size:16px;
                        color:#183526;
                    ">
                        ${escapeHtml(priority)}
                    </strong>

                </div>

            </div>


            <!-- RISK PROFILE -->

            <div style="
                font-size:11px;
                font-weight:700;
                color:#68736b;
                text-transform:uppercase;
                letter-spacing:.06em;
                margin-bottom:9px;
            ">
                Risk Profile
            </div>


            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:10px 18px;
                font-size:12px;
                margin-bottom:18px;
            ">

                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                    ">
                        Population
                    </div>

                    <strong>
                        ${
                            population === "—"
                                ? "—"
                                : Number(population).toLocaleString("en-IN")
                        }
                    </strong>
                </div>


                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                    ">
                        Hazard Score
                    </div>

                    <strong>
                        ${fmt(hazardScore)}/100
                    </strong>
                </div>


                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                    ">
                        Exposure Score
                    </div>

                    <strong>
                        ${fmt(exposureScore)}/100
                    </strong>
                </div>


                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                    ">
                        Vulnerability
                    </div>

                    <strong>
                        ${fmt(vulnerabilityScore)}/100
                    </strong>
                </div>

            </div>


            <!-- HAZARD COMPONENTS -->

            <div style="
                border-top:1px solid #dddddd;
                padding-top:13px;
                margin-bottom:15px;
            ">

                <div style="
                    font-size:11px;
                    font-weight:700;
                    color:#68736b;
                    text-transform:uppercase;
                    letter-spacing:.06em;
                    margin-bottom:9px;
                ">
                    Hazard Components
                </div>


                <div style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:10px 18px;
                    font-size:12px;
                ">

                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Rainfall Hazard
                        </div>

                        <strong>
                            ${fmt(rainfallHazard)}
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Landslide Hazard
                        </div>

                        <strong>
                            ${fmt(landslideHazard)}
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            River Signal
                        </div>

                        <strong>
                            ${fmt(riverSignal)}
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Nearby Landslides
                        </div>

                        <strong>
                            ${fmt(landslideCount, 0)}
                        </strong>
                    </div>

                </div>

            </div>


            <!-- GIS CONTEXT -->

            <div style="
                border-top:1px solid #dddddd;
                padding-top:13px;
                margin-bottom:15px;
            ">

                <div style="
                    font-size:11px;
                    font-weight:700;
                    color:#68736b;
                    text-transform:uppercase;
                    letter-spacing:.06em;
                    margin-bottom:9px;
                ">
                    GIS Spatial Context
                </div>


                <div style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:10px 18px;
                    font-size:12px;
                ">

                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Mean Slope
                        </div>

                        <strong>
                            ${
                                slope === "—"
                                    ? "—"
                                    : `${fmt(slope)}°`
                            }
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Road Distance
                        </div>

                        <strong>
                            ${
                                roadDistance === "—"
                                    ? "—"
                                    : `${fmt(roadDistance)} km`
                            }
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Rainfall Station
                        </div>

                        <strong style="
                            font-size:10px;
                            word-break:break-word;
                        ">
                            ${escapeHtml(rainfallStation)}
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            River Station
                        </div>

                        <strong style="
                            font-size:10px;
                            word-break:break-word;
                        ">
                            ${escapeHtml(riverStation)}
                        </strong>
                    </div>

                </div>

            </div>


            <!-- NOTE -->

            <div style="
                border-top:1px solid #dddddd;
                padding-top:10px;
                color:#68736b;
                font-size:10px;
                line-height:1.5;
            ">
                Risk scores are decision-support outputs.
                Red-Zone Candidates require authority review
                and are not legal declarations of uninhabitable land.
            </div>

        </div>

    `;
}


// ============================================================
// NORMAL VILLAGE STYLE
// ============================================================

function villageStyle(feature) {

    const p = feature.properties || {};

    const category =
        p.risk_category ||
        "Insufficient Data";

    const selected =
        selectedVillageId !== null &&
        String(p.village_id) ===
        String(selectedVillageId);

    return {

        color: selected
            ? "#10261a"
            : "#4d5d52",

        weight: selected
            ? 3
            : 0.8,

        fillColor:
            riskColor(category),

        fillOpacity:
            selected
                ? 0.85
                : category === "Insufficient Data"
                    ? 0.28
                    : 0.65,

        opacity: 1
    };
}


// ============================================================
// HOVER STYLE
// ============================================================

function villageHoverStyle(feature) {

    const p = feature.properties || {};

    return {

        color: "#111111",

        weight:
            String(p.village_id) ===
            String(selectedVillageId)
                ? 3
                : 2.5,

        fillColor:
            riskColor(
                p.risk_category ||
                "Insufficient Data"
            ),

        fillOpacity: 0.90,

        opacity: 1
    };
}


// ============================================================
// GIS HOVER TOOLTIP
// ============================================================

function villageTooltipHtml(p) {

    const village =
        p.village_name ||
        p.village ||
        "Unknown Village";

    const district =
        p.district ||
        "Unknown District";

    const category =
        p.risk_category ||
        "Insufficient Data";

    const risk =
        p.risk_score !== null &&
        p.risk_score !== undefined &&
        p.risk_score !== ""
            ? `${fmt(p.risk_score)}/100`
            : "Insufficient Data";

    const population =
        p.population !== null &&
        p.population !== undefined &&
        p.population !== ""
            ? fmt(p.population, 0)
            : "—";

    const priority =
        p.priority ||
        p.relocation_priority ||
        "—";

    const hazard =
        p.hazard_score !== null &&
        p.hazard_score !== undefined
            ? `${fmt(p.hazard_score)}/100`
            : "—";

    const vulnerability =
        p.vulnerability_score !== null &&
        p.vulnerability_score !== undefined
            ? `${fmt(p.vulnerability_score)}/100`
            : "—";

    const rainfall =
        p.rainfall_hazard !== null &&
        p.rainfall_hazard !== undefined
            ? fmt(p.rainfall_hazard)
            : "—";

    const landslideHazard =
        p.landslide_hazard !== null &&
        p.landslide_hazard !== undefined
            ? fmt(p.landslide_hazard)
            : "—";

    const landslideCount =
        p.landslide_count !== null &&
        p.landslide_count !== undefined
            ? fmt(p.landslide_count, 0)
            : "—";

    const slope =
        p.mean_slope_deg !== null &&
        p.mean_slope_deg !== undefined
            ? `${fmt(p.mean_slope_deg)}°`
            : "—";

    let roadDistance = "—";

    if (
        p.road_distance_km !== null &&
        p.road_distance_km !== undefined
    ) {

        roadDistance =
            `${fmt(p.road_distance_km)} km`;

    }
    else if (
        p.road_distance_m !== null &&
        p.road_distance_m !== undefined
    ) {

        const meters =
            Number(p.road_distance_m);

        roadDistance =
            meters >= 1000
                ? `${(meters / 1000).toFixed(1)} km`
                : `${Math.round(meters)} m`;
    }

    const rainfallStation =
        p.nearest_rainfall_station ||
        p.rainfall_station ||
        "—";

    const riverStation =
        p.nearest_river_station ||
        p.river_station ||
        "—";


    return `

        <div style="
            min-width:285px;
            max-width:330px;
            font-family:Arial,sans-serif;
            color:#24362b;
            line-height:1.4;
        ">

            <div style="
                font-size:16px;
                font-weight:800;
                color:#183526;
                margin-bottom:3px;
            ">
                ${escapeHtml(village)}
            </div>


            <div style="
                color:#68736b;
                font-size:12px;
                margin-bottom:10px;
            ">
                ${escapeHtml(district)}, Uttarakhand
            </div>


            <div style="
                background:#f4f6f1;
                border-radius:8px;
                padding:9px 10px;
                margin-bottom:10px;
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    margin-bottom:5px;
                ">

                    <span style="
                        font-size:10px;
                        color:#68736b;
                        text-transform:uppercase;
                    ">
                        Risk Score
                    </span>

                    <strong>
                        ${escapeHtml(risk)}
                    </strong>

                </div>


                <div style="
                    display:flex;
                    justify-content:space-between;
                ">

                    <span style="
                        font-size:10px;
                        color:#68736b;
                        text-transform:uppercase;
                    ">
                        Category
                    </span>

                    <strong>
                        ${escapeHtml(category)}
                    </strong>

                </div>

            </div>


            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:8px 14px;
                font-size:12px;
            ">

                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Population
                    </div>

                    <strong>
                        ${escapeHtml(population)}
                    </strong>
                </div>


                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Priority
                    </div>

                    <strong>
                        ${escapeHtml(priority)}
                    </strong>
                </div>


                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Hazard
                    </div>

                    <strong>
                        ${escapeHtml(hazard)}
                    </strong>
                </div>


                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Vulnerability
                    </div>

                    <strong>
                        ${escapeHtml(vulnerability)}
                    </strong>
                </div>


                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Rainfall Hazard
                    </div>

                    <strong>
                        ${escapeHtml(rainfall)}
                    </strong>
                </div>


                <div>
                    <div style="
                        color:#68736b;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Landslide Hazard
                    </div>

                    <strong>
                        ${escapeHtml(landslideHazard)}
                    </strong>
                </div>

            </div>


            <div style="
                border-top:1px solid #dddddd;
                margin-top:10px;
                padding-top:9px;
            ">

                <div style="
                    font-size:10px;
                    font-weight:700;
                    color:#68736b;
                    text-transform:uppercase;
                    letter-spacing:.05em;
                    margin-bottom:7px;
                ">
                    GIS Spatial Context
                </div>


                <div style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:8px 14px;
                    font-size:12px;
                ">

                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Landslides
                        </div>

                        <strong>
                            ${escapeHtml(landslideCount)}
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Mean Slope
                        </div>

                        <strong>
                            ${escapeHtml(slope)}
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Road Distance
                        </div>

                        <strong>
                            ${escapeHtml(roadDistance)}
                        </strong>
                    </div>


                    <div>
                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Rainfall Station
                        </div>

                        <strong style="
                            font-size:10px;
                            word-break:break-word;
                        ">
                            ${escapeHtml(rainfallStation)}
                        </strong>
                    </div>


                    <div style="
                        grid-column:1 / -1;
                    ">

                        <div style="
                            color:#68736b;
                            font-size:10px;
                        ">
                            Nearest River Station
                        </div>

                        <strong style="
                            font-size:10px;
                            word-break:break-word;
                        ">
                            ${escapeHtml(riverStation)}
                        </strong>

                    </div>

                </div>

            </div>


            <div style="
                border-top:1px solid #dddddd;
                margin-top:10px;
                padding-top:7px;
                color:#68736b;
                font-size:10px;
            ">
                Hover to inspect · Click for full assessment
            </div>

        </div>
    `;
}


// ============================================================
// INITIALISE LEAFLET
// ============================================================

function initMap() {

    if (leafletMap) {
        return;
    }


    leafletMap =
        L.map(
            "map",
            {
                zoomControl: true,

                minZoom: 5,

                maxZoom: 17,

                // IMPORTANT:
                // SVG renderer is used so mouse
                // events work reliably on polygons.
                preferCanvas: false
            }
        );


    // OpenStreetMap base layer

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,

            attribution:
                "&copy; OpenStreetMap contributors"
        }
    ).addTo(leafletMap);


    // Uttarakhand

    leafletMap.setView(
        [30.0668, 79.0193],
        8
    );


    setTimeout(
        () => {

            if (leafletMap) {

                leafletMap.invalidateSize(
                    true
                );

            }

        },
        300
    );
}


// ============================================================
// VILLAGE EVENTS
// ============================================================

function attachFeatureEvents(
    feature,
    layer
) {

    const p =
        feature.properties || {};


    // --------------------------------------------------------
    // GIS-STYLE TOOLTIP
    // --------------------------------------------------------

    layer.bindTooltip(
        villageTooltipHtml(p),
        {
            sticky: true,

            direction: "top",

            opacity: 0.98,

            className:
                "dri-village-tooltip",

            offset: [
                0,
                -5
            ]
        }
    );


    // --------------------------------------------------------
    // HOVER IN
    // --------------------------------------------------------

    layer.on(
        "mouseover",
        function () {

            layer.setStyle(
                villageHoverStyle(
                    feature
                )
            );


            if (
                layer.bringToFront
            ) {

                layer.bringToFront();

            }

        }
    );


    // --------------------------------------------------------
    // HOVER OUT
    // --------------------------------------------------------

    layer.on(
        "mouseout",
        function () {

            layer.setStyle(
                villageStyle(
                    feature
                )
            );

        }
    );


    // --------------------------------------------------------
    // CLICK
    // --------------------------------------------------------

    layer.on(
        "click",
        function () {

            if (!p.village_id) {
                return;
            }


            selectedVillageId =
                String(
                    p.village_id
                );


            refreshMapStyles();


            // Update right panel.
            // FALSE = don't zoom / destroy map.

            if (
                typeof selectVillage ===
                "function"
            ) {

                selectVillage(
                    String(
                        p.village_id
                    ),
                    false
                );

            }

        }
    );
}


// ============================================================
// LOAD REAL GEOJSON
// ============================================================

async function loadMapLayer(
    district = ""
) {

    try {

        console.log(
            "DRI: Loading village GeoJSON...",
            district || "ALL DISTRICTS"
        );


        const geojson =
            await DriAPI.villagesGeojson(
                district
                    ? { district: district }
                    : {}
            );


        console.log(
            "DRI: GeoJSON received:",
            geojson.features?.length
        );


        if (
            !geojson ||
            !Array.isArray(
                geojson.features
            )
        ) {

            console.error(
                "DRI: Invalid GeoJSON response",
                geojson
            );

            return;
        }


        // Remove old village layer

        if (villageLayer) {

            leafletMap.removeLayer(
                villageLayer
            );

            villageLayer = null;

        }


        selectedVillageId = null;


        // ----------------------------------------------------
        // CREATE REAL VILLAGE POLYGONS
        // ----------------------------------------------------

        villageLayer =
            L.geoJSON(
                geojson,
                {

                    style:
                        villageStyle,

                    onEachFeature:
                        attachFeatureEvents

                }
            );


        // ----------------------------------------------------
        // ADD TO MAP
        // ----------------------------------------------------

        villageLayer.addTo(
            leafletMap
        );


        console.log(
            "DRI: Village layer added:",
            villageLayer.getLayers().length
        );


        // ----------------------------------------------------
        // FIT TO DATA
        // ----------------------------------------------------

        const bounds =
            villageLayer.getBounds();


        if (
            bounds &&
            bounds.isValid()
        ) {

            leafletMap.fitBounds(
                bounds,
                {
                    padding: [
                        20,
                        20
                    ],

                    maxZoom:
                        district
                            ? 11
                            : 9
                }
            );

        }


        setTimeout(
            () => {

                if (leafletMap) {

                    leafletMap.invalidateSize(
                        true
                    );

                }

            },
            300
        );


    }
    catch (error) {

        console.error(
            "DRI: GIS layer loading failed:",
            error
        );

    }
}


// ============================================================
// REFRESH VILLAGE STYLES
// ============================================================

function refreshMapStyles() {

    if (!villageLayer) {
        return;
    }


    villageLayer.eachLayer(
        function (layer) {

            if (
                layer.feature
            ) {

                layer.setStyle(
                    villageStyle(
                        layer.feature
                    )
                );

            }

        }
    );
}


// ============================================================
// SELECT VILLAGE
// ============================================================

async function selectVillage(
    villageId,
    zoomToVillage = false
) {

    if (!villageId) {
        return;
    }


    selectedVillageId =
        String(villageId);


    refreshMapStyles();


    // Update village dropdown

    const villageSelect =
        document.getElementById(
            "villageSelect"
        );


    if (villageSelect) {

        villageSelect.value =
            selectedVillageId;

    }


    // Update detail panel

    const panel =
        document.getElementById(
            "detailPanel"
        );


    if (panel) {

        panel.innerHTML = `

            <div class="state-msg">

                <div class="spinner"></div>

                Loading village details…

            </div>

        `;

    }


    try {

        const village =
            await DriAPI.village(
                selectedVillageId
            );


        if (panel) {

            panel.innerHTML =
                renderVillageDetail(
                    village
                );

        }


        refreshMapStyles();


        // Only zoom when explicitly requested.

        if (
            zoomToVillage
        ) {

            focusSelectedVillage(
                selectedVillageId
            );

        }


        // Bring selected village forward

        if (villageLayer) {

            villageLayer.eachLayer(
                function (layer) {

                    const p =
                        layer.feature?.properties ||
                        {};


                    if (
                        String(
                            p.village_id
                        ) ===
                        String(
                            selectedVillageId
                        )
                    ) {

                        layer.setStyle(
                            villageStyle(
                                layer.feature
                            )
                        );


                        if (
                            layer.bringToFront
                        ) {

                            layer.bringToFront();

                        }

                    }

                }
            );

        }


        setTimeout(
            () => {

                if (leafletMap) {

                    leafletMap.invalidateSize(
                        true
                    );

                }

            },
            150
        );

    }
    catch (error) {

        console.error(
            "DRI: Village loading failed:",
            error
        );


        if (panel) {

            panel.innerHTML = `

                <div class="state-msg error-msg">

                    Couldn't load village details.

                    <br><br>

                    ${escapeHtml(
                        error.message
                    )}

                </div>

            `;

        }

    }
}


// ============================================================
// OPTIONAL ZOOM FUNCTION
// ============================================================

function focusSelectedVillage(
    villageId
) {

    if (!villageLayer) {
        return;
    }


    villageLayer.eachLayer(
        function (layer) {

            const p =
                layer.feature?.properties ||
                {};


            if (
                String(
                    p.village_id
                ) !==
                String(villageId)
            ) {

                return;

            }


            const bounds =
                layer.getBounds();


            if (
                bounds &&
                bounds.isValid()
            ) {

                leafletMap.fitBounds(
                    bounds,
                    {
                        padding: [
                            60,
                            60
                        ],

                        maxZoom: 11
                    }
                );

            }


            layer.setStyle(
                villageStyle(
                    layer.feature
                )
            );


            if (
                layer.bringToFront
            ) {

                layer.bringToFront();

            }

        }
    );
}


// ============================================================
// COVERAGE
// ============================================================

async function loadCoverage() {

    try {

        const c =
            await DriAPI.coverage();


        const statGis =
            document.getElementById(
                "statGis"
            );


        const statCensus =
            document.getElementById(
                "statCensus"
            );


        const statRisk =
            document.getElementById(
                "statRisk"
            );


        if (statGis) {

            statGis.textContent =
                fmt(
                    c.gis_villages_total,
                    0
                );

        }


        if (statCensus) {

            statCensus.textContent =
                `${fmt(
                    c.census_integrated_total,
                    0
                )} (${c.census_integrated_pct}%)`;

        }


        if (statRisk) {

            statRisk.textContent =
                `${fmt(
                    c.complete_risk_total,
                    0
                )} (${c.complete_risk_pct}%)`;

        }

    }
    catch (error) {

        console.error(
            "DRI: Coverage failed:",
            error
        );

    }
}


// ============================================================
// DISTRICT DROPDOWN
// ============================================================

async function loadDistrictOptions() {

    const select =
        document.getElementById(
            "districtSelect"
        );


    if (!select) {
        return;
    }


    try {

        const result =
            await DriAPI.districts();


        const districts =
            result.districts || [];


        districts.forEach(
            function (district) {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    district;


                option.textContent =
                    district;


                select.appendChild(
                    option
                );

            }
        );

    }
    catch (error) {

        console.error(
            "DRI: District loading failed:",
            error
        );

    }
}


// ============================================================
// VILLAGE DROPDOWN
// ============================================================

async function loadVillageOptions(
    district = ""
) {

    const select =
        document.getElementById(
            "villageSelect"
        );


    if (!select) {
        return;
    }


    select.innerHTML =
        `<option value="">
            All villages
        </option>`;


    try {

        const result =
            await DriAPI.villages(
                district
                    ? { district }
                    : {}
            );


        const villages =
            result.villages || [];


        villages.sort(
            function (a, b) {

                return (
                    a.village_name || ""
                ).localeCompare(
                    b.village_name || ""
                );

            }
        );


        villages.forEach(
            function (village) {

                if (
                    !village.village_id
                ) {

                    return;

                }


                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    village.village_id;


                option.textContent =
                    village.village_name;


                select.appendChild(
                    option
                );

            }
        );

    }
    catch (error) {

        console.error(
            "DRI: Village dropdown failed:",
            error
        );

    }
}


// ============================================================
// DASHBOARD STARTUP
// ============================================================

async function initDashboard() {

    console.log(
        "DRI: Starting GIS Risk Map..."
    );


    // 1. Create map

    initMap();


    // 2. Load sidebar information

    await Promise.all(
        [
            loadCoverage(),
            loadDistrictOptions()
        ]
    );


    // 3. Load village dropdown

    await loadVillageOptions();


    // 4. Load REAL GIS POLYGONS

    await loadMapLayer();


    // ========================================================
    // DISTRICT FILTER
    // ========================================================

    const districtSelect =
        document.getElementById(
            "districtSelect"
        );


    if (districtSelect) {

        districtSelect.addEventListener(
            "change",
            async function () {

                const district =
                    districtSelect.value;


                selectedVillageId =
                    null;


                await loadVillageOptions(
                    district
                );


                await loadMapLayer(
                    district
                );

            }
        );

    }


    // ========================================================
    // VILLAGE FILTER
    // ========================================================

    const villageSelect =
        document.getElementById(
            "villageSelect"
        );


    if (villageSelect) {

        villageSelect.addEventListener(
            "change",
            function () {

                const villageId =
                    villageSelect.value;


                if (!villageId) {
                    return;
                }


                // FALSE = keep map where it is

                selectVillage(
                    villageId,
                    false
                );

            }
        );

    }


    // ========================================================
    // VIEW ASSESSMENT BUTTON
    // ========================================================

    const assessmentButton =
        document.getElementById(
            "viewAssessmentBtn"
        );


    if (assessmentButton) {

        assessmentButton.addEventListener(
            "click",
            function () {

                const villageId =
                    document.getElementById(
                        "villageSelect"
                    )?.value;


                if (!villageId) {
                    return;
                }


                selectVillage(
                    villageId,
                    false
                );

            }
        );

    }


    // ========================================================
    // URL PRESELECTION
    // ========================================================

    const params =
        new URLSearchParams(
            window.location.search
        );


    const preselect =
        params.get(
            "village"
        );


    if (preselect) {

        selectVillage(
            preselect,
            false
        );

    }


    // Final Leaflet resize

    setTimeout(
        () => {

            if (leafletMap) {

                leafletMap.invalidateSize(
                    true
                );

            }

        },
        500
    );


    console.log(
        "DRI: GIS Risk Map ready."
    );
}


// ============================================================
// ONE — AND ONLY ONE — PAGE LOAD HANDLER
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    initDashboard
);