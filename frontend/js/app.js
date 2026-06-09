/**
 * MosaVerse Gallery Page - Main Application Logic
 */

// State
let currentPage = 1;
let currentCategory = "all";
let isSearching = false;

// DOM Elements
const galleryGrid = document.getElementById("galleryGrid");
const galleryLoading = document.getElementById("galleryLoading");
const emptyState = document.getElementById("emptyState");
const pagination = document.getElementById("pagination");
const categoryFilter = document.getElementById("categoryFilter");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const searchLoading = document.getElementById("searchLoading");
const searchInfo = document.getElementById("searchInfo");
const searchCount = document.getElementById("searchCount");
const searchQuery = document.getElementById("searchQuery");
const clearSearch = document.getElementById("clearSearch");

/**
 * Render a single design card
 */
function renderCard(design) {
  const imageUrl =
    design.image_url || "https://via.placeholder.com/400x400?text=No+Image";
  const categoryName = design.category_name || "Uncategorized";

  return `
        <a href="detail.html?id=${design.id}" class="block bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
            <div class="aspect-square overflow-hidden bg-gray-900">
                <img src="${imageUrl}" alt="${design.title}" class="w-full h-full object-cover">
            </div>
            <div class="p-4">
                <h3 class="font-epilogue text-sm font-bold text-black truncate">${design.title}</h3>
                <p class="text-xs text-gray-500 mt-1">${categoryName}</p>
                <button class="mt-3 w-full py-2 bg-black text-white text-xs font-semibold rounded-lg hover:bg-gray-800 transition-colors">
                    View Detail
                </button>
            </div>
        </a>
    `;
}

/**
 * Render the gallery grid
 */
function renderGallery(designs) {
  if (designs.length === 0) {
    galleryGrid.classList.add("hidden");
    galleryLoading.classList.add("hidden");
    emptyState.classList.remove("hidden");
    pagination.classList.add("hidden");
    return;
  }

  galleryGrid.innerHTML = designs.map(renderCard).join("");
  galleryLoading.classList.add("hidden");
  emptyState.classList.add("hidden");
  galleryGrid.classList.remove("hidden");
}

/**
 * Render pagination
 */
function renderPagination(totalPages, current) {
  if (totalPages <= 1) {
    pagination.classList.add("hidden");
    return;
  }

  let html = "";

  // Previous button
  html += `<button class="page-btn" ${current === 1 ? "disabled" : ""} onclick="goToPage(${current - 1})">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
    </button>`;

  // Page numbers
  const start = Math.max(1, current - 2);
  const end = Math.min(totalPages, current + 2);

  if (start > 1) {
    html += `<button class="page-btn" onclick="goToPage(1)">1</button>`;
    if (start > 2) html += `<span class="text-primary/40 px-1">...</span>`;
  }

  for (let i = start; i <= end; i++) {
    html += `<button class="page-btn ${i === current ? "active" : ""}" onclick="goToPage(${i})">${i}</button>`;
  }

  if (end < totalPages) {
    if (end < totalPages - 1)
      html += `<span class="text-primary/40 px-1">...</span>`;
    html += `<button class="page-btn" onclick="goToPage(${totalPages})">${totalPages}</button>`;
  }

  // Next button
  html += `<button class="page-btn" ${current === totalPages ? "disabled" : ""} onclick="goToPage(${current + 1})">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
    </button>`;

  pagination.innerHTML = html;
  pagination.classList.remove("hidden");
}

/**
 * Navigate to a specific page
 */
