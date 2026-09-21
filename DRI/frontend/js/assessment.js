/**
 * assessment.js — powers assessment.html
 *
 * Behaviour:
 * 1. If URL contains ?village=ID, load that village directly.
 * 2. If no village is selected, show a real village selector.
 * 3. Uses the existing DriAPI backend and REAL risk-engine data.
 */


/* ============================================================
   START
   ============================================================ */

async function loadAssessment() {

    const root =
        document.getElementById("assessmentRoot") ||
        document.getElementById("assessment-root") ||
        document.getElementById("assessmentRoot");

    if (!root) {

        console.error(
            "DRI: assessmentRoot not found."
        );

        return;
    }


    const params =
        new URLSearchParams(
            window.location.search
        );

    const villageId =
        params.get("village");


    /*
     * If a village was passed in the URL,
     * load its assessment directly.
     */

    if (villageId) {

        await renderAssessment(
            root,
            villageId
        );

        return;
    }


    /*
     * Otherwise show a village selector.
     */

    await showAssessmentSelector(
        root
    );
}


/* ============================================================
   VILLAGE SELECTOR
   ============================================================ */

async function showAssessmentSelector(root) {

    root.innerHTML = `

        <div class="glass section-block">

            <h3>
                Select a village
            </h3>

            <p
                style="
                    color:var(--ink-soft);
                    margin-top:0.3rem;
                "
            >
                Select a village to view its complete
                hazard, exposure, vulnerability and
                risk assessment.
            </p>


            <div
                style="
                    max-width:560px;
                    margin-top:1.2rem;
                "
            >

                <label
                    for="assessmentVillageSelect"
                    class="label"
                    style="
                        display:block;
                        margin-bottom:0.45rem;
                    "
                >
                    Village
                </label>


                <select
                    id="assessmentVillageSelect"
                    style="
                        width:100%;
                        padding:0.85rem 1rem;
                        border:1px solid rgba(30,70,50,0.18);
                        border-radius:12px;
                        background:#fff;
                        font-size:1rem;
                        color:var(--ink);
                    "
                >

                    <option value="">
                        Loading villages…
                    </option>

                </select>


                <button
                    id="loadAssessmentVillage"
                    type="button"
                    class="btn-primary"
                    style="
                        margin-top:1rem;
                        width:100%;
                    "
                >
                    View Risk Assessment
                </button>

            </div>

        </div>
    `;


    const select =
        document.getElementById(
            "assessmentVillageSelect"
        );

    const button =
        document.getElementById(
            "loadAssessmentVillage"
        );


    try {

        const result =
            await DriAPI.villages();


        let villages =
            Array.isArray(result.villages)
                ? result.villages
                : [];


        /*
         * Put villages with actual risk scores first.
         * Within those, highest-risk villages first.
         */

        villages.sort(
            (a, b) => {

                const ar =
                    Number(a.risk_score);

                const br =
                    Number(b.risk_score);


                const aValid =
                    Number.isFinite(ar);

                const bValid =
                    Number.isFinite(br);


                if (
                    aValid &&
                    !bValid
                ) {

                    return -1;

                }


                if (
                    !aValid &&
                    bValid
                ) {

                    return 1;

                }


                if (
                    aValid &&
                    bValid
                ) {

                    return br - ar;

                }


                return (
                    String(
                        a.village_name || ""
                    )
                    .localeCompare(
                        String(
                            b.village_name || ""
                        )
                    )
                );

            }
        );


        select.innerHTML = `

            <option value="">
                Choose a village…
            </option>

        `;


        villages.forEach(
            (village) => {

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


                const risk =
                    village.risk_score != null
                        ? ` · Risk ${formatAssessmentNumber(village.risk_score)}`
                        : "";


                option.textContent =
                    `${village.village_name} — ${village.district}${risk}`;


                select.appendChild(
                    option
                );

            }
        );


        /*
         * Automatically choose Sherpur for the demo.
         */

        const sherpur =
            villages.find(
                (village) =>
                    String(
                        village.village_name || ""
                    )
                    .trim()
                    .toLowerCase() ===
                    "sherpur"
            );


        if (sherpur) {

            select.value =
                sherpur.village_id;

        }

    }
    catch (error) {

        console.error(
            "DRI: Assessment village list failed:",
            error
        );


        select.innerHTML = `

            <option value="">
                Couldn't load villages
            </option>

        `;

    }


    button.addEventListener(
        "click",
        async () => {

            const selectedId =
                select.value;


            if (!selectedId) {

                alert(
                    "Please select a village first."
                );

                return;

            }


            const url =
                new URL(
                    window.location.href
                );


            url.searchParams.set(
                "village",
                selectedId
            );


            window.history.replaceState(
                {},
                "",
                url
            );


            await renderAssessment(
                root,
                selectedId
            );

        }
    );
}


