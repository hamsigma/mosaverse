/**
 * MosaVerse Design Detail Page
 */

const detailLoading = document.getElementById("detailLoading");
const detailContent = document.getElementById("detailContent");
const errorState = document.getElementById("errorState");

/**
 * Load design detail
 */
async function loadDesignDetail() {
  const designId = getUrlParam("id");

  if (!designId) {
    showError();
    return;
  }

  try {
    const design = await API.getDesign(designId);

    // Populate the page
    document.getElementById("designTitle").textContent = design.title;
    document.getElementById("breadcrumbTitle").textContent = design.title;
    document.title = `MosaVerse — ${design.title}`;

    // Image
    const imageUrl =
      design.image_url ||
      design.image ||
      "https://via.placeholder.com/600x800?text=No+Image";
    const imgEl = document.getElementById("designImage");
    imgEl.src = imageUrl;
    imgEl.alt = design.title;

    // Category
    const categoryEl = document.getElementById("designCategory");
    if (design.category) {
      categoryEl.textContent = design.category.name;
    } else {
      categoryEl.classList.add("hidden");
    }

    // Description
    const descEl = document.getElementById("designDescription");
    descEl.textContent =
      design.description || "Belum ada deskripsi untuk desain ini.";

    // Dates
    document.getElementById("designCreated").textContent = formatDate(
      design.created_at,
    );
    document.getElementById("designUpdated").textContent = formatDate(
      design.updated_at,
    );

    // Show content
    detailLoading.classList.add("hidden");
    detailContent.classList.remove("hidden");
    detailContent.classList.add("fade-in");
  } catch (error) {
    console.error("Error loading design:", error);
    showError();
  }
}

/**
 * Show error state
 */
function showError() {
  detailLoading.classList.add("hidden");
  errorState.classList.remove("hidden");
  errorState.classList.add("fade-in");
}

// Initialize
document.addEventListener("DOMContentLoaded", loadDesignDetail);
