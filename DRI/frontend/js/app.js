/**
 * DRI — Shared frontend behaviour
 * Header navigation, search, village detail panel.
 */

/* =========================================================
   HELPERS
========================================================= */

function driEscapeHtml(value) {
  if (value === null || value === undefined) return "—";

  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function driNumber(value, decimals = 1) {
  const n = Number(value);

  if (!Number.isFinite(n)) return "—";

  return n.toFixed(decimals);
}

function driValue(obj, key, fallback = "—") {
  if (!obj) return fallback;

  const value = obj[key];

  if (value === null || value === undefined || value === "") {
    return fallback;
  }

  return value;
}

function riskPillClass(category) {
  const value = String(category || "").toLowerCase();

  if (value.includes("very high")) return "risk-very-high";
  if (value.includes("high")) return "risk-high";
  if (value.includes("moderate")) return "risk-moderate";
  if (value.includes("low")) return "risk-low";

  return "risk-unknown";
}


/* =========================================================
   HEADER NAVIGATION
========================================================= */

function initHeaderNav() {
  const path =
    window.location.pathname.split("/").pop() || "dashboard.html";

  document
    .querySelectorAll(".header-nav a, .nav-list a")
    .forEach((a) => {
      const href = a.getAttribute("href");

      if (href === path) {
        a.classList.add("active");
      }
    });
}


/* =========================================================
   OPEN VILLAGE
========================================================= */

function goToVillage(villageId) {
  if (!villageId) return;

  const url = new URL("dashboard.html", window.location.href);

  url.searchParams.set("village", villageId);

  window.location.href = url.toString();
}


/* =========================================================
   VILLAGE DETAIL PANEL
========================================================= */

function renderVillageDetail(village) {
  const panel =
    document.getElementById("villageDetail") ||
    document.getElementById("villageDetails") ||
    document.querySelector(".village-detail");

  if (!panel) {
    console.warn("Village detail panel not found.");
    return;
  }

  if (!village) {
    panel.innerHTML = `
      <div class="empty-state">
        <p>Select a village to view its details.</p>
      </div>
    `;
    return;
  }

  const villageName = driValue(
    village,
    "village_name",
    driValue(village, "name", "Unknown Village")
  );

  const district = driValue(village, "district");

  const population = driValue(
    village,
    "population",
    driValue(village, "census_population_2011")
  );

  const riskScore = driValue(
    village,
    "risk_score",
    driValue(village, "risk")
  );

  const riskCategory = driValue(
    village,
    "risk_category",
    "Insufficient Data"
  );

  const priority = driValue(
    village,
    "priority",
    "Insufficient Data"
  );

  const hazardScore = driValue(
    village,
    "hazard_score"
  );

  const exposureScore = driValue(
    village,
    "exposure_score"
  );

  const vulnerabilityScore = driValue(
    village,
    "vulnerability_score"
  );

  const rainfallHazard = driValue(
    village,
    "rainfall_hazard"
  );

  const landslideHazard = driValue(
    village,
    "landslide_hazard"
  );

  const riverSignal = driValue(
    village,
    "river_signal"
  );

  const landslideCount = driValue(
    village,
    "landslide_count"
  );

  const slope = driValue(
    village,
    "mean_slope_deg"
  );

  const roadDistance = driValue(
    village,
    "road_distance_km"
  );

  const nearestRainfallStation = driValue(
    village,
    "nearest_rainfall_station"
  );

  const nearestRiverStation = driValue(
    village,
    "nearest_river_station"
  );

  panel.innerHTML = `
    <div class="village-detail-inner">

      <div class="detail-header">
        <div>
          <div class="detail-eyebrow">
            SELECTED VILLAGE
          </div>

          <h2>
            ${driEscapeHtml(villageName)}
          </h2>

          <p class="detail-district">
            ${driEscapeHtml(district)}
          </p>
        </div>

        <div class="${riskPillClass(riskCategory)}">
          ${driEscapeHtml(riskCategory)}
        </div>
      </div>


      <div class="detail-risk-main">

        <div class="risk-score-block">
          <span class="detail-label">
            OVERALL RISK
          </span>

          <strong>
            ${
              riskScore === "—"
                ? "—"
                : driNumber(riskScore, 1)
            }
          </strong>
        </div>

        <div class="priority-block">
          <span class="detail-label">
            RELOCATION PRIORITY
          </span>

          <strong>
            ${driEscapeHtml(priority)}
          </strong>
        </div>

      </div>


      <div class="detail-section">

        <h3>Population & Risk</h3>

        <div class="detail-grid">

          <div class="detail-item">
            <span>Population</span>
            <strong>
              ${
                population === "—"
                  ? "—"
                  : Number(population).toLocaleString("en-IN")
              }
            </strong>
          </div>

          <div class="detail-item">
            <span>Hazard Score</span>
            <strong>
              ${driNumber(hazardScore)}
            </strong>
          </div>

          <div class="detail-item">
            <span>Exposure Score</span>
            <strong>
              ${driNumber(exposureScore)}
            </strong>
          </div>

          <div class="detail-item">
            <span>Vulnerability</span>
            <strong>
              ${driNumber(vulnerabilityScore)}
            </strong>
          </div>

        </div>

      </div>


      <div class="detail-section">

        <h3>Hazard Components</h3>

        <div class="detail-grid">

          <div class="detail-item">
            <span>Rainfall Hazard</span>
            <strong>
              ${driNumber(rainfallHazard)}
            </strong>
          </div>

          <div class="detail-item">
            <span>Landslide Hazard</span>
            <strong>
              ${driNumber(landslideHazard)}
            </strong>
          </div>

          <div class="detail-item">
            <span>River Signal</span>
            <strong>
              ${driNumber(riverSignal)}
            </strong>
          </div>

          <div class="detail-item">
            <span>Nearby Landslides</span>
            <strong>
              ${driNumber(landslideCount, 0)}
            </strong>
          </div>

        </div>

      </div>


      <div class="detail-section">

        <h3>GIS Context</h3>

        <div class="detail-grid">

          <div class="detail-item">
            <span>Mean Slope</span>
            <strong>
              ${
                slope === "—"
                  ? "—"
                  : `${driNumber(slope)}°`
              }
            </strong>
          </div>

          <div class="detail-item">
            <span>Road Distance</span>
            <strong>
              ${
                roadDistance === "—"
                  ? "—"
                  : `${driNumber(roadDistance)} km`
              }
            </strong>
          </div>

          <div class="detail-item">
            <span>Rainfall Station</span>
            <strong>
              ${driEscapeHtml(nearestRainfallStation)}
            </strong>
          </div>

          <div class="detail-item">
            <span>River Station</span>
            <strong>
              ${driEscapeHtml(nearestRiverStation)}
            </strong>
          </div>

        </div>

      </div>


      <div class="detail-actions">

        <button
          type="button"
          class="primary-button"
          onclick="goToVillageAssessment('${driEscapeHtml(
            village.village_id
          )}')"
        >
          View Full Risk Assessment →
        </button>

      </div>


      <p class="detail-note">
        Risk scores are decision-support outputs.
        Red-Zone Candidates require authority review and
        are not legal declarations of uninhabitable land.
      </p>

    </div>
  `;
}


/* =========================================================
   GO TO FULL ASSESSMENT
========================================================= */

function goToVillageAssessment(villageId) {
  if (!villageId) return;

  const url = new URL(
    "assessment.html",
    window.location.href
  );

  url.searchParams.set("village", villageId);

  window.location.href = url.toString();
}


/* =========================================================
   HEADER SEARCH
========================================================= */

function initHeaderSearch() {
  const input =
    document.getElementById("headerSearch");

  const resultsBox =
    document.getElementById("headerSearchResults");

  if (!input || !resultsBox) return;

  let debounceTimer = null;

  input.addEventListener("input", () => {

    const q = input.value.trim();

    clearTimeout(debounceTimer);

    if (q.length < 2) {
      resultsBox.classList.remove("open");
      resultsBox.innerHTML = "";
      return;
    }

    debounceTimer = setTimeout(async () => {

      try {

        const response =
          await DriAPI.villages({ q });

        const villages =
          response.villages || [];

        renderResults(
          villages.slice(0, 8)
        );

      } catch (err) {

        console.error(
          "Village search failed:",
          err
        );

        resultsBox.innerHTML = `
          <div
            style="
              padding:0.7em 1em;
              font-size:0.85rem;
              color:var(--ink-soft);
            "
          >
            Couldn't reach the API —
            is the backend running?
          </div>
        `;

        resultsBox.classList.add("open");
      }

    }, 220);
  });


  document.addEventListener("click", (e) => {

    if (
      !resultsBox.contains(e.target) &&
      e.target !== input
    ) {
      resultsBox.classList.remove("open");
    }

  });


  function renderResults(villages) {

    if (!villages.length) {

      resultsBox.innerHTML = `
        <div
          style="
            padding:0.7em 1em;
            font-size:0.85rem;
            color:var(--ink-soft);
          "
        >
          No villages match that search.
        </div>
      `;

      resultsBox.classList.add("open");

      return;
    }


    resultsBox.innerHTML = villages
      .map(
        (v) => `
          <button
            type="button"
            data-id="${driEscapeHtml(v.village_id)}"
          >

            <span>
              ${driEscapeHtml(v.village_name)}

              <br>

              <span class="muted">
                ${driEscapeHtml(v.district)}
              </span>
            </span>

            <span
              class="${riskPillClass(
                v.risk_category
              )}"
            >
              ${driEscapeHtml(
                v.risk_category ||
                "Insufficient Data"
              )}
            </span>

          </button>
        `
      )
      .join("");


    resultsBox.classList.add("open");


    resultsBox
      .querySelectorAll("button")
      .forEach((btn) => {

        btn.addEventListener(
          "click",
          () => {
            goToVillage(
              btn.dataset.id
            );
          }
        );

      });
  }
}


/* =========================================================
   START
========================================================= */

document.addEventListener(
  "DOMContentLoaded",
  () => {

    initHeaderNav();
    initHeaderSearch();

  }
);