/* ============================================================
   LOAD ONE VILLAGE ASSESSMENT
   ============================================================ */

async function renderAssessment(
    root,
    villageId
) {

    root.innerHTML = `

        <div class="state-msg">

            <div class="spinner"></div>

            Loading village risk assessment…

        </div>

    `;


    try {

        const risk =
            await DriAPI.risk(
                villageId
            );


        /*
         * Incomplete demographic data.
         */

        if (
            risk.has_complete_risk_profile === false
        ) {

            root.innerHTML = `

                <div
                    class="glass section-block"
                >

                    <div
                        style="
                            display:flex;
                            justify-content:space-between;
                            align-items:center;
                            gap:1rem;
                            flex-wrap:wrap;
                        "
                    >

                        <div>

                            <div class="label">
                                SELECTED VILLAGE
                            </div>

                            <h2
                                style="
                                    margin:0.25rem 0;
                                "
                            >
                                ${escapeAssessment(
                                    risk.village_name
                                )}
                            </h2>

                            <div
                                style="
                                    color:var(--ink-soft);
                                "
                            >
                                ${escapeAssessment(
                                    risk.district
                                )},
                                Uttarakhand
                            </div>

                        </div>


                        <button
                            id="changeAssessmentVillage"
                            type="button"
                            class="btn-secondary"
                            style="
                                padding:0.65rem 1rem;
                                border-radius:10px;
                                cursor:pointer;
                            "
                        >
                            Change Village
                        </button>

                    </div>


                    <div
                        class="note caution"
                        style="
                            margin-top:1.5rem;
                        "
                    >

                        <strong>
                            Risk Assessment Pending
                        </strong>

                        <br>

                        Complete demographic inputs
                        are not currently available for
                        this village, so the system does
                        not generate a final risk score.

                    </div>

                </div>

            `;


            document
                .getElementById(
                    "changeAssessmentVillage"
                )
                ?.addEventListener(
                    "click",
                    () => {

                        const url =
                            new URL(
                                window.location.href
                            );

                        url.searchParams.delete(
                            "village"
                        );

                        window.history.replaceState(
                            {},
                            "",
                            url
                        );

                        showAssessmentSelector(
                            root
                        );

                    }
                );


            return;
        }


        /*
         * Complete risk profile.
         */

        root.innerHTML =
            buildAssessmentHTML(
                risk
            );


        /*
         * Change village button.
         */

        document
            .getElementById(
                "changeAssessmentVillage"
            )
            ?.addEventListener(
                "click",
                () => {

                    const url =
                        new URL(
                            window.location.href
                        );

                    url.searchParams.delete(
                        "village"
                    );

                    window.history.replaceState(
                        {},
                        "",
                        url
                    );

                    showAssessmentSelector(
                        root
                    );

                }
            );


        /*
         * Open relocation options.
         */

        document
            .getElementById(
                "openRelocationAssessment"
            )
            ?.addEventListener(
                "click",
                () => {

                    const url =
                        new URL(
                            "relocation.html",
                            window.location.href
                        );


                    url.searchParams.set(
                        "village",
                        villageId
                    );


                    window.location.href =
                        url.toString();

                }
            );


    }
    catch (error) {

        console.error(
            "DRI: Assessment loading failed:",
            error
        );


        root.innerHTML = `

            <div
                class="state-msg error-msg"
            >

                <h3>
                    Couldn't load village assessment.
                </h3>

                <p>
                    ${escapeAssessment(
                        error.message ||
                        "Unknown error"
                    )}
                </p>


                <button
                    id="retryAssessment"
                    type="button"
                    class="btn-primary"
                    style="
                        margin-top:1rem;
                    "
                >
                    Retry
                </button>

            </div>

        `;


        document
            .getElementById(
                "retryAssessment"
            )
            ?.addEventListener(
                "click",
                () => {

                    renderAssessment(
                        root,
                        villageId
                    );

                }
            );

    }
}


/* ============================================================
   BUILD ASSESSMENT UI
   ============================================================ */