function goToPage(page) {
  currentPage = page;
  loadDesigns();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * Load designs from API
 */
async function loadDesigns() {
  if (isSearching) return; // Don't load regular designs during search

  galleryLoading.classList.remove("hidden");
  galleryGrid.classList.add("hidden");
  emptyState.classList.add("hidden");

  try {
    const data = await API.getDesigns(currentPage);
    renderGallery(data.results || []);
    renderPagination(Math.ceil((data.count || 0) / 12), currentPage);
  } catch (error) {
    console.error("Error loading designs:", error);
    galleryLoading.classList.add("hidden");
    emptyState.classList.remove("hidden");
  }
}

/**
 * Load categories from API
 */
async function loadCategories() {
  try {
    const data = await API.getCategories();
    const categories = data.results || data || [];

    // Keep the "All" button and add category buttons
    const allBtn = categoryFilter.querySelector('[data-category="all"]');
    categoryFilter.innerHTML = "";
    categoryFilter.appendChild(allBtn);

    categories.forEach((cat) => {
      const btn = document.createElement("button");
      btn.className =
        "category-btn px-4 py-1.5 text-xs font-bold uppercase tracking-wider rounded-full transition-all";
      btn.dataset.category = cat.id;
      btn.textContent = cat.name;
      btn.addEventListener("click", () => filterByCategory(cat.id, cat.name));
      categoryFilter.appendChild(btn);
    });
  } catch (error) {
    console.error("Error loading categories:", error);
  }
}

/**
 * Filter gallery by category
 */
function filterByCategory(categoryId, categoryName) {
  currentCategory = categoryId;
  currentPage = 1;

  // Update active state
  categoryFilter.querySelectorAll(".category-btn").forEach((btn) => {
    if (btn.dataset.category == categoryId) {
      btn.classList.add("active");
      btn.classList.remove("bg-primary", "text-accent");
      btn.classList.add("bg-primary", "text-accent");
    } else {
      btn.classList.remove("active");
    }
  });

  // Update "All" button
  const allBtn = categoryFilter.querySelector('[data-category="all"]');
  if (categoryId === "all") {
    allBtn.classList.add("active");
  } else {
    allBtn.classList.remove("active");
  }

  // Reload with filter (using search param for category name)
  loadDesignsWithCategory(categoryId);
}

/**
 * Load designs filtered by category
 */
async function loadDesignsWithCategory(categoryId) {
  galleryLoading.classList.remove("hidden");
  galleryGrid.classList.add("hidden");

  try {
    const params = { page: currentPage };
    if (categoryId !== "all") {
      // Use the category name for filtering via search
      const catBtn = categoryFilter.querySelector(
        `[data-category="${categoryId}"]`,
      );
      if (catBtn) params.search = catBtn.textContent;
    }

    const data = await API.getDesigns(currentPage, params.search || "");
    renderGallery(data.results || []);
    renderPagination(Math.ceil((data.count || 0) / 12), currentPage);
  } catch (error) {
    console.error("Error loading designs:", error);
  }
}

/**
 * AI Smart Search
 */
async function performSearch(query) {
  if (!query.trim()) return;

  isSearching = true;
  searchLoading.classList.remove("hidden");
  searchInfo.classList.add("hidden");
  galleryLoading.classList.remove("hidden");
  galleryGrid.classList.add("hidden");
  emptyState.classList.add("hidden");
  pagination.classList.add("hidden");
  searchBtn.disabled = true;

  try {
    const data = await API.aiSearch(query.trim());
    const results = data.results || [];

    searchLoading.classList.add("hidden");
    searchCount.textContent = data.count || results.length;
    searchQuery.textContent = query.trim();
    searchInfo.classList.remove("hidden");

    renderGallery(results);
  } catch (error) {
    console.error("Error performing AI search:", error);
    searchLoading.classList.add("hidden");
    galleryLoading.classList.add("hidden");
    emptyState.classList.remove("hidden");
  } finally {
    isSearching = false;
    searchBtn.disabled = false;
  }
}

/**
 * Clear search results
 */
function clearSearchResults() {
  isSearching = false;
  searchInput.value = "";
  searchInfo.classList.add("hidden");
  searchLoading.classList.add("hidden");
  loadDesigns();
}

// Event Listeners
searchBtn.addEventListener("click", () => {
  performSearch(searchInput.value);
});

searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    performSearch(searchInput.value);
  }
});

clearSearch.addEventListener("click", clearSearchResults);

// Category filter "All" button
document
  .querySelector('[data-category="all"]')
  .addEventListener("click", () => {
    currentCategory = "all";
    currentPage = 1;
    categoryFilter
      .querySelectorAll(".category-btn")
      .forEach((btn) => btn.classList.remove("active"));
    document.querySelector('[data-category="all"]').classList.add("active");
    loadDesigns();
  });

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  loadDesigns();
  loadCategories();
});
