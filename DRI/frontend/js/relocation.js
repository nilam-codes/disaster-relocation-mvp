/**
 * relocation.js — powers relocation.html
 *
 * Works in two ways:
 * 1. If a village ID is present in the URL:
 *      relocation.html?village=044922
 *
 * 2. If no village ID is present:
 *      Loads the real village list and provides a selector.
 */

async function loadRelocation() {
  const root = document.getElementById("relocationRoot");

  if (!root) {
    console.error("DRI: relocationRoot not found.");
    return;
  }

  const params = new URLSearchParams(window.location.search);
  let villageId = params.get("village");

  /*
   * ---------------------------------------------------------
   * NO VILLAGE SELECTED
   * ---------------------------------------------------------
   *
   * Instead of showing a dead-end message, give the user a
   * real village selector populated from the backend.
   */
  if (!villageId) {
    await showVillageSelector(root);
    return;
  }

  await renderRelocationForVillage(
    root,
    villageId
  );
}


/**
 * Show a village selector when relocation.html is opened
 * directly or from the top navigation.
 */
async function showVillageSelector(root) {

  root.innerHTML = `
    <div class="glass section-block">
      <h3>Select source village</h3>

      <p style="color:var(--ink-soft); margin-top:0.3rem;">
        Select a vulnerable village to view its relocation
        recommendation.
      </p>

      <div style="max-width:520px; margin-top:1.2rem;">
        <label
          for="relocationVillageSelect"
          class="label"
          style="display:block; margin-bottom:0.45rem;"
        >
          Village
        </label>

        <select
          id="relocationVillageSelect"
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
          <option value="">Loading villages…</option>
        </select>

        <button
          id="loadRelocationVillage"
          type="button"
          class="btn-primary"
          style="
            margin-top:1rem;
            width:100%;
          "
        >
          View Relocation Options
        </button>
      </div>
    </div>
  `;


  const select =
    document.getElementById(
      "relocationVillageSelect"
    );

  const button =
    document.getElementById(
      "loadRelocationVillage"
    );


  try {

    const data =
      await DriAPI.villages();


    const villages =
      Array.isArray(data.villages)
        ? data.villages
        : [];


    /*
     * Put high-risk villages first.
     * This makes Sherpur / other priority villages easy
     * to find during the demo.
     */
    villages.sort(
      (a, b) => {

        const ar =
          Number.isFinite(
            Number(a.risk_score)
          )
            ? Number(a.risk_score)
            : -1;

        const br =
          Number.isFinite(
            Number(b.risk_score)
          )
            ? Number(b.risk_score)
            : -1;

        return br - ar;
      }
    );


    select.innerHTML = `
      <option value="">
        Choose a village…
      </option>
    `;


    villages.forEach(
      (village) => {

        const option =
          document.createElement(
            "option"
          );

        option.value =
          village.village_id;

        const risk =
          village.risk_score != null
            ? ` · Risk ${fmt(village.risk_score)}`
            : "";

        option.textContent =
          `${village.village_name} — ${village.district}${risk}`;

        select.appendChild(
          option
        );
      }
    );


    /*
     * IMPORTANT FOR YOUR DEMO:
     * Automatically select Sherpur if it exists.
     */
    const sherpur =
      villages.find(
        (v) =>
          String(
            v.village_name || ""
          ).toLowerCase() ===
          "sherpur"
      );


    if (sherpur) {

      select.value =
        sherpur.village_id;

    }


  } catch (err) {

    console.error(
      "DRI: village list loading failed:",
      err
    );

    select.innerHTML = `
      <option value="">
        Couldn't load villages
      </option>
    `;
  }


  button.addEventListener(
    "click",
    () => {

      const selected =
        select.value;

      if (!selected) {

        alert(
          "Please select a village first."
        );

        return;
      }


      /*
       * Update the URL so the page can be refreshed/shared
       * without losing the selected village.
       */
      const url =
        new URL(
          window.location.href
        );

      url.searchParams.set(
        "village",
        selected
      );

      window.history.replaceState(
        {},
        "",
        url
      );


      renderRelocationForVillage(
        root,
        selected
      );

    }
  );
}


/**
 * Load and render relocation information for one village.
 */