function buildAssessmentHTML(risk) {

    const category =
        risk.risk_category ||
        "—";


    const riskScore =
        risk.risk_score;


    const hazard =
        risk.hazard || {};


    const exposure =
        risk.exposure || {};


    const vulnerability =
        risk.vulnerability || {};


    const supporting =
        risk.supporting_signals || {};


    const priority =
        risk.priority ||
        "—";


    const riskClass =
        assessmentRiskClass(
            category
        );


    return `

        <!-- HEADER -->

        <div
            class="glass section-block"
        >

            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    align-items:flex-start;
                    gap:1rem;
                    flex-wrap:wrap;
                "
            >

                <div>

                    <div class="label">
                        SELECTED VILLAGE
                    </div>


                    <h2
                        style="
                            margin:0.25rem 0;
                        "
                    >
                        ${escapeAssessment(
                            risk.village_name
                        )}
                    </h2>


                    <div
                        style="
                            color:var(--ink-soft);
                        "
                    >
                        ${escapeAssessment(
                            risk.district
                        )},
                        Uttarakhand
                    </div>

                </div>


                <span
                    class="${riskPillAssessment(
                        category
                    )}"
                >
                    ${escapeAssessment(
                        category
                    )}
                </span>

            </div>


            <!-- OVERALL RISK -->

            <div
                style="
                    display:grid;
                    grid-template-columns:
                        minmax(0,1fr)
                        minmax(0,1fr);
                    gap:1rem;
                    margin-top:1.5rem;
                "
            >

                <div
                    class="mini-card"
                    style="
                        padding:1.25rem;
                    "
                >

                    <div class="label">
                        OVERALL RISK
                    </div>


                    <div
                        class="value"
                        style="
                            font-size:2rem;
                            margin-top:0.3rem;
                        "
                    >
                        ${formatAssessmentNumber(
                            riskScore
                        )}/100
                    </div>


                    <div
                        style="
                            color:var(--ink-soft);
                            margin-top:0.25rem;
                        "
                    >
                        ${escapeAssessment(
                            category
                        )}
                    </div>

                </div>


                <div
                    class="mini-card"
                    style="
                        padding:1.25rem;
                    "
                >

                    <div class="label">
                        RELOCATION PRIORITY
                    </div>


                    <div
                        class="value"
                        style="
                            font-size:1.25rem;
                            margin-top:0.5rem;
                        "
                    >
                        ${escapeAssessment(
                            priority
                        )}
                    </div>


                    <div
                        style="
                            color:var(--ink-soft);
                            margin-top:0.25rem;
                        "
                    >
                        Action urgency
                    </div>

                </div>

            </div>

        </div>


        <!-- HAZARD -->

        <div
            class="glass section-block"
        >

            <h3>
                Hazard Assessment
            </h3>


            <p
                style="
                    color:var(--ink-soft);
                    margin-top:0.25rem;
                "
            >
                Hazard component of the transparent
                risk model.
            </p>


            <div class="card-grid">

                <div class="mini-card">

                    <div class="label">
                        Landslide Hazard
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            hazard.landslide_hazard
                        )}/100
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        Rainfall Hazard
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            hazard.rainfall_hazard
                        )}/100
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        Hazard Score
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            hazard.score
                        )}/100
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        River Signal
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            hazard.river_signal
                        )}/100
                    </div>

                </div>

            </div>


            <div
                class="note"
                style="
                    margin-top:1rem;
                "
            >

                <strong>
                    River / flood signal:
                </strong>

                supporting hydrological context
                only — it is not part of the current
                final risk formula.

            </div>

        </div>


        <!-- EXPOSURE -->

        <div
            class="glass section-block"
        >

            <h3>
                Population & Exposure
            </h3>


            <div class="card-grid">

                <div class="mini-card">

                    <div class="label">
                        Population
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            exposure.population,
                            0
                        )}
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        Exposure Score
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            exposure.score
                        )}/100
                    </div>

                </div>

            </div>

        </div>


        <!-- VULNERABILITY -->

        <div
            class="glass section-block"
        >

            <h3>
                Vulnerability
            </h3>


            <div class="card-grid">

                <div class="mini-card">

                    <div class="label">
                        Vulnerability Score
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            vulnerability.score
                        )}/100
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        Children 0–6
                    </div>

                    <div class="value">
                        ${formatAssessmentPercent(
                            vulnerability.children_0_6
                        )}
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        Illiteracy
                    </div>

                    <div class="value">
                        ${formatAssessmentPercent(
                            vulnerability.illiteracy_rate
                        )}
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        SC / ST
                    </div>

                    <div class="value">
                        ${formatAssessmentPercent(
                            vulnerability.sc_st_pct
                        )}
                    </div>

                </div>

            </div>

        </div>


        <!-- GIS CONTEXT -->

        <div
            class="glass section-block"
        >

            <h3>
                GIS Spatial Context
            </h3>


            <div class="card-grid">

                <div class="mini-card">

                    <div class="label">
                        Nearby Landslides
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            supporting.landslide_count,
                            0
                        )}
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        Mean Slope
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            supporting.mean_slope_deg
                        )}
                        °
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        Road Distance
                    </div>

                    <div class="value">
                        ${formatAssessmentNumber(
                            supporting.road_distance_km
                        )}
                        km
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        Rainfall Station
                    </div>

                    <div
                        class="value"
                        style="
                            font-size:0.95rem;
                        "
                    >
                        ${escapeAssessment(
                            supporting.nearest_rainfall_station ||
                            "—"
                        )}
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        River Station
                    </div>

                    <div
                        class="value"
                        style="
                            font-size:0.95rem;
                        "
                    >
                        ${escapeAssessment(
                            supporting.nearest_river_station ||
                            "—"
                        )}
                    </div>

                </div>

            </div>


            <div
                class="note"
                style="
                    margin-top:1rem;
                "
            >

                GIS context is supporting spatial
                evidence. Slope is displayed only
                where DEM coverage is available.

            </div>

        </div>


        <!-- MODEL EXPLANATION -->

        <div
            class="glass section-block"
        >

            <h3>
                How the Risk Score Is Built
            </h3>


            <div
                style="
                    display:grid;
                    grid-template-columns:
                        repeat(3,minmax(0,1fr));
                    gap:1rem;
                    margin-top:1rem;
                "
            >

                <div class="mini-card">

                    <div class="label">
                        HAZARD
                    </div>

                    <div
                        class="value"
                        style="
                            font-size:1.2rem;
                        "
                    >
                        50%
                    </div>

                    <div class="sub">
                        Landslide + rainfall
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        EXPOSURE
                    </div>

                    <div
                        class="value"
                        style="
                            font-size:1.2rem;
                        "
                    >
                        20%
                    </div>

                    <div class="sub">
                        Population exposure
                    </div>

                </div>


                <div class="mini-card">

                    <div class="label">
                        VULNERABILITY
                    </div>

                    <div
                        class="value"
                        style="
                            font-size:1.2rem;
                        "
                    >
                        30%
                    </div>

                    <div class="sub">
                        Demographic vulnerability
                    </div>

                </div>

            </div>


            <div
                class="note"
                style="
                    margin-top:1rem;
                "
            >

                These are transparent MVP weights
                defined for the prototype, not
                official government weights.

            </div>

        </div>


        <!-- ACTIONS -->

        <div
            class="glass section-block"
        >

            <div
                style="
                    display:flex;
                    gap:0.8rem;
                    flex-wrap:wrap;
                "
            >

                <button
                    id="changeAssessmentVillage"
                    type="button"
                    class="btn-secondary"
                    style="
                        padding:0.75rem 1.1rem;
                        border-radius:10px;
                        cursor:pointer;
                    "
                >
                    Change Village
                </button>


                <button
                    id="openRelocationAssessment"
                    type="button"
                    class="btn-primary"
                    style="
                        padding:0.75rem 1.1rem;
                        border-radius:10px;
                        cursor:pointer;
                    "
                >
                    View Relocation Options →
                </button>

            </div>


            <div
                class="note caution"
                style="
                    margin-top:1rem;
                "
            >

                <strong>
                    Decision-support note:
                </strong>

                A high-risk score identifies a
                priority area for authority review.
                It does not legally declare a village
                uninhabitable or automatically order
                relocation.

            </div>

        </div>

    `;
}


