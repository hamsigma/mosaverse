/**
 * MosaVerse API Client
 *
 * Centralized HTTP client for all API communication.
 * All endpoints go through this module for consistent error handling,
 * credential management, and CSRF token injection.
 */

const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000/api"
  : "/api";

// ─── Utilities ─────────────────────────────────────────

function formatDate(dateString) {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleDateString("id-ID", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function getUrlParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

// ─── HTTP Helpers ──────────────────────────────────────

function _buildHeaders({ json = true } = {}) {
  const headers = {};
  if (json) headers["Content-Type"] = "application/json";
  // Note: CSRF is handled server-side via SessionAuthentication bypass.
  // CSRF_COOKIE_HTTPONLY=True prevents JS access; not needed here.
  return headers;
}

async function _request(method, endpoint, { body, params, json = true } = {}) {
  const url = new URL(`${API_BASE}${endpoint}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, val]) => {
      if (val !== null && val !== undefined && val !== "") {
        url.searchParams.append(key, val);
      }
    });
  }

  const options = {
    method,
    headers: _buildHeaders({ json }),
    credentials: "include",
  };

  if (body !== undefined) {
    options.body = json ? JSON.stringify(body) : body;
    if (!json) {
      // Let browser set Content-Type for FormData
      delete options.headers["Content-Type"];
    }
  }

  const response = await fetch(url.toString(), options);

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(JSON.stringify(errData) || `HTTP ${response.status}`);
  }

  // 204 No Content
  if (response.status === 204) return null;
  return response.json();
}

// ─── API Object ────────────────────────────────────────

const API = {
  get(endpoint, params) {
    return _request("GET", endpoint, { params });
  },

  post(endpoint, body) {
    return _request("POST", endpoint, { body });
  },

  put(endpoint, body) {
    return _request("PUT", endpoint, { body });
  },

  delete(endpoint) {
    return _request("DELETE", endpoint);
  },

  /** Multipart upload (FormData) — POST */
  upload(endpoint, formData) {
    return _request("POST", endpoint, { body: formData, json: false });
  },

  /** Multipart upload (FormData) — PUT */
  uploadPut(endpoint, formData) {
    return _request("PUT", endpoint, { body: formData, json: false });
  },

  // ─── Domain Methods ──────────────────────────────────

  getDesigns(page = 1, search = "", category = "") {
    const params = { page };
    if (search) params.search = search;
    if (category) params.category = category;
    return this.get("/designs/", params);
  },

  getDesign(id) {
    return this.get(`/designs/${id}/`);
  },

  getCategories() {
    return this.get("/categories/");
  },

  aiSearch(query) {
    return this.post("/ai/search/", { query });
  },
};