async function renderRelocationForVillage(
  root,
  villageId
) {

  root.innerHTML = `
    <div class="state-msg">
      <div class="spinner"></div>
      Loading relocation options…
    </div>
  `;


  try {

    const data =
      await DriAPI.relocation(
        villageId
      );


    /*
     * -------------------------------------------------------
     * SOURCE VILLAGE CARD
     * -------------------------------------------------------
     */

    const sourceCard = `
      <div class="glass section-block">

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

            <h3>
              Source village
            </h3>

            <div
              style="
                color:var(--ink-soft);
                margin-top:0.2rem;
              "
            >
              Vulnerable habitation identified
              for relocation planning
            </div>

          </div>


          <button
            id="changeRelocationVillage"
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


        <div class="card-grid">

          <div class="mini-card">

            <div class="label">
              Village
            </div>

            <div
              class="value"
              style="font-size:1.05rem;"
            >
              ${escapeHtml(
                data.source_village
              )}
            </div>

            <div class="sub">
              ${escapeHtml(
                data.source_district
              )}
            </div>

          </div>


          <div class="mini-card">

            <div class="label">
              Population
            </div>

            <div class="value">
              ${fmt(
                data.source_population
              )}
            </div>

          </div>


          <div class="mini-card">

            <div class="label">
              Current risk
            </div>

            <div class="value">
              ${fmt(
                data.source_risk_score
              )}
              <span
                style="
                  font-size:0.8rem;
                  color:var(--ink-soft);
                "
              >
                /100
              </span>
            </div>

          </div>


          <div class="mini-card">

            <div class="label">
              Priority
            </div>

            <div
              class="value"
              style="font-size:0.95rem;"
            >
              ${escapeHtml(
                data.source_priority ||
                "—"
              )}
            </div>

          </div>

        </div>

      </div>
    `;


    /*
     * -------------------------------------------------------
     * NO RECOMMENDATION
     * -------------------------------------------------------
     */

    if (
      !data.recommendations ||
      data.recommendations.length === 0
    ) {

      root.innerHTML = `
        ${sourceCard}

        <div
          class="glass section-block state-msg"
        >

          <p>
            No relocation recommendation has
            been generated for
            <strong>
              ${escapeHtml(
                data.source_village
              )}
            </strong>
            yet.
          </p>

          <p
            style="
              color:var(--ink-soft);
              margin-top:0.7rem;
            "
          >
            The relocation engine currently
            covers the high-priority villages
            for which a lower-risk planning
            candidate has been generated.
          </p>

        </div>
      `;


      attachChangeVillageButton(
        root
      );

      return;
    }


    /*
     * -------------------------------------------------------
     * RECOMMENDATION CARDS
     * -------------------------------------------------------
     */

    const cards =
      data.recommendations
        .map(
          (r) => {

            const destinationRisk =
              Number(
                r.dest_risk_score
              );


            const sourceRisk =
              Number(
                data.source_risk_score
              );


            const riskReduction =
              Number.isFinite(
                destinationRisk
              ) &&
              Number.isFinite(
                sourceRisk
              )
                ? sourceRisk -
                  destinationRisk
                : null;


            return `

              <div
                class="glass section-block"
              >

                <div
                  class="relocation-flow"
                >

                  <!-- SOURCE -->

                  <div>

                    <div
                      class="label"
                      style="
                        font-size:0.78rem;
                        text-transform:uppercase;
                        letter-spacing:0.05em;
                        color:var(--ink-soft);
                      "
                    >
                      From
                    </div>


                    <h4
                      style="
                        margin:0.2em 0;
                      "
                    >
                      ${escapeHtml(
                        data.source_village
                      )}
                    </h4>


                    <div
                      style="
                        font-size:0.85rem;
                        color:var(--ink-soft);
                      "
                    >
                      Pop.
                      ${fmt(
                        data.source_population
                      )}
                      · Risk
                      ${fmt(
                        data.source_risk_score
                      )}
                    </div>

                  </div>


                  <!-- ARROW -->

                  <div
                    class="relocation-arrow"
                  >

                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >

                      <path
                        d="M5 12h14M13 6l6 6-6 6"
                      />

                    </svg>

                  </div>


                  <!-- DESTINATION -->

                  <div
                    class="dest-card"
                  >

                    <div
                      class="label"
                      style="
                        font-size:0.78rem;
                        text-transform:uppercase;
                        letter-spacing:0.05em;
                        color:var(--ink-soft);
                      "
                    >
                      Recommended relocation site
                    </div>


                    <h4>
                      ${escapeHtml(
                        r.dest_village
                      )}

                      <span
                        style="
                          font-weight:400;
                          font-size:0.85rem;
                          color:var(--ink-soft);
                        "
                      >
                        —
                        ${escapeHtml(
                          r.dest_district
                        )}
                      </span>
                    </h4>


                    <span
                      class="${riskPillClass(
                        r.dest_risk_category
                      )}"
                    >
                      ${escapeHtml(
                        r.dest_risk_category ||
                        "Lower Risk Candidate"
                      )}
                      ·
                      ${fmt(
                        r.dest_risk_score
                      )}
                    </span>


                    ${
                      riskReduction !== null
                        ? `
                          <div
                            class="note"
                            style="
                              margin-top:0.8rem;
                            "
                          >
                            <strong>
                              Risk reduction:
                            </strong>
                            ${fmt(
                              riskReduction
                            )}
                            points
                          </div>
                        `
                        : ""
                    }


                    <div
                      class="card-grid"
                      style="
                        margin-top:1rem;
                      "
                    >

                      <div class="mini-card">

                        <div class="label">
                          Safety score
                        </div>

                        <div class="value">
                          ${fmt(
                            r.safety_score
                          )}
                        </div>

                      </div>


                      <div class="mini-card">

                        <div class="label">
                          Distance
                        </div>

                        <div class="value">
                          ${fmt(
                            r.distance_km,
                            " km"
                          )}
                        </div>

                      </div>


                      <div class="mini-card">

                        <div class="label">
                          Healthcare access
                        </div>

                        <div class="value">
                          ${fmt(
                            r.healthcare_score
                          )}
                        </div>

                        <div class="sub">
                          ${escapeHtml(
                            r.healthcare_access_note ||
                            ""
                          )}
                        </div>

                      </div>


                      <div class="mini-card">

                        <div class="label">
                          Suitability score
                        </div>

                        <div class="value">
                          ${fmt(
                            r.suitability_score
                          )}
                        </div>

                      </div>

                    </div>


                    ${bar(
                      r.suitability_score
                    )}


                    <div
                      class="note"
                      style="
                        margin-top:1rem;
                      "
                    >

                      <strong>
                        Estimated Additional Capacity
                        (Planning Proxy):
                      </strong>

                      ${fmt(
                        r.estimated_additional_capacity
                      )}
                      people.

                      ${
                        r.capacity_note
                          ? `
                            <br>
                            ${escapeHtml(
                              r.capacity_note
                            )}
                          `
                          : ""
                      }

                    </div>


                    <div
                      class="note caution"
                    >

                      <strong>
                        Planning note:
                      </strong>

                      Destination is a
                      lower-risk planning
                      candidate, not a legally
                      certified safe site.

                      Final relocation decisions
                      require State Disaster
                      Management Authority
                      review.

                    </div>

                  </div>

                </div>

              </div>

            `;
          }
        )
        .join("");


    root.innerHTML =
      sourceCard +
      cards;


    attachChangeVillageButton(
      root
    );


  } catch (err) {

    console.error(
      "DRI: relocation loading failed:",
      err
    );


    root.innerHTML = `

      <div
        class="state-msg error-msg"
      >

        <h3>
          Couldn't load relocation options.
        </h3>

        <p>
          ${escapeHtml(
            err.message ||
            "Unknown error"
          )}
        </p>

        <button
          id="retryRelocation"
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


    const retry =
      document.getElementById(
        "retryRelocation"
      );


    if (retry) {

      retry.addEventListener(
        "click",
        () =>
          renderRelocationForVillage(
            root,
            villageId
          )
      );

    }

  }
}


/**
 * Allow the user to change the source village.
 */
function attachChangeVillageButton(
  root
) {

  const button =
    document.getElementById(
      "changeRelocationVillage"
    );


  if (!button) {
    return;
  }


  button.addEventListener(
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


      showVillageSelector(
        root
      );

    }
  );
}


/**
 * Suitability progress bar.
 */
function bar(score) {

  const numeric =
    Number(score);


  const pct =
    Number.isFinite(numeric)
      ? Math.max(
          0,
          Math.min(
            100,
            numeric
          )
        )
      : 0;


  return `

    <div
      class="suitability-bar"
      aria-label="Suitability score ${pct}"
    >

      <div
        style="
          width:${pct}%;
        "
      ></div>

    </div>

  `;
}


/**
 * Simple HTML escaping so data from CSVs/API
 * cannot accidentally become HTML.
 */
function escapeHtml(
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


/**
 * Number formatter.
 *
 * Uses the existing project's fmt()
 * if available, otherwise provides a
 * safe fallback.
 */
function fmt(
  value,
  suffix = ""
) {

  if (
    value === null ||
    value === undefined ||
    value === "" ||
    Number.isNaN(
      Number(value)
    )
  ) {

    return "—";

  }


  const n =
    Number(value);


  if (
    Number.isInteger(n)
  ) {

    return (
      n.toLocaleString("en-IN") +
      suffix
    );

  }


  return (
    n.toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 1
      }
    ) +
    suffix
  );

}


/**
 * Risk pill fallback.
 *
 * Uses the project's existing
 * riskPillClass() when available.
 */
function riskPillClass(
  category
) {

  const c =
    String(
      category || ""
    ).toLowerCase();


  if (
    c.includes("very high")
  ) {

    return "risk-pill very-high";

  }


  if (
    c.includes("high")
  ) {

    return "risk-pill high";

  }


  if (
    c.includes("moderate")
  ) {

    return "risk-pill moderate";

  }


  if (
    c.includes("low")
  ) {

    return "risk-pill low";

  }


  return "risk-pill";

}


/**
 * Start page.
 */
document.addEventListener(
  "DOMContentLoaded",
  loadRelocation
);