/* ============================================================
   HELPERS
   ============================================================ */

function formatAssessmentNumber(
    value,
    decimals = 1
) {

    if (
        value === null ||
        value === undefined ||
        value === "" ||
        !Number.isFinite(
            Number(value)
        )
    ) {

        return "—";

    }


    const number =
        Number(value);


    if (
        decimals === 0
    ) {

        return number.toLocaleString(
            "en-IN",
            {
                maximumFractionDigits: 0
            }
        );

    }


    return number.toLocaleString(
        "en-IN",
        {
            minimumFractionDigits: 1,
            maximumFractionDigits: decimals
        }
    );

}


function formatAssessmentPercent(
    value
) {

    if (
        value === null ||
        value === undefined ||
        value === "" ||
        !Number.isFinite(
            Number(value)
        )
    ) {

        return "—";

    }


    return (
        formatAssessmentNumber(
            value
        ) +
        "%"
    );

}


function escapeAssessment(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


function assessmentRiskClass(
    category
) {

    const value =
        String(
            category || ""
        ).toLowerCase();


    if (
        value.includes(
            "very high"
        )
    ) {

        return "risk-very-high";

    }


    if (
        value.includes("high")
    ) {

        return "risk-high";

    }


    if (
        value.includes("moderate")
    ) {

        return "risk-moderate";

    }


    if (
        value.includes("low")
    ) {

        return "risk-low";

    }


    return "risk-insufficient";

}


function riskPillAssessment(
    category
) {

    const value =
        String(
            category || ""
        ).toLowerCase();


    if (
        value.includes(
            "very high"
        )
    ) {

        return "risk-pill very-high";

    }


    if (
        value.includes("high")
    ) {

        return "risk-pill high";

    }


    if (
        value.includes("moderate")
    ) {

        return "risk-pill moderate";

    }


    if (
        value.includes("low")
    ) {

        return "risk-pill low";

    }


    return "risk-pill";

}


/* ============================================================
   PAGE LOAD
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    loadAssessment
);