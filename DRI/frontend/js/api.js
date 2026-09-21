/**
 * api.js — the only file that knows the backend's base URL.
 * Every page fetches data through this client instead of hardcoding values.
 */
const DRI_API_BASE = window.DRI_API_BASE || "http://127.0.0.1:8000";

const DriAPI = {
  async _get(path) {
    const res = await fetch(`${DRI_API_BASE}${path}`);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed (${res.status})`);
    }
    return res.json();
  },

  coverage() {
    return this._get("/api/coverage");
  },
  districts() {
    return this._get("/api/districts");
  },
  villages({ district, q } = {}) {
    const params = new URLSearchParams();
    if (district) params.set("district", district);
    if (q) params.set("q", q);
    const qs = params.toString();
    return this._get(`/api/villages${qs ? `?${qs}` : ""}`);
  },
  villagesGeojson({ district } = {}) {
    const params = new URLSearchParams();
    if (district) params.set("district", district);
    const qs = params.toString();
    return this._get(`/api/villages/geojson${qs ? `?${qs}` : ""}`);
  },
  village(id) {
    return this._get(`/api/villages/${encodeURIComponent(id)}`);
  },
  risk(id) {
    return this._get(`/api/risk/${encodeURIComponent(id)}`);
  },
  relocation(id) {
    return this._get(`/api/relocation/${encodeURIComponent(id)}`);
  },
  healthFacilities({ district } = {}) {
    const params = new URLSearchParams();
    if (district) params.set("district", district);
    const qs = params.toString();
    return this._get(`/api/health-facilities${qs ? `?${qs}` : ""}`);
  },
};

/** Shared risk-category -> color mapping, kept in one place so the map
 * legend and pills never drift apart. */
const RISK_COLORS = {
  "Low": "#6e8f63",
  "Moderate": "#d9a441",
  "High": "#c77b3d",
  "Very High": "#a83232",
  "Insufficient Data": "#9b9788",
};

function riskColor(category) {
  return RISK_COLORS[category] || RISK_COLORS["Insufficient Data"];
}

function riskPillClass(category) {
  const key = (category || "Insufficient Data").replace(/\s+/g, "-");
  return `risk-pill risk-${key}`;
}

function fmt(value, suffix = "") {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  if (typeof value === "number") {
    return `${Number.isInteger(value) ? value.toLocaleString("en-IN") : value.toFixed(1)}${suffix}`;
  }
  return `${value}${suffix}`;
}
