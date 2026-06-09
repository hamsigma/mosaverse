/**
 * MosaVerse API Configuration & Helper Functions
 */

const API_BASE = "http://127.0.0.1:8000/api";

const API = {
  /**
   * GET request
   */
  async get(endpoint, params = {}) {
    const url = new URL(`${API_BASE}${endpoint}`);
    Object.entries(params).forEach(([key, val]) => {
      if (val !== null && val !== undefined && val !== "") {
        url.searchParams.append(key, val);
      }
    });

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * POST request
   */
  async post(endpoint, data = {}, useCSRF = true) {
    const headers = {
      "Content-Type": "application/json",
    };

    if (useCSRF) {
      const csrfToken = getCookie("csrftoken");
      if (csrfToken) {
        headers["X-CSRFToken"] = csrfToken;
      }
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers,
      credentials: "include",
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get all designs (paginated)
   */
  async getDesigns(page = 1, search = "", category = "") {
    const params = { page };
    if (search) params.search = search;
    if (category) params.category = category;
    return this.get("/designs/", params);
  },

  /**
   * Get single design detail
   */
  async getDesign(id) {
    return this.get(`/designs/${id}/`);
  },

  /**
   * Get all categories
   */
  async getCategories() {
    return this.get("/categories/");
  },

  /**
   * AI Smart Search
   */
  async aiSearch(query) {
    return this.post("/ai/search/", { query });
  },
};

/**
 * Get cookie value by name
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Format date to Indonesian locale
 */
function formatDate(dateString) {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleDateString("id-ID", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

/**
 * Get URL parameter by name
 */
function getUrlParam(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